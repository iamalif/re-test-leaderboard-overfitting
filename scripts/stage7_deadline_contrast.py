"""Stage 7: the deadline contrast (analysis plan addendum A, v1.0).

Before a deadline a team sees only public scores; after it, late submissions are scored on the same public and
private sets [ASSUMPTION to verify: both scores are then shown to the team]. If the pre-deadline rise in the
public-over-private gap reflects dependence on public feedback, it should stop or reverse at the deadline. If it
reflects a model-dependent difference between the sets, it should continue as teams keep changing their models.

    python scripts/stage7_deadline_contrast.py --selftest     # synthetic data only; safe before unsealing
    python scripts/stage7_deadline_contrast.py                # reads POST-DEADLINE scores: only after the addendum is archived

Outputs: outputs/stage7/deadline_per_competition.csv, outputs/stage7/deadline_results.csv
"""
import argparse, sys, numpy as np, pandas as pd
from scipy.stats import binomtest
sys.path.insert(0, "scripts")
from stage2_measures import RAW_SCORE_GROUPS

MIN_PRE, MIN_POST, MIN_TEAMS = 8, 1, 20


def team_steps(pre, post, higher_better):
    """pre, post: DataFrames with TeamId, Id, day, pub, priv for one competition (already clipped if applicable).
    Returns one row per eligible team: gap means by pre-deadline quarter (q2,q3,q4) and post (p), and score levels."""
    s = 1.0 if higher_better else -1.0
    pre = pre.assign(gap=s * (pre.pub - pre.priv)).sort_values(["TeamId", "day", "Id"])
    post = post.assign(gap=s * (post.pub - post.priv))
    k = pre.groupby("TeamId").cumcount(); n = pre.groupby("TeamId").Id.transform("size")
    pre = pre.assign(q=(4 * k // n))[n >= MIN_PRE]
    g = pre.groupby(["TeamId", "q"]).agg(gap=("gap", "mean"), pub=("pub", "mean"), priv=("priv", "mean")).unstack("q")
    pm = post.groupby("TeamId").agg(p_gap=("gap", "mean"), p_pub=("pub", "mean"), p_priv=("priv", "mean"), n_post=("gap", "size"))
    pm = pm[pm.n_post >= MIN_POST]
    t = pd.DataFrame({"q2": g[("gap", 1)], "q3": g[("gap", 2)], "q4": g[("gap", 3)],
                      "q4_pub": s * g[("pub", 3)], "q4_priv": s * g[("priv", 3)], "q3_priv": s * g[("priv", 2)]}).join(pm, how="inner")
    t["J"] = t.p_gap - t.q4                    # step across the deadline
    t["Dq"] = t.q4 - t.q3                      # last step before the deadline
    t["Dq_prev"] = t.q3 - t.q2                 # the step before that (placebo)
    t["level_J"] = s * t.p_priv - t.q4_priv    # change in private score across the deadline, better = positive
    t["level_Dq"] = t.q4_priv - t.q3_priv
    t["post_public_not_worse"] = s * t.p_pub >= t.q4_pub
    return t


def competition_row(t):
    out = dict(eligible_teams=len(t))
    for c in ("J", "Dq", "Dq_prev", "level_J", "level_Dq"): out[c] = t[c].mean()
    out["X"] = out["J"] - out["Dq"]                       # primary: change of step at the deadline
    out["X_placebo"] = out["Dq"] - out["Dq_prev"]         # same statistic one quarter earlier
    r = t[t.post_public_not_worse]
    out["restricted_teams"] = len(r)
    out["X_restricted"] = (r.J.mean() - r.Dq.mean()) if len(r) >= MIN_TEAMS else np.nan
    return out


def sign_summary(label, v, rng):
    v = pd.Series(v).dropna(); neg, nz = int((v < 0).sum()), int((v != 0).sum())
    bs = [np.median(rng.choice(v.values, len(v))) for _ in range(10000)] if len(v) >= 8 else [np.nan]
    return dict(quantity=label, n=nz, negative=neg, share_negative=neg / nz if nz else np.nan,
                sign_p=binomtest(neg, nz, .5).pvalue if nz else np.nan, median=v.median() if len(v) else np.nan,
                ci_lo=np.nanpercentile(bs, 2.5), ci_hi=np.nanpercentile(bs, 97.5))


def selftest():
    rng = np.random.default_rng(7); res = []
    for mode in ("adaptive, then private visible", "composition trend, no feedback", "noise only"):
        Xs = []
        for c in range(120):
            n_pub, n_priv = 600, 1400; recs_pre, recs_post = [], []
            for t in range(40):
                acc = rng.uniform(.6, .75); pub = rng.random(n_pub) < acc; priv = rng.random(n_priv) < acc
                for sidx in range(24):
                    post = sidx >= 16
                    cp, cq = pub.copy(), priv.copy()
                    for arr in (cp, cq):
                        kk = int(0.04 * len(arr)); i = rng.choice(len(arr), kk, replace=False); arr[i] = rng.random(kk) < acc + 0.02   # same share of each set changes
                    a, b = cp.mean(), cq.mean()
                    if mode.startswith("composition"): a += 0.004 * sidx           # gap grows with the model, no feedback used
                    (recs_post if post else recs_pre).append((t, sidx, a, b))
                    if mode.startswith("adaptive"): keep = (cq.mean() > priv.mean()) if post else (cp.mean() > pub.mean())
                    else: keep = rng.random() < 0.5
                    if keep: pub, priv = cp, cq
            mk = lambda r: pd.DataFrame(r, columns=["TeamId", "Id", "pub", "priv"]).assign(day=pd.Timestamp("2020-01-01"))
            Xs.append(competition_row(team_steps(mk(recs_pre), mk(recs_post), True)))
        x = pd.DataFrame(Xs)
        res.append(dict(mode=mode, share_X_negative=(x.X < 0).mean(), share_J_negative=(x.J < 0).mean(), share_Dq_positive=(x.Dq > 0).mean(),
                        share_placebo_negative=(x.X_placebo < 0).mean(), mean_J_pp=100 * x.J.mean(), mean_Dq_pp=100 * x.Dq.mean()))
    print(pd.DataFrame(res).round(3).to_string(index=False))


def main():
    import duckdb, os
    os.makedirs("outputs/stage7", exist_ok=True)
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
        rawpre, rawpost = pre, post
        if r.Group not in RAW_SCORE_GROUPS:                       # same clipping rule as plan v1.0, bounds from PRE-deadline public scores
            lo, hi = pre.pub.quantile([0.01, 0.99])
            pre = pre.assign(pub=pre.pub.clip(lo, hi), priv=pre.priv.clip(lo, hi)); post = post.assign(pub=post.pub.clip(lo, hi), priv=post.priv.clip(lo, hi))
        t = team_steps(pre, post, bool(r.higher_better))
        if len(t) < MIN_TEAMS: continue
        row = dict(CompetitionId=r.CompetitionId, Cohort=r.Cohort, Group=r.Group, Segment=r.Segment, CodeOnly=r.CodeOnly, flagged=r.flagged,
                   team_spread=r.team_spread, drift_mean=r.drift_mean, **competition_row(t))
        if r.Group not in RAW_SCORE_GROUPS:
            tu = team_steps(rawpre, rawpost, bool(r.higher_better)); row["X_unclipped"] = tu.J.mean() - tu.Dq.mean()
        else: row["X_unclipped"] = row["X"]
        rows.append(row)
    x = pd.DataFrame(rows); x["rel_X"] = x.X / x.team_spread; x["rel_J"] = x.J / x.team_spread
    x.to_csv("outputs/stage7/deadline_per_competition.csv", index=False)
    res = [dict(test="PRIMARY T1", **sign_summary("X = J - Dq, O+E", x.X, rng))]
    res.append(dict(test="effect size", **sign_summary("relative X (in team spreads), O+E", x.rel_X, rng)))
    for coh in ("E", "O"): res.append(dict(test="secondary", **sign_summary(f"X, {coh}", x[x.Cohort == coh].X, rng)))
    res.append(dict(test="secondary", **sign_summary("J (step across the deadline), O+E", x.J, rng)))
    res.append(dict(test="secondary", **sign_summary("relative J, O+E", x.rel_J, rng)))
    res.append(dict(test="secondary", **sign_summary("placebo: X one quarter earlier, O+E", x.X_placebo, rng)))
    res.append(dict(test="secondary", **sign_summary("X minus placebo X, O+E", x.X - x.X_placebo, rng)))
    res.append(dict(test="secondary", **sign_summary("X, teams whose post-deadline public score is not worse", x.X_restricted, rng)))
    res.append(dict(test="secondary", **sign_summary("X, unclipped", x.X_unclipped, rng)))
    res.append(dict(test="secondary", **sign_summary("X, unflagged", x[~x.flagged].X, rng)))
    res.append(dict(test="secondary", **sign_summary("X, accuracy/AUC/MAP@K", x[x.Group.isin(RAW_SCORE_GROUPS)].X, rng)))
    res.append(dict(test="secondary", **sign_summary("X, competitions with positive pre-deadline drift", x[x.drift_mean > 0].X, rng)))
    res.append(dict(test="context", **sign_summary("private-score change across the deadline (negative = worse)", x.level_J, rng)))
    res.append(dict(test="context", **sign_summary("private-score change in the last pre-deadline step", x.level_Dq, rng)))
    res = pd.DataFrame(res); res.to_csv("outputs/stage7/deadline_results.csv", index=False)
    pd.set_option("display.width", 220); print(len(x), "competitions"); print(res.round(4).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true"); a = ap.parse_args()
    selftest() if a.selftest else main()
