from __future__ import annotations
import pandas as pd

import config

CRITERIA = ["harga", "rating", "bahan_aktif"]
CRITERIA_LABEL = {"harga": "Harga (cost)", "rating": "Rating (benefit)", "bahan_aktif": "Bahan aktif sesuai (benefit)"}


def normalize_weights(w_harga: int, w_rating: int, w_bahan: int):
    """Bobot mentah 1-5 dari formulir pengguna -> bobot ternormalisasi (jumlah = 1). Mengembalikan (w, raw)."""
    raw = {"harga": float(w_harga), "rating": float(w_rating), "bahan_aktif": float(w_bahan)}
    tot = sum(raw.values())
    return {c: raw[c] / tot for c in CRITERIA}, raw


def _minmax(s: pd.Series, cost: bool) -> pd.Series:
    lo, hi = s.min(), s.max()
    if hi == lo:                                                     # satu kandidat / nilai sama -> tanpa pembagian nol
        return pd.Series(1.0, index=s.index)
    return (hi - s) / (hi - lo) if cost else (s - lo) / (hi - lo)


def run_smart(cands: pd.DataFrame, w: dict) -> pd.DataFrame:
    p = cands.copy()
    if p.empty:
        return p.assign(u_harga=[], u_rating=[], u_bahan=[], smart=[], peringkat=[])
    p["u_harga"] = _minmax(p["harga_num"], cost=True)
    p["u_rating"] = _minmax(p["rating_num"], cost=False).where(p["rating_num"].notna(), config.RATING_NETRAL)
    p["u_bahan"] = _minmax(p["jumlah_bahan_cocok"].astype(float), cost=False)
    p["smart"] = w["harga"] * p["u_harga"] + w["rating"] * p["u_rating"] + w["bahan_aktif"] * p["u_bahan"]
    p = p.sort_values(["smart", "sim"], ascending=False).reset_index(drop=True)
    p["peringkat"] = p.index + 1
    return p
