from __future__ import annotations
import argparse, glob, re
from pathlib import Path

import numpy as np
import pandas as pd

import pconfig as config, encoding, utils


# konversi numerik
def parse_price_list(s) -> list[int]:
    """'Rp16.000 (60ml) / Rp27.000 (100ml)' | 'Rp45.000 - 55.000' | '$7.62 (diskon dari $9.57)' -> [angka rupiah].
    '(ukuran)' & 'diskon dari ...' diabaikan; dolar dikonversi dengan config.USD_IDR."""
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return []
    t = re.split(r"diskon dari", re.sub(r"\(.*?\)", "", str(s)), flags=re.I)[0]
    if "$" in t:
        return [int(round(float(n) * config.USD_IDR)) for n in re.findall(r"\d+(?:\.\d+)?", t)]
    out = []
    for n in re.findall(r"\d[\d.]*", t):
        n = n.replace(".", "")
        if n and int(n) >= 1000:
            out.append(int(n))
    return out


def parse_rating(s) -> float:
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return np.nan
    m = re.search(r"\d+(?:[.,]\d+)?", str(s))
    if not m:
        return np.nan
    r = float(m.group().replace(",", "."))
    return r if 0 < r <= 5 else np.nan              # di luar skala -> tidak wajar


def fmt_rp(n: int) -> str:
    return "Rp" + f"{n:,}".replace(",", ".")


def fmt_price(vals: list[int]) -> str:
    lo, hi = min(vals), max(vals)
    return fmt_rp(lo) if lo == hi else f"{fmt_rp(lo)} - {f'{hi:,}'.replace(',', '.')}"


# integrasi
_NOISE = {"ml", "gr", "g", "gram", "official", "original", "new", "bpom", "pcs", "isi", "paket", "with", "dengan", "for", "untuk", "and", "dan"}


def name_tokens(name: str, brand: str) -> set[str]:
    t = re.sub(r"[^a-z0-9 ]", " ", str(name).lower())
    t = re.sub(r"\b\d+\s?(ml|gr|g|gram)\b", " ", t)
    toks = set(t.split()) - _NOISE - set(brand.lower().split())
    return {w for w in toks if not w.isdigit()}


def best_match(b_tokens: set[str], cands: pd.DataFrame, thr=0.75):
    if not b_tokens:
        return []
    hits = [(len(b_tokens & m["_tok"]) / len(b_tokens), i) for i, m in cands.iterrows()]
    hits = [h for h in hits if h[0] >= thr]
    if not hits:
        return []
    top = max(h[0] for h in hits)
    return [i for c, i in hits if c >= top - 0.05]


def integrate(raw_dir: Path = config.RAW, log=print) -> pd.DataFrame:
    brands = [pd.read_csv(f) for f in sorted(glob.glob(str(raw_dir / "brand_*.csv")))]
    if not brands:
        raise FileNotFoundError("Belum ada data/raw/brand_*.csv - jalankan scraping situs brand dahulu.")
    mk = [pd.read_csv(f) for f in glob.glob(str(raw_dir / "*_official.csv"))]
    b = pd.concat(brands, ignore_index=True)
    m = pd.concat(mk, ignore_index=True) if mk else pd.DataFrame(columns=["brand", "nama_produk", "harga", "rating", "bahan_aktif"])
    log(f"integrasi: {len(brands)} berkas brand ({len(b)} baris) + {len(mk)} berkas marketplace ({len(m)} baris)")
    m["_tok"] = [name_tokens(n, br) for n, br in zip(m["nama_produk"], m["brand"])]
    rows = []
    for _, r in b.iterrows():                       # kunci produk = merek + nama produk
        sub = m[m["brand"].str.lower() == str(r["brand"]).lower()]
        hit = sub.loc[best_match(name_tokens(r["nama_produk"], r["brand"]), sub)]
        aktif = [str(x) for x in hit["bahan_aktif"].dropna() if str(x).strip()]
        rows.append({**r.to_dict(),
                     "_harga_list": [p for v in hit["harga"] for p in parse_price_list(v)],
                     "_rating_list": [x for x in (parse_rating(v) for v in hit["rating"]) if not np.isnan(x)],
                     "bahan_aktif_mp": ", ".join(dict.fromkeys(aktif))})
    return pd.DataFrame(rows)


def from_gabungan(path) -> pd.DataFrame:
    g = pd.read_csv(path) if str(path).lower().endswith(".csv") else pd.read_excel(path)
    g = g.rename(columns={"Merk": "Brand"})
    return pd.DataFrame({
        "brand": g["Brand"].astype(str).str.strip(), "nama_produk": g["Nama Produk"].astype(str),
        "jenis_produk": g["Jenis Produk"].astype(str).str.split(r"\s*\(").str[0].str.strip(),
        "tekstur_produk": g["Tekstur Produk"], "jenis_kulit": g["Jenis Kulit"], "masalah_kulit": g["Masalah Kulit"],
        "_harga_list": g["Harga"].map(parse_price_list),
        "_rating_list": g["Rating"].map(lambda v: [] if np.isnan(parse_rating(v)) else [parse_rating(v)]),
        "bahan_aktif_mp": g["Bahan Aktif Utama"].astype(str), "jumlah_given": g["Jumlah Bahan Aktif Cocok"]})


