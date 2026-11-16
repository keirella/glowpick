import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import *   



USER_AGENT = "Mozilla/5.0 (compatible; SkincareResearchBot/1.0; riset skripsi; hanya data publik)"
USD_IDR = 16500               
DELAY = (1.5, 3.5)            

BRANDS = {
    "Wardah":    {"site": "https://wardahbeauty.com",
                  "shopee": "https://shopee.co.id/wardahofficial",
                  "tokopedia": "https://www.tokopedia.com/wardah-official"},
    "Emina":     {"site": "https://eminacosmetics.com",
                  "shopee": "https://shopee.co.id/eminaofficial",
                  "tokopedia": "https://www.tokopedia.com/emina-official"},
    "Somethinc": {"site": "https://somethinc.com",
                  "shopee": "https://shopee.co.id/somethinc",
                  "tokopedia": "https://www.tokopedia.com/somethinc"},
    "Erha":      {"site": "https://erhastore.co.id",
                  "shopee": "https://shopee.co.id/erhaofficialstore",
                  "tokopedia": "https://www.tokopedia.com/erhastore-official"},
    "Azarine":   {"site": "https://azarinecosmetic.com",
                  "shopee": "https://shopee.co.id/azarinecosmetic",
                  "tokopedia": "https://www.tokopedia.com/azarinecosmetics"},
}

TYPE_KEYWORDS = [
    ("Sunscreen",   ["sunscreen", "sun screen", "sunblock", "sun block", "sun protect", "spf", "uv shield", "sun serum", "sun gel"]),
    ("Masker",      ["mask", "masker", "sleeping pack", "clay pack"]),
    ("Serum",       ["serum", "ampoule", "booster", "spot gel", "spot treatment", "essence serum"]),
    ("Toner",       ["toner", "essence", "face mist", "exfoliating water", "tonic"]),
    ("Facial Wash", ["facial wash", "face wash", "cleanser", "cleansing", "facial foam", "face foam", "foaming", "wash", "micellar", "cleansing gel"]),
    ("Moisturizer", ["moisturizer", "moisturiser", "cream", "gel cream", "lotion", "pelembap", "barrier", "hydrating gel", "night cream", "day cream"]),
]

# ---------------------------------------------------------------- Kamus istilah baku (3.7.4)
# kunci baku -> (label tampil, kata-kata yang dikenali)
SKIN_DICT = {
    "normal":     ("Normal",     ["normal", "normal skin"]),
    "kering":     ("kering",     ["kering", "dry"]),
    "berminyak":  ("berminyak",  ["berminyak", "oily", "minyak"]),
    "kombinasi":  ("kombinasi",  ["kombinasi", "combination"]),
    "sensitif":   ("sensitif",   ["sensitif", "sensitive"]),
    "berjerawat": ("berjerawat", ["berjerawat", "acne prone", "acne-prone", "acne", "jerawat"]),
    "dewasa":     ("Dewasa / anti-aging", ["dewasa", "anti-aging", "anti aging", "antiaging", "penuaan", "mature"]),
}
CONCERN_DICT = {
    "jerawat":     ("Jerawat",               ["jerawat", "acne", "breakout", "blemish"]),
    "flek":        ("Bekas jerawat & flek",  ["bekas jerawat", "flek", "hiperpigmentasi", "hyperpigmentation", "dark spot", "noda hitam", "tidak merata", "uneven", "brightening", "mencerahkan", "whitening"]),
    "komedo_pori": ("Komedo & pori",         ["komedo", "pori", "pore", "blackhead", "whitehead"]),
    "minyak":      ("Minyak berlebih",       ["minyak berlebih", "oil control", "sebum", "shine", "berminyak", "oily"]),
    "kusam":       ("Kusam",                 ["kusam", "dull", "glowing", "radiance", "cerah"]),
    "dehidrasi":   ("Dehidrasi",             ["dehidrasi", "dehydrat", "hidrasi", "hydrat", "melembapkan", "moistur", "kulit kering"]),
    "sensitif":    ("Kemerahan / sensitif",  ["kemerahan", "redness", "iritasi", "irritat", "soothing", "menenangkan", "sensitif"]),
    "barrier":     ("Skin barrier lemah",    ["barrier", "skin barrier"]),
    "penuaan":     ("Tanda penuaan",         ["penuaan", "anti-aging", "anti aging", "kerutan", "wrinkle", "fine line", "elastisitas"]),
    "tekstur":     ("Tekstur kasar",         ["tekstur", "texture", "sel kulit mati", "eksfoliasi", "exfoliat", "bumpy"]),
    "uv":          ("Proteksi UV & polusi",  ["uv", "spf", "pa+", "polusi", "pollution", "sinar matahari"]),
}
TEXTURE_DICT = {
    "Cair":       ["cair", "essence", "watery", "liquid", "water-like", "air"],
    "Gel":        ["gel", "jelly", "jeli"],
    "Foam":       ["foam", "busa", "bubble", "mousse"],
    "Krim":       ["krim", "cream"],
    "Lotion":     ["lotion", "losion", "milk"],
    "Clay":       ["clay", "tanah liat", "mud"],
    "Sheet mask": ["sheet mask", "sheet", "peel-off", "peel off"],
}
DEFAULT_TEXTURE = {"Facial Wash": "Foam", "Toner": "Cair", "Serum": "Cair", "Moisturizer": "Cream",
                   "Sunscreen": "Lotion ringan", "Masker": "Clay"}

