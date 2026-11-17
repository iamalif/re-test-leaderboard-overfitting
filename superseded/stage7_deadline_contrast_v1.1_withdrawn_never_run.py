"""Stage 7: the deadline contrast (analysis plan addendum A, v1.1). Replaces v1.0, which was never run on data.

Equal-sized, consecutive windows of w submissions per team around the deadline:
    C, A, B = the three last windows before the deadline (B is the last w pre-deadline submissions)
    P       = the first w post-deadline submissions
Steps of the mean gap:  B-A (last step before the deadline),  P-B (step across it),  A-C (the step before).
    X = (P-B) - (B-A)          zero for any gap trajectory that is linear in submission index
    X_placebo = (B-A) - (A-C)  the same statistic one window earlier, no deadline involved
    Y = X - X_placebo          zero for any trajectory that is quadratic in submission index

    python scripts/stage7_deadline_contrast.py --selftest     # synthetic data only; safe before unsealing
    python scripts/stage7_deadline_contrast.py                # reads POST-DEADLINE scores: only after the addendum is archived
"""
import argparse, sys, numpy as np, pandas as pd
from scipy.stats import binomtest
sys.path.insert(0, "scripts")
from stage2_measures import RAW_SCORE_GROUPS

W_PRIMARY, MIN_TEAMS = 3, 20


