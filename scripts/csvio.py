"""Exact reading of the project's CSV tables, identical under every pandas version (added 17 Nov 2026).

pandas' default CSV number parser is not correctly rounded in pandas 2.x and 3.0 (it is in 3.1). Every script reads
tables through read_csv_exact, which reads all cells as text and converts them with Python's int() and float()
(correctly rounded). Column types follow pandas' own inference: all-integer columns become int64 (float64 if any
cell is missing), true/false columns (True, TRUE, true and their opposites, as pandas accepts) become bool (object if any cell is missing), numeric columns float64, anything
else stays text.
"""
import re
import numpy as np
import pandas as pd

_INT = re.compile(r"^\s*[+-]?\d+\s*$")
_BOOL = {"True": True, "TRUE": True, "true": True, "False": False, "FALSE": False, "false": False}


def _convert(s):
    vals = s.dropna()
    if len(vals) == 0:
        return s.astype(float)
    if vals.isin(_BOOL).all():                     # same spellings pandas accepts by default
        out = s.map(_BOOL)
        return out.astype(bool) if s.notna().all() else out.astype(object)
    if vals.map(lambda v: bool(_INT.match(v))).all():
        return s.map(int).astype("int64") if s.notna().all() else s.map(lambda v: float(int(v)) if isinstance(v, str) else np.nan).astype(float)
    try:
        return s.map(lambda v: float(v) if isinstance(v, str) else np.nan).astype(float)
    except ValueError:
        return s.astype(object)


def read_csv_exact(path, **kw):
    if "chunksize" in kw: raise ValueError("read_csv_exact does not support chunksize")
    kw["dtype"] = str
    df = pd.read_csv(path, **kw)
    for c in df.columns:
        df[c] = _convert(df[c])
    return df
