from __future__ import annotations
import pconfig as config


def _has(t: str, words) -> bool:
    return any(w in t for w in words)


def skin_tags(text) -> set[str]:
    t = str(text).lower()
    tags = set()
    if "normal" in t: tags.add("normal")
    if "kering" in t: tags.add("kering")
    if "berminyak" in t or "oily" in t: tags.add("berminyak")
    if "kombinasi" in t: tags.add("kombinasi")
    if "sensitif" in t: tags.add("sensitif")
    if "berjerawat" in t: tags.add("berjerawat")
    if _has(t, ["dewasa", "anti-aging", "anti aging", "penuaan"]): tags.add("dewasa")
    if "semua jenis" in t or not tags:          # tidak menyebut jenis kulit -> cocok untuk semua jenis inti
        tags.update(config.CORE_SKIN)
    return tags


def texture_tags(text) -> set[str]:
    t = str(text).lower()
    tags = set()
    if _has(t, ["cair", "essence", "serum", "watery", "liquid"]): tags.add("cair")
    if _has(t, ["gel", "jelly", "jeli"]): tags.add("gel")
    if _has(t, ["foam", "busa", "bubble", "mousse"]): tags.add("foam")
    if _has(t, ["krim", "cream"]): tags.add("krim")
    if _has(t, ["lotion", "losion", "milk"]): tags.add("lotion")
    return tags


def concern_tags(masalah, jenis_kulit="") -> set[str]:
    t, s = str(masalah).lower(), str(jenis_kulit).lower()
    tags: set[str] = set()

    def scan(txt: str, allowed: set[str] | None):
        def add(tag, cond):
            if cond and (allowed is None or tag in allowed):
                tags.add(tag)
        plain = txt.replace("bekas jerawat", " ")
        add("jerawat", "jerawat" in plain)
        add("flek", _has(txt, ["bekas jerawat", "flek", "hiperpigmentasi", "noda hitam", "tidak merata", "tak merata", "koreksi warna"]))
        add("komedo_pori", _has(txt, ["komedo", "pori"]))
        add("minyak", _has(txt, ["minyak", "sebum"]))
        add("kusam", _has(txt, ["kusam", "dullness"]))
        add("dehidrasi", _has(txt, ["dehidrasi", "hidrasi", "kering"]))
        add("sensitif", _has(txt, ["sensitif", "kemerahan", "iritasi"]))
        add("barrier", "barrier" in txt)
        add("penuaan", _has(txt, ["penuaan", "kerutan", "elastisitas"]))
        add("tekstur", _has(txt, ["tekstur", "sel kulit mati"]))
        add("uv", _has(txt, ["uv", "proteksi", "polusi", "polutan"]))

    scan(t, None)
    scan(s, {"kusam", "flek", "komedo_pori", "tekstur", "dehidrasi", "barrier"})   # kolom kulit kadang memuat masalah
    if "kemerahan" in s:
        tags.add("sensitif")
    return tags
