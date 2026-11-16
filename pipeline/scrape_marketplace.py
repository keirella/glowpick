from __future__ import annotations
import argparse, random, re, time
import pandas as pd
import pconfig as config

LINK_SELECTOR = {"tokopedia": 'a[href*="tokopedia.com/"]', "shopee": 'a[href*="-i."]'}
PRICE_RE = re.compile(r"Rp\s?[\d.]+(?:\s?-\s?(?:Rp\s?)?[\d.]+)?")
RATING_RE = re.compile(r"(?<![\d.])([1-5](?:[.,]\d)?)(?![\d.%])")


def parse_card(text: str):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    price = next((PRICE_RE.search(l).group() for l in lines if PRICE_RE.search(l)), None)
    # Tokopedia/Shopee menampilkan harga coret (diskon) lebih dulu -> ambil harga TERENDAH sebagai harga jual
    prices = [PRICE_RE.search(l).group() for l in lines if PRICE_RE.search(l)]
    if len(prices) > 1:
        price = min(prices, key=lambda p: int(re.sub(r"\D", "", p.split("-")[0]) or 10**9))
    rating = next((m.group(1).replace(",", ".") for l in lines if len(l) <= 4
                   for m in [RATING_RE.fullmatch(l)] if m), None)
    nama = max((l for l in lines if not PRICE_RE.search(l) and len(l) > 8), key=len, default=None)
    return nama, price, rating


def scroll_all(page, rounds=12):
    last = 0
    for _ in range(rounds):
        page.mouse.wheel(0, 2500)
        time.sleep(random.uniform(1.0, 2.0))
        h = page.evaluate("document.body.scrollHeight")
        if h == last:
            break
        last = h


def scrape_shop(ctx, site: str, brand: str, url: str) -> list[dict]:
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(4)
    scroll_all(page)
    rows, seen = [], set()
    for a in page.query_selector_all(LINK_SELECTOR[site]):
        href = a.get_attribute("href") or ""
        if href in seen or len(href) < 30:
            continue
        txt = a.inner_text()
        nama, harga, rating = parse_card(txt)
        if nama and harga:
            seen.add(href)
            rows.append({"brand": brand, "nama_produk": nama, "harga": harga, "rating": rating, "bahan_aktif": ""})
    page.close()
    print(f"  [{site}] {brand}: {len(rows)} produk")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", choices=["shopee", "tokopedia"], required=True)
    ap.add_argument("--brand", help="satu brand saja (default: semua)")
    ap.add_argument("--headed", action="store_true", help="tampilkan browser (wajib untuk login/captcha)")
    a = ap.parse_args()

    from playwright.sync_api import sync_playwright
    config.RAW.mkdir(parents=True, exist_ok=True)
    rows = []
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(str(config.ROOT / ".browser_profile"),
                                                   headless=not a.headed, user_agent=config.USER_AGENT.replace("SkincareResearchBot/1.0", "Chrome/124.0"),
                                                   locale="id-ID")
        for brand, src in config.BRANDS.items():
            if a.brand and brand.lower() != a.brand.lower():
                continue
            rows += scrape_shop(ctx, a.site, brand, src[a.site])
            time.sleep(random.uniform(*config.DELAY))
        ctx.close()
    out = config.RAW / f"{a.site}_official.csv"
    pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8-sig")
    print(f"-> {out} ({len(rows)} baris)")


if __name__ == "__main__":
    main()