# cleaning
def clean(df: pd.DataFrame, log=print) -> pd.DataFrame:
    n0 = len(df)
    df = df.drop_duplicates(subset=["brand", "nama_produk"]).copy()
    log(f"cleaning: duplikat dihapus -> {len(df)} baris")
    for c in ["nama_produk", "jenis_kulit", "masalah_kulit", "tekstur_produk", "deskripsi", "komposisi"]:
        if c in df:
            df[c] = df[c].map(utils.clean_text)
    luar = ~df["jenis_produk"].isin(config.PRODUCT_TYPES)
    log(f"cleaning: {int(luar.sum())} produk di luar jenis base skincare disisihkan")
    df = df[~luar]
    tanpa_harga = df["_harga_list"].map(len) == 0
    log(f"cleaning: {int(tanpa_harga.sum())} produk tanpa harga dikeluarkan (tidak diisi rata-rata)")
    df = df[(~tanpa_harga) & (df["nama_produk"].str.len() > 0)]
    log(f"cleaning: {n0} -> {len(df)} baris")
    return df.reset_index(drop=True)


# pengodean
def encode(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["harga_num"] = df["_harga_list"].map(lambda v: float(np.mean([min(v), max(v)])))   # rentang -> titik tengah
    df["harga_teks"] = df["_harga_list"].map(fmt_price)
    df["rating_num"] = df["_rating_list"].map(lambda v: round(float(np.mean(v)), 1) if v else np.nan)
    # nilai rating yang berulang >= 10 kali = hasil pengisian rata-rata (bukan rating asli)
    freq = df["rating_num"].map(df["rating_num"].value_counts())
    df["rating_estimasi"] = df["rating_num"].notna() & (freq >= 10)

    tk, tt, tm, aktif, jumlah = [], [], [], [], []
    for _, r in df.iterrows():
        ks = encoding.skin_tags(r["jenis_kulit"])
        ms = encoding.concern_tags(r["masalah_kulit"], r["jenis_kulit"])
        tk.append(ks); tt.append(encoding.texture_tags(r["tekstur_produk"])); tm.append(ms)
        text = f"{r.get('komposisi', '')} {r['bahan_aktif_mp']} {r['nama_produk']}"
        found = utils.detect_actives(text)
        aktif.append(r["bahan_aktif_mp"] or ", ".join(n for n, _ in found))
        given = r.get("jumlah_given", np.nan)
        jumlah.append(int(given) if pd.notna(given) else sum(1 for _, t in found if t & ms))
    df["istilah_kulit"] = [" ".join(sorted(s)) for s in tk]
    df["istilah_tekstur"] = [" ".join(sorted(s)) for s in tt]
    df["istilah_masalah"] = [" ".join(sorted(s)) for s in tm]
    df["bahan_aktif"] = aktif
    df["jumlah_bahan_cocok"] = jumlah
    return df

# case folding, tokenizing, stopword removal
_MULTI = sorted({n.lower() for _, n, _ in config.ACTIVES if " " in n}, key=len, reverse=True)


def tokenize(text: str) -> list[str]:
    t = str(text).lower()                                            # case folding
    for term in _MULTI:                                              # nama bahan >1 kata = satu token
        t = t.replace(term, term.replace(" ", "_"))
    toks = re.findall(r"[a-z0-9_%+]+", t)                            # tokenizing
    return [w for w in toks if (w not in config.STOPWORDS or w in config.KEEP_TERMS)]   # stopword removal


def add_tokens(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    doc = (df["nama_produk"] + " " + df["jenis_produk"] + " " + df["tekstur_produk"].astype(str) + " " +
           df["jenis_kulit"].astype(str) + " " + df["masalah_kulit"].astype(str) + " " + df["bahan_aktif"].astype(str))
    df["token"] = doc.map(lambda s: " ".join(tokenize(s)))
    return df


# keluaran
BERSIH_COLS = ["no", "brand", "nama_produk", "jenis_produk", "tekstur_produk", "jenis_kulit", "masalah_kulit",
               "harga_teks", "harga_num", "rating_num", "rating_estimasi", "jumlah_bahan_cocok", "bahan_aktif",
               "istilah_kulit", "istilah_tekstur", "istilah_masalah", "token"]


def finalize(df: pd.DataFrame) -> pd.DataFrame:
    ob = {b: i for i, b in enumerate(config.BRANDS)}
    ot = {t: i for i, t in enumerate(config.PRODUCT_TYPES)}
    df = df.assign(_b=df["brand"].map(ob).fillna(99), _t=df["jenis_produk"].map(ot).fillna(99))
    df = df.sort_values(["_b", "_t"], kind="stable").reset_index(drop=True)
    df.insert(0, "no", range(1, len(df) + 1))
    return df[BERSIH_COLS]


def run(source: str = "raw", gabungan_path=None, log=print) -> pd.DataFrame:
    """source='raw' (hasil scraping) atau 'gabungan'. Menulis data/processed/produk_bersih.csv dan mengembalikannya."""
    df = from_gabungan(gabungan_path) if source == "gabungan" else integrate(log=log)
    out = finalize(add_tokens(encode(clean(df, log=log))))
    config.PROCESSED.mkdir(parents=True, exist_ok=True)
    out.to_csv(config.BERSIH_PATH, index=False, encoding="utf-8-sig")
    log(f"selesai: {len(out)} produk -> {config.BERSIH_PATH.name}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-gabungan", metavar="FILE", help="pakai dataset gabungan (csv/xlsx) alih-alih data/raw")
    a = ap.parse_args()
    out = run("gabungan", a.from_gabungan) if a.from_gabungan else run("raw")
    print(out[["no", "brand", "nama_produk", "harga_num", "rating_num", "jumlah_bahan_cocok", "istilah_kulit"]].head(8).to_string())
