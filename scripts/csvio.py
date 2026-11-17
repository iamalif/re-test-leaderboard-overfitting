"""Round-trip-safe reading of this project's CSV tables (added 17 Nov 2026; v2 the same day).

pandas' default CSV number parser is not correctly rounded in pandas 2.x and 3.0 (it is in 3.1). Every script reads
tables through read_csv_exact, which reads all cells as text and converts them with Python's int() and float()
(correctly rounded). Column types follow pandas' default inference for the kinds of columns this project writes:
  - every cell an integer within the int64 range  -> int64 (float64 if any cell is missing, as pandas does);
  - every cell true/false (True, TRUE, true and opposites, as pandas accepts) -> bool (object if any is missing);
  - every cell a plain decimal number (digits, point, exponent, nan, inf; no underscores) -> float64;
  - anything else -> text.
Scope: verified to reproduce pandas' types and values on every table this project writes, under pandas 2.3 and 3.1.
It is not a general replacement for pandas.read_csv: integers outside int64 stay text, and options that change type
inference (parse_dates, converters) are refused.
"""
import re
import numpy as np
import pandas as pd

_INT = re.compile(r"^\s*[+-]?\d+\s*$")
_NUM = re.compile(r"^\s*[+-]?((\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?|nan|inf|infinity)\s*$", re.I)
_BOOL = {"True": True, "TRUE": True, "true": True, "False": False, "FALSE": False, "false": False}
_I64 = (-(2 ** 63), 2 ** 63 - 1)


def _convert(s):
    vals = s.dropna()
    if len(vals) == 0:
        return s.astype(float)
    if vals.isin(_BOOL).all():
        out = s.map(_BOOL)
        return out.astype(bool) if s.notna().all() else out.astype(object)
    if vals.map(lambda v: bool(_INT.match(v))).all():
        ints = vals.map(int)
        if ints.min() < _I64[0] or ints.max() > _I64[1]:
            return s.astype(object)                                   # out of int64 range: keep exact text
        return s.map(int).astype("int64") if s.notna().all() else s.map(lambda v: float(int(v)) if isinstance(v, str) else np.nan).astype(float)
    if vals.map(lambda v: bool(_NUM.match(v))).all():
        return s.map(lambda v: float(v) if isinstance(v, str) else np.nan).astype(float)
    return s.astype(object)


def read_csv_exact(path, **kw):
    for bad in ("chunksize", "parse_dates", "converters", "dtype", "true_values", "false_values"):
        if bad in kw: raise ValueError(f"read_csv_exact does not support {bad}")
    kw["dtype"] = str
    df = pd.read_csv(path, **kw)
    for c in df.columns:
        df[c] = _convert(df[c])
    return df
