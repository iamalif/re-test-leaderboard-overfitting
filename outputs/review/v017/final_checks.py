"""Read-only final QA. Usage: python final_checks.py /path/to/project."""
from pathlib import Path
import hashlib, json, re, subprocess, sys, zipfile

p = Path(sys.argv[1]).resolve()
out = Path(__file__).parent
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

r = {'commit': subprocess.check_output(['git', '-C', str(p), 'rev-parse', 'HEAD'], text=True).strip(),
     'pdf_sha256': sha(p/'paper/main.pdf'), 'zip_sha256': sha(p/'anonymous_review_package.zip')}
r['archived_hashes'] = {}
for line in (p/'analysis_plan/SHA256SUMS.txt').read_text().splitlines():
    h, name = line.split(None, 1)
    r['archived_hashes'][name] = sha(p/name) == h
ledger = [json.loads(s) for s in (p/'outputs/run_ledger.jsonl').read_text().splitlines()]
latest = {}
for row in ledger:
    latest.update(row['outputs_changed'])
r['ledger'] = {'stages': len(ledger), 'exits': [x['exit'] for x in ledger],
               'output_count': len(latest), 'hash_failures': [n for n,h in latest.items() if sha(p/n) != h]}
with zipfile.ZipFile(p/'anonymous_review_package.zip') as z:
    bad, diff, hits = [], [], {}
    for line in z.read('MANIFEST_SHA256.txt').decode().splitlines():
        h, n = line.split('  ', 1)
        if hashlib.sha256(z.read(n)).hexdigest() != h: bad.append(n)
        if (p/n).is_file() and (p/n).read_bytes() != z.read(n): diff.append(n)
    for n in z.namelist():
        try: text = z.read(n).decode()
        except UnicodeDecodeError: continue
        found = re.findall(r'iamalif|/Users/alif|/sessions/|re-test-leaderboard-overfitting', text, re.I)
        if found: hits[n] = sorted(set(found))
    r['package'] = {'members': len(z.namelist()), 'manifest_failures': bad,
                    'project_differences': diff, 'targeted_identity_hits': hits}
r['appendix_byte_identical'] = (out/'paper/appendix_secondary.tex').read_bytes() == (p/'paper/appendix_secondary.tex').read_bytes()
r['changed_analysis_files_since_v016'] = subprocess.check_output(
    ['git','-C',str(p),'diff','--name-only','48bc60a','HEAD','--','scripts/stage*.py','run_all.sh','requirements*.txt','outputs/stage*'], text=True).splitlines()
(out/'final_checks.json').write_text(json.dumps(r, indent=2))
print(json.dumps(r, indent=2))
