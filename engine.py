from __future__ import annotations
import pandas as pd

import cbf, config, smart


def load_data(path=config.BERSIH_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["rating_estimasi"] = df["rating_estimasi"].astype(bool)
    for c in ["istilah_kulit", "istilah_tekstur", "istilah_masalah", "tekstur_produk", "jenis_kulit", "masalah_kulit", "bahan_aktif"]:
        df[c] = df[c].fillna("")
    return df


def recommend(df, jenis_produk, skin, texture, concern, budget, weights_raw, theta=config.THETA, min_candidates=config.MIN_CANDIDATES):
    """-> (ranked DataFrame, info dict). Tidak pernah melempar error untuk 0 atau 1 kandidat."""
    res = cbf.run_cbf(df, jenis_produk, skin, texture, concern, budget, theta, min_candidates)
    w, raw = smart.normalize_weights(weights_raw["harga"], weights_raw["rating"], weights_raw["bahan_aktif"])
    ranked = smart.run_smart(res.candidates, w)
    info = {"n_total": res.n_total, "n_pass_sim": res.n_pass_sim, "n_over_budget": res.n_over_budget,
            "n_candidates": len(ranked), "min_price_pass": res.min_price_pass, "theta": res.theta, "limited": res.limited, "min_candidates": res.min_candidates,
            "profile": res.profile, "weights": w, "weights_raw": raw}
    return ranked, info
