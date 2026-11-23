from __future__ import annotations
import math
from dataclasses import dataclass

import pandas as pd

import config


def product_terms(row) -> set[str]:
    return set(str(row["istilah_kulit"]).split()) | set(str(row["istilah_tekstur"]).split()) | set(str(row["istilah_masalah"]).split())


def idf_table(docs: list[set[str]]) -> dict[str, float]:
    n = len(docs)
    df: dict[str, int] = {}
    for d in docs:
        for t in d:
            df[t] = df.get(t, 0) + 1
    return {t: math.log10(n / c) for t, c in df.items()}


def tfidf(doc: set[str], idf: dict[str, float]) -> dict[str, float]:
    """tf biner: f(t,d)=1 -> TF = 1/|d|. Istilah yang tidak ada pada satu pun produk (df=0) diabaikan."""
    if not doc:
        return {}
    tf = 1 / len(doc)
    return {t: tf * idf[t] for t in doc if t in idf}


def cosine(u: dict[str, float], p: dict[str, float]) -> float:
    dot = sum(w * p[t] for t, w in u.items() if t in p)
    nu = math.sqrt(sum(w * w for w in u.values()))
    npp = math.sqrt(sum(w * w for w in p.values()))
    return dot / (nu * npp) if nu and npp else 0.0


@dataclass
class CBFResult:
    scored: pd.DataFrame        # semua produk (jenis terpilih) + kolom sim
    candidates: pd.DataFrame    # lolos sim >= theta dan harga <= budget
    n_total: int
    n_pass_sim: int
    n_over_budget: int
    theta: float
    limited: bool               # kandidat < batas minimum
    min_price_pass: float | None  # harga termurah di antara produk yang lolos sim >= theta
    min_candidates: int
    profile: list[str]
    idf: dict


def run_cbf(df: pd.DataFrame, jenis_produk: str, skin, texture, concern, budget: float,
            theta: float = config.THETA, min_candidates: int = config.MIN_CANDIDATES) -> CBFResult:
    d = df[df["jenis_produk"] == jenis_produk].copy()                 # korpus N = produk berjenis sama
    docs = [product_terms(r) for _, r in d.iterrows()]
    idf = idf_table(docs)
    profile = sorted(set(skin) | set(texture) | set(concern))
    u = tfidf(set(profile), idf)
    d["sim"] = [cosine(u, tfidf(doc, idf)) for doc in docs]

    lolos_sim = d[d["sim"] >= theta - 1e-12]                          # syarat 1
    cand = lolos_sim[lolos_sim["harga_num"] <= budget]                # syarat 2
    cand = cand.sort_values(["sim", "no"], ascending=[False, True])
    return CBFResult(scored=d, candidates=cand, n_total=len(d), n_pass_sim=len(lolos_sim),
                     n_over_budget=len(lolos_sim) - len(cand), theta=theta,
                     min_price_pass=(float(lolos_sim['harga_num'].min()) if len(lolos_sim) else None),
                     limited=len(cand) < min_candidates, min_candidates=min_candidates, profile=profile, idf=idf)


def explain(res: CBFResult, budget: float, theta: float = config.THETA):
    """Rincian perhitungan CBF untuk ditampilkan: (tabel istilah profil + IDF, tabel kemiripan tiap produk)."""
    d = res.scored
    docs = [product_terms(r) for _, r in d.iterrows()]
    n = len(docs)
    prof = set(res.profile)
    u = tfidf(prof, res.idf)
    nu = math.sqrt(sum(w * w for w in u.values()))

    rows = []
    for t in res.profile:
        df_t = sum(1 for doc in docs if t in doc)
        rows.append({"Istilah": t, "df": df_t,
                     "IDF = log10(N/df)": (res.idf[t] if t in res.idf else None),
                     "TF pengguna": (1 / len(prof)),
                     "TF-IDF pengguna": u.get(t, 0.0),
                     "Keterangan": "dipakai" if t in res.idf else "diabaikan (tidak ada di produk mana pun)"})
    term_tbl = pd.DataFrame(rows)

    prow = []
    for (_, r), doc in zip(d.iterrows(), docs):
        p = tfidf(doc, res.idf)
        dot = sum(w * p[t] for t, w in u.items() if t in p)
        npp = math.sqrt(sum(w * w for w in p.values()))
        lolos_sim = r["sim"] >= theta - 1e-12
        lolos_harga = r["harga_num"] <= budget
        status = ("Lolos" if lolos_sim and lolos_harga
                  else "Melebihi budget" if lolos_sim else f"Sim < {theta:.2f}")
        prow.append({"Merek": r["brand"], "Produk": r["nama_produk"],
                     "Istilah cocok": ", ".join(sorted(prof & doc)) or "-",
                     "|d|": len(doc), "u·p": dot, "|u|": nu, "|p|": npp, "sim(u,p)": r["sim"],
                     "Harga (Rp)": r["harga_num"], "Status": status})
    prod_tbl = (pd.DataFrame(prow).sort_values("sim(u,p)", ascending=False, kind="stable")
                .reset_index(drop=True))
    prod_tbl.insert(0, "No", prod_tbl.index + 1)
    return term_tbl, prod_tbl
