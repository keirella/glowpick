from __future__ import annotations
import json, uuid
from datetime import datetime

import pandas as pd

import config

COLS = ["id", "waktu", "jenis_produk", "profil", "hasil", "info"]
KEEP = ["no", "brand", "nama_produk", "jenis_produk", "tekstur_produk", "jenis_kulit", "masalah_kulit", "harga_num",
        "rating_num", "rating_estimasi", "jumlah_bahan_cocok", "bahan_aktif", "sim", "u_harga", "u_rating", "u_bahan",
        "smart", "peringkat"]


def _read() -> pd.DataFrame:
    if config.RIWAYAT_PATH.exists():
        try:
            return pd.read_csv(config.RIWAYAT_PATH)
        except Exception:
            pass
    return pd.DataFrame(columns=COLS)


def save(inputs: dict, ranked: pd.DataFrame, info: dict) -> str:
    h = _read()
    rid = uuid.uuid4().hex[:8]
    row = {"id": rid, "waktu": datetime.now().strftime("%d %b %Y %H:%M"), "jenis_produk": inputs["ptype"],
           "profil": json.dumps(inputs, ensure_ascii=False),
           "hasil": ranked[[c for c in KEEP if c in ranked.columns]].to_json(orient="records", force_ascii=False),
           "info": json.dumps(info, ensure_ascii=False, default=float)}
    config.DATA.mkdir(exist_ok=True)
    pd.concat([h, pd.DataFrame([row])], ignore_index=True).to_csv(config.RIWAYAT_PATH, index=False)
    return rid


def list_history() -> pd.DataFrame:
    return _read().iloc[::-1].reset_index(drop=True)          # terbaru di atas


def load(rid: str):
    h = _read()
    r = h[h["id"] == rid]
    if r.empty:
        return None
    r = r.iloc[0]
    return json.loads(r["profil"]), pd.read_json(__import__("io").StringIO(r["hasil"]), orient="records"), json.loads(r["info"])


def delete(rid: str):
    h = _read()
    h[h["id"] != rid].to_csv(config.RIWAYAT_PATH, index=False)
