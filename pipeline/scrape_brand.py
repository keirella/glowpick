from __future__ import annotations
import json, re, sys
import xml.etree.ElementTree as ET

import pandas as pd
from bs4 import BeautifulSoup

import pconfig as config, utils

PRODUCT_URL_HINT = re.compile(r"/(product|products|produk|p)/[^/]+", re.I)


# Shopify
def from_shopify(base: str) -> list[dict]:
    items, page = [], 1
    while True:
        r = utils.polite_get(f"{base}/products.json?limit=250&page={page}")
        if r is None:
            break
        try:
            prods = r.json().get("products", [])
        except ValueError:
            break
        if not prods:
            break
        for p in prods:
            items.append({"nama": p["title"], "deskripsi": BeautifulSoup(p.get("body_html") or "", "lxml").get_text(" "),
                          "tipe_situs": p.get("product_type", ""), "url": f"{base}/products/{p['handle']}"})
        page += 1
    return items


# sitemap + JSON-LD
def sitemap_urls(base: str) -> list[str]:
    queue, seen, out = [f"{base}/sitemap.xml"], set(), []
    while queue:
        u = queue.pop(0)
        if u in seen:
            continue
        seen.add(u)
        r = utils.polite_get(u)
        if r is None:
            continue
        try:
            root = ET.fromstring(r.content)
        except ET.ParseError:
            continue
        for loc in root.iter():
            if loc.tag.endswith("loc") and loc.text:
                (queue if loc.text.endswith(".xml") else out).append(loc.text.strip())
    return [u for u in out if PRODUCT_URL_HINT.search(u)]


def parse_product_page(url: str) -> dict | None:
    r = utils.polite_get(url)
    if r is None:
        return None
    soup = BeautifulSoup(r.text, "lxml")
    name = desc = ""
    for tag in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(tag.string or "")
        except ValueError:
            continue
        for d in (data if isinstance(data, list) else [data]):
            if isinstance(d, dict) and d.get("@type") in ("Product", ["Product"]):
                name, desc = d.get("name", ""), d.get("description", "")
    if not name:
        og = soup.find("meta", property="og:title")
        name = og["content"] if og else (soup.title.string if soup.title else "")
    if not desc:
        og = soup.find("meta", property="og:description")
        desc = og["content"] if og else ""
    body = soup.get_text(" ")                      # komposisi biasanya ada di badan halaman
    return {"nama": name, "deskripsi": desc, "tipe_situs": "", "url": url, "body": body}


def from_sitemap(base: str) -> list[dict]:
    items = []
    for u in sitemap_urls(base):
        p = parse_product_page(u)
        if p and p["nama"]:
            items.append(p)
    return items


# bentuk baris dataset
def to_row(brand: str, it: dict) -> dict | None:
    nama = utils.clean_text(it["nama"])
    jenis = utils.classify_type(nama, it.get("tipe_situs", ""))
    if jenis not in config.PRODUCT_TYPES:          # di luar jenis base skincare -> disisihkan
        return None
    teks = utils.clean_text(f"{nama}. {it.get('deskripsi', '')}")
    raw_body = it.get("body") or it.get("deskripsi", "")
    return {
        "brand": brand, "nama_produk": nama, "jenis_produk": jenis,
        "tekstur_produk": utils.extract_texture(teks, jenis),
        "jenis_kulit": utils.extract_skin(teks),
        "masalah_kulit": utils.extract_concern(teks),
        "deskripsi": teks[:600], "komposisi": utils.extract_ingredients(raw_body), "url": it["url"],
    }


def scrape_brand(brand: str) -> pd.DataFrame:
    base = config.BRANDS[brand]["site"]
    print(f"[{brand}] {base}")
    items = from_shopify(base)
    print(f"  Shopify  : {len(items)} produk")
    if not items:
        items = from_sitemap(base)
        print(f"  Sitemap  : {len(items)} produk")
    rows = [r for r in (to_row(brand, i) for i in items) if r]
    df = pd.DataFrame(rows).drop_duplicates(subset=["nama_produk"])
    out = config.RAW / f"brand_{brand.lower()}.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"  -> {out.name}: {len(df)} produk base skincare")
    return df


if __name__ == "__main__":
    targets = sys.argv[1:] or list(config.BRANDS)
    config.RAW.mkdir(parents=True, exist_ok=True)
    for b in targets:
        scrape_brand(b)
