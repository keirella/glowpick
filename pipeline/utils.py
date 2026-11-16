from __future__ import annotations
import random, re, time, urllib.robotparser as rp
from urllib.parse import urlparse
import requests
import pconfig as config

_session = requests.Session()
_session.headers.update({"User-Agent": config.USER_AGENT, "Accept-Language": "id-ID,id;q=0.9,en;q=0.8"})
_robots: dict[str, rp.RobotFileParser] = {}


def allowed(url: str) -> bool:
    host = "{0.scheme}://{0.netloc}".format(urlparse(url))
    if host not in _robots:
        r = rp.RobotFileParser(host + "/robots.txt")
        try:
            r.read()
        except Exception:
            r = None
        _robots[host] = r
    r = _robots[host]
    return True if r is None else r.can_fetch(config.USER_AGENT, url)


def polite_get(url: str, **kw):
    if not allowed(url):
        print(f"  [robots.txt melarang] {url}")
        return None
    for attempt in range(3):
        time.sleep(random.uniform(*config.DELAY))
        try:
            r = _session.get(url, timeout=25, **kw)
            if r.status_code == 200:
                return r
            if r.status_code in (403, 429):
                time.sleep(5 * (attempt + 1))
        except requests.RequestException:
            time.sleep(3)
    return None


# teks
_EMOJI = re.compile("[\U0001F000-\U0001FFFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200d]+")


def clean_text(s) -> str:
    """Hapus emoji, simbol & tanda baca berlebih, rapikan spasi (3.7.2)."""
    if s is None or (isinstance(s, float) and s != s):
        return ""
    s = _EMOJI.sub(" ", str(s))
    s = re.sub(r"<[^>]+>", " ", s)                      # sisa tag HTML
    s = re.sub(r"[^\w\s%+\-/.,()&]", " ", s)
    s = re.sub(r"([!?.,])\1+", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def _has(text: str, words) -> bool:
    return any(w in text for w in words)


def classify_type(*texts) -> str | None:
    t = " ".join(texts).lower()
    for label, kws in config.TYPE_KEYWORDS:
        if _has(t, kws):
            return label
    return None


def extract_skin(text: str) -> str:
    t = text.lower()
    keys = [k for k, (_, ws) in config.SKIN_DICT.items() if _has(t, ws)]
    if "semua jenis kulit" in t or "all skin" in t or not keys:
        return "Semua jenis kulit"
    return ", ".join(config.SKIN_DICT[k][0] for k in keys)


def concern_keys(text: str) -> list[str]:
    t = text.lower()
    return [k for k, (_, ws) in config.CONCERN_DICT.items() if _has(t, ws)]


def extract_concern(text: str) -> str:
    keys = concern_keys(text)
    return ", ".join(config.CONCERN_DICT[k][0] for k in keys)


def extract_texture(text: str, jenis: str | None) -> str:
    t = text.lower()
    found = [lbl for lbl, ws in config.TEXTURE_DICT.items() if _has(t, ws)]
    if not found and jenis:
        found = [config.DEFAULT_TEXTURE.get(jenis, "")]
    return "/".join(f for f in found[:2] if f)


def extract_ingredients(text: str) -> str:
    m = re.search(r"(komposisi|ingredients?|kandungan)\s*[:\-]?\s*(.{20,1500})", text, flags=re.I | re.S)
    return clean_text(m.group(2)) if m else ""


def detect_actives(text: str):
    import re as _re
    t = text.lower()
    return [(name, tags) for pat, name, tags in config.ACTIVES if _re.search(pat, t)]