# bahan aktif -> masalah yang disasar
ACTIVES = [
    (r"niacinamide|vitamin b3|vit b3",                 "Niacinamide",       {"minyak", "komedo_pori", "kusam", "flek"}),
    (r"salicylic|bha\b|betaine salicylate",            "Salicylic Acid",    {"jerawat", "komedo_pori", "minyak", "tekstur"}),
    (r"hyaluronic|sodium hyaluronate",                 "Hyaluronic Acid",   {"dehidrasi"}),
    (r"ceramide",                                      "Ceramide",          {"barrier", "dehidrasi"}),
    (r"panthenol|vitamin b5|pentavitin",               "Panthenol",         {"barrier", "sensitif", "dehidrasi"}),
    (r"centella|cica|madecassoside|asiatic",           "Centella Asiatica", {"sensitif", "barrier", "jerawat"}),
    (r"retinol|retinal|bakuchiol",                     "Retinol",           {"penuaan", "jerawat", "tekstur"}),
    (r"peptide|peptida",                               "Peptide",           {"penuaan"}),
    (r"vitamin c|ascorb|ethyl ascorbic",               "Vitamin C",         {"kusam", "flek"}),
    (r"\baha\b|glycolic|lactic|mandelic|gluconolactone", "AHA",             {"kusam", "tekstur", "flek"}),
    (r"\bpha\b",                                       "PHA",               {"kusam", "tekstur"}),
    (r"zinc|zinc pca|zinc gluconate",                  "Zinc",              {"minyak", "jerawat"}),
    (r"tea tree|melaleuca",                            "Tea Tree",          {"jerawat"}),
    (r"witch hazel",                                   "Witch Hazel",       {"komedo_pori", "minyak"}),
    (r"alpha arbutin|arbutin",                         "Alpha Arbutin",     {"flek", "kusam"}),
    (r"tranexamic",                                    "Tranexamic Acid",   {"flek"}),
    (r"azelaic",                                       "Azelaic Acid",      {"jerawat", "flek"}),
    (r"aloe",                                          "Aloe Vera",         {"dehidrasi", "sensitif"}),
    (r"green tea|camellia sinensis",                   "Green Tea",         {"minyak", "sensitif"}),
    (r"licorice|glycyrrhiz",                           "Licorice",          {"kusam", "flek"}),
    (r"kaolin|bentonite|\bclay\b",                     "Clay",              {"minyak", "komedo_pori"}),
    (r"squalane|squalene",                             "Squalane",          {"dehidrasi", "barrier"}),
    (r"glycerin",                                      "Glycerin",          {"dehidrasi"}),
    (r"sulfur",                                        "Sulfur",            {"jerawat"}),
    (r"mugwort|artemisia",                             "Mugwort",           {"sensitif", "jerawat"}),
    (r"titanium dioxide|zinc oxide|uv filter|tinosorb|uvinul|octocrylene|avobenzone|ethylhexyl methoxycinnamate|homosalate|bemotrizinol",
                                                       "UV Filter",         {"uv"}),
    (r"vitamin e|tocopher",                            "Vitamin E",         {"penuaan", "barrier"}),
    (r"propolis|bee venom",                            "Propolis",          {"jerawat", "sensitif"}),
]

# Stopword 
STOPWORDS = set("""yang dan untuk dengan atau di ke dari pada dalam ini itu adalah juga serta agar bagi oleh
sebagai akan dapat bisa lebih sangat semua setiap nya the and for with of a an to in""".split())
KEEP_TERMS = {"kulit"}  