def team_windows(pre, post, higher_better, w=W_PRIMARY):
    """One row per eligible team (at least 3w scored pre-deadline and w scored post-deadline submissions)."""
    s = 1.0 if higher_better else -1.0
    pre = pre.assign(gap=s * (pre.pub - pre.priv), lvl=s * pre.priv).sort_values(["TeamId", "day", "Id"])
    post = post.assign(gap=s * (post.pub - post.priv), lvl=s * post.priv).sort_values(["TeamId", "day", "Id"])
    n = pre.groupby("TeamId").Id.transform("size"); back = n - 1 - pre.groupby("TeamId").cumcount()     # 0 = last pre-deadline submission
    pre = pre.assign(win=(back // w))[(n >= 3 * w) & (back < 3 * w)]                                    # 0 = B, 1 = A, 2 = C
    g = pre.groupby(["TeamId", "win"])[["gap", "lvl"]].mean().unstack("win")
    post = post[post.groupby("TeamId").cumcount() < w]
    p = post.groupby("TeamId").agg(P=("gap", "mean"), P_lvl=("lvl", "mean"), k=("gap", "size")); p = p[p.k == w]
    t = pd.DataFrame({"B": g[("gap", 0)], "A": g[("gap", 1)], "C": g[("gap", 2)], "B_lvl": g[("lvl", 0)], "A_lvl": g[("lvl", 1)]}).join(p, how="inner")
    t["X"] = (t.P - t.B) - (t.B - t.A); t["X_placebo"] = (t.B - t.A) - (t.A - t.C); t["Y"] = t.X - t.X_placebo
    t["step_post"] = t.P - t.B; t["step_pre"] = t.B - t.A
    t["level_post"] = t.P_lvl - t.B_lvl; t["level_pre"] = t.B_lvl - t.A_lvl
    return t


def competition_row(t):
    out = dict(eligible_teams=len(t))
    for c in ("X", "X_placebo", "Y", "step_post", "step_pre", "level_post", "level_pre"): out[c] = t[c].mean()
    return out


def sign_summary(label, v, rng=None):
    v = pd.Series(v).dropna(); neg, pos, zero = int((v < 0).sum()), int((v > 0).sum()), int((v == 0).sum()); nz = neg + pos
    out = dict(quantity=label, competitions=len(v), negative=neg, positive=pos, zero=zero, share_negative_of_nonzero=neg / nz if nz else np.nan,
               sign_p=binomtest(neg, nz, .5).pvalue if nz else np.nan, median=v.median() if len(v) else np.nan)
    if rng is not None and len(v) >= 8:
        bs = [np.median(rng.choice(v.values, len(v))) for _ in range(10000)]; out.update(ci_lo=np.percentile(bs, 2.5), ci_hi=np.percentile(bs, 97.5))
    return out


# ------------------------------------------------------------------ synthetic suite
def _frames(traj_gap, traj_lvl, n_pre, n_post, teams=40, noise=0.0, rng=None):
    pre, post = [], []
    for t in range(teams):
        for k in range(n_pre + n_post):
            e1, e2 = (rng.normal(0, noise, 2) if noise else (0.0, 0.0))
            priv = traj_lvl(k) + e2; pub = priv + traj_gap(k) + e1
            (pre if k < n_pre else post).append((t, k, pub, priv))
    mk = lambda r: pd.DataFrame(r, columns=["TeamId", "Id", "pub", "priv"]).assign(day=pd.Timestamp("2020-01-01"))
    return mk(pre), mk(post)


def _adaptive(rng, post_mode, comps=60, n_pub=600, n_priv=1400, pre_steps=16, post_steps=8):
    rows = []
    for c in range(comps):
        pre, post = [], []
        for t in range(40):
            acc = rng.uniform(.6, .75); pub = rng.random(n_pub) < acc; priv = rng.random(n_priv) < acc
            for k in range(pre_steps + post_steps):
                is_post = k >= pre_steps; cp, cq = pub.copy(), priv.copy()
                for arr in (cp, cq):
                    kk = int(0.04 * len(arr)); i = rng.choice(len(arr), kk, replace=False); arr[i] = rng.random(kk) < acc + 0.02
                (post if is_post else pre).append((t, k, cp.mean(), cq.mean()))
                if post_mode == "noise": keep = rng.random() < 0.5
                elif is_post and post_mode == "private": keep = cq.mean() > priv.mean()
                elif is_post and post_mode == "fresh": keep = rng.random() < 0.5
                else: keep = cp.mean() > pub.mean()
                if keep: pub, priv = cp, cq
        mk = lambda r: pd.DataFrame(r, columns=["TeamId", "Id", "pub", "priv"]).assign(day=pd.Timestamp("2020-01-01"))
        rows.append(competition_row(team_windows(mk(pre), mk(post), True)))
    return pd.DataFrame(rows)


def selftest():
    rng = np.random.default_rng(11); out = []
    lvl = lambda k: 0.600 + 0.002 * k
    det = {  # deterministic, feedback-free trajectories (the first two are the pre-unsealing review's counterexamples)
        "linear gap, feedback-free": lambda k: 0.001 * k,
        "gap saturates exactly at the deadline, feedback-free": lambda k: 0.001 * min(k, 16),
        "concave (quadratic) gap, feedback-free": lambda k: 0.002 * k - 0.00004 * k * k,
        "gap saturates smoothly (exponential), feedback-free": lambda k: 0.02 * (1 - np.exp(-k / 8)),
    }
    for name, f in det.items():
        for n_post in (3, 8, 30):
            pre, post = _frames(f, lvl, 16, n_post)
            r = competition_row(team_windows(pre, post, True))
            out.append(dict(case=name, post_per_team=n_post, kind="deterministic", X_pp=100 * r["X"], X_placebo_pp=100 * r["X_placebo"], Y_pp=100 * r["Y"]))
    for name, mode in (("adaptive before; private score steers after", "private"), ("adaptive before; unsteered changes after", "fresh"),
                       ("adaptive before and after (public still steers)", "public"), ("no feedback use at all (noise)", "noise")):
        x = _adaptive(rng, mode)
        out.append(dict(case=name, post_per_team=8, kind="simulated, 60 competitions", X_pp=100 * x.X.mean(), X_placebo_pp=100 * x.X_placebo.mean(), Y_pp=100 * x.Y.mean(),
                        share_X_negative=(x.X < 0).mean(), share_Y_negative=(x.Y < 0).mean(), share_placebo_negative=(x.X_placebo < 0).mean()))
    o = pd.DataFrame(out); o.to_csv("outputs/stage7/selftest_suite.csv", index=False)
    pd.set_option("display.width", 220); print(o.round(4).to_string(index=False))


def main():
    import duckdb, os
    rng = np.random.default_rng(20261117)
    m = pd.read_csv("outputs/stage3/competition_measures.csv"); m = m[(m.excluded.fillna("") == "") & m.Cohort.isin(["O", "E"])].sort_values("CompetitionId")
    con = duckdb.connect(); con.execute("SET memory_limit='2GB'; SET temp_directory='/tmp/duck'")
    PQ = "outputs/stage7/post_deadline_submissions.parquet"
    if not os.path.exists(PQ):
        con.register("ids", pd.DataFrame({"CompetitionId": m.CompetitionId.astype(str)}))
        con.execute(f"""COPY (SELECT t.CompetitionId::BIGINT CompetitionId, s.Id::BIGINT Id, s.TeamId::BIGINT TeamId,
              strptime(s.SubmissionDate, '%m/%d/%Y')::DATE AS day,
              try_cast(s.PublicScoreFullPrecision AS DOUBLE) pub, try_cast(s.PrivateScoreFullPrecision AS DOUBLE) priv
            FROM read_csv('data/raw/Submissions.csv', header=true, all_varchar=true) s
            JOIN read_csv('data/raw/Teams.csv', header=true, all_varchar=true) t ON s.TeamId = t.Id
            WHERE t.CompetitionId IN (SELECT CompetitionId FROM ids) AND s.IsAfterDeadline='True' AND t.IsBenchmark='False'
              AND isfinite(try_cast(s.PublicScoreFullPrecision AS DOUBLE)) AND isfinite(try_cast(s.PrivateScoreFullPrecision AS DOUBLE))
            ORDER BY 1, 2) TO '{PQ}' (FORMAT parquet, ROW_GROUP_SIZE 100000)""")
    rows = []
    for r in m.itertuples():
        pre = con.sql(f"select * from 'outputs/stage3/analysis_submissions.parquet' where CompetitionId={r.CompetitionId}").df()
        post = con.sql(f"select * from '{PQ}' where CompetitionId={r.CompetitionId}").df()
        if len(post) == 0: continue
        for d in (pre, post): d["day"] = pd.to_datetime(d.day)
        raw = (pre, post)
        if r.Group not in RAW_SCORE_GROUPS:       # plan v1.0 clipping rule; bounds from PRE-deadline public scores, applied to both periods
            lo, hi = pre.pub.quantile([0.01, 0.99])
            pre = pre.assign(pub=pre.pub.clip(lo, hi), priv=pre.priv.clip(lo, hi)); post = post.assign(pub=post.pub.clip(lo, hi), priv=post.priv.clip(lo, hi))
        hb = bool(r.higher_better); t = team_windows(pre, post, hb)
        if len(t) < MIN_TEAMS: continue
        row = dict(CompetitionId=r.CompetitionId, Cohort=r.Cohort, Group=r.Group, Segment=r.Segment, CodeOnly=r.CodeOnly, flagged=r.flagged,
                   team_spread=r.team_spread, drift_mean=r.drift_mean, **competition_row(t))
        for w in (2, 5):
            tw = team_windows(pre, post, hb, w); row[f"X_w{w}"] = tw.X.mean() if len(tw) >= MIN_TEAMS else np.nan; row[f"Y_w{w}"] = tw.Y.mean() if len(tw) >= MIN_TEAMS else np.nan
        tu = team_windows(raw[0], raw[1], hb); row["X_unclipped"], row["Y_unclipped"] = tu.X.mean(), tu.Y.mean()
        dl = pd.Timestamp(r.Deadline); p30 = post[post.day <= dl + pd.Timedelta(days=30)]
        t30 = team_windows(pre, p30, hb); row["X_30d"] = t30.X.mean() if len(t30) >= MIN_TEAMS else np.nan; row["Y_30d"] = t30.Y.mean() if len(t30) >= MIN_TEAMS else np.nan
        rows.append(row)
    x = pd.DataFrame(rows)
    for c in ("X", "Y", "X_placebo"): x["rel_" + c] = x[c] / x.team_spread
    x.to_csv("outputs/stage7/deadline_per_competition.csv", index=False)
    res = [dict(role="PRIMARY (both must be significant and negative)", **sign_summary("X, O+E", x.X, rng)),
           dict(role="PRIMARY (both must be significant and negative)", **sign_summary("Y, O+E", x.Y, rng)),
           dict(role="effect size", **sign_summary("X in team spreads, O+E", x.rel_X, rng)),
           dict(role="effect size", **sign_summary("Y in team spreads, O+E", x.rel_Y, rng)),
           dict(role="placebo", **sign_summary("X one window earlier, O+E", x.X_placebo, rng))]
    for lab, sub in (("E", x[x.Cohort == "E"]), ("O", x[x.Cohort == "O"]), ("unflagged", x[~x.flagged]), ("not code-only", x[~x.CodeOnly]),
                     ("accuracy/AUC/MAP@K", x[x.Group.isin(RAW_SCORE_GROUPS)]), ("positive pre-deadline drift", x[x.drift_mean > 0])):
        res.append(dict(role="secondary", **sign_summary(f"X, {lab}", sub.X, rng))); res.append(dict(role="secondary", **sign_summary(f"Y, {lab}", sub.Y, rng)))
    for c in ("X_w2", "Y_w2", "X_w5", "Y_w5", "X_unclipped", "Y_unclipped", "X_30d", "Y_30d"): res.append(dict(role="sensitivity", **sign_summary(c, x[c], rng)))
    res.append(dict(role="context", **sign_summary("private-score change across the deadline (negative = worse)", x.level_post, rng)))
    res.append(dict(role="context", **sign_summary("private-score change in the last pre-deadline step", x.level_pre, rng)))
    res.append(dict(role="context", **sign_summary("gap step across the deadline (P-B)", x.step_post, rng)))
    res.append(dict(role="context", **sign_summary("gap step before the deadline (B-A)", x.step_pre, rng)))
    res = pd.DataFrame(res); res.to_csv("outputs/stage7/deadline_results.csv", index=False)
    pd.set_option("display.width", 240); print(len(x), "competitions"); print(res.round(4).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true"); a = ap.parse_args()
    selftest() if a.selftest else main()
