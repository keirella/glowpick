import datetime as dt
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pconfig as config          
import pandas as pd               


def run_brand(brands=None):
    import scrape_brand
    config.RAW.mkdir(parents=True, exist_ok=True)
    for b in (brands or list(config.BRANDS)):
        try:
            scrape_brand.scrape_brand(b)
        except Exception as e:
            print(f"  [gagal] {b}: {e}")


def run_marketplace():
    for site in ("tokopedia", "shopee"):
        print(f"\n>> scraping {site} (login/captcha manual di browser yang terbuka bila diminta)")
        subprocess.call([sys.executable, str(HERE / "scrape_marketplace.py"), "--site", site, "--headed"])


def run_preprocess(gabungan=None):
    import preprocessing
    out = preprocessing.run("gabungan", gabungan) if gabungan else preprocessing.run("raw")
    print(f"\nproduk_bersih.csv: {len(out)} produk")


def cek():
    print("== Status berkas ==")
    files = sorted(config.RAW.glob("*.csv")) + [config.BERSIH_PATH, config.RIWAYAT_PATH]
    for f in files:
        name = f.relative_to(config.ROOT)
        if f.exists():
            n = len(pd.read_csv(f))
            print(f"  {str(name):45s} {n:5d} baris   {dt.datetime.fromtimestamp(f.stat().st_mtime):%d %b %Y %H:%M}")
        else:
            print(f"  {str(name):45s} belum ada")
    if config.BERSIH_PATH.exists():
        d = pd.read_csv(config.BERSIH_PATH)
        print(f"\n== Data bersih: {len(d)} produk ==")
        print(pd.crosstab(d["brand"], d["jenis_produk"]).to_string())
        print(f"\n  tanpa rating: {int(d['rating_num'].isna().sum())} | rating estimasi: {int(d['rating_estimasi'].sum())}"
              f" | tanpa bahan aktif sesuai: {int((d['jumlah_bahan_cocok'] == 0).sum())}")
        print("  rata-rata harga per jenis (Rp):")
        print(d.groupby("jenis_produk")["harga_num"].mean().round(0).astype(int).to_string())


def menu():
    print(__doc__.split("Tekan")[0])
    print("Pilih tahap:\n  1) scraping situs brand\n  2) scraping Shopee & Tokopedia\n  3) preprocessing\n  4) semua tahap (1-3)\n  5) cek data")
    return {"1": ["brand"], "2": ["marketplace"], "3": ["preprocess"], "4": ["all"], "5": ["cek"]}.get(input("> ").strip(), [])


def main(argv):
    argv = argv or menu()
    if not argv:
        return
    cmd, rest = argv[0], argv[1:]
    if cmd == "brand":
        run_brand(rest)
    elif cmd == "marketplace":
        run_marketplace()
    elif cmd == "preprocess":
        run_preprocess(rest[1] if rest[:1] == ["--from-gabungan"] and len(rest) > 1 else None)
    elif cmd == "all":
        run_brand(); run_marketplace(); run_preprocess()
    elif cmd == "cek":
        cek()
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
