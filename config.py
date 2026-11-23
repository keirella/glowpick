from pathlib import Path

ROOT = Path(__file__).parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

PRODUCT_TYPES = ["Facial Wash", "Toner", "Serum", "Moisturizer", "Sunscreen"]

DATA = ROOT / "data"
BERSIH_PATH = PROCESSED / "produk_bersih.csv"       
RIWAYAT_PATH = DATA / "riwayat.csv"                 # riwayat hasil yang disimpan pengguna

THETA = 0.15            
MIN_CANDIDATES = 5      
SMART_MIN = 0.1        # produk dengan skor akhir SMART (Ui) di bawah ini tidak ditampilkan
RATING_NETRAL = 0.5     # utilitas rating bila rating produk kosong


SKIN_OPTIONS = {"normal": "Normal", "kering": "Kering", "berminyak": "Berminyak", "kombinasi": "Kombinasi",
                "sensitif": "Sensitif", "berjerawat": "Berjerawat", "dewasa": "Dewasa / Anti-aging"}
TEXTURE_OPTIONS = {"cair": "Cair / Essence", "gel": "Gel / Jelly", "foam": "Foam / Busa", "krim": "Krim / Cream",
                   "lotion": "Lotion"}
CONCERN_OPTIONS = {"jerawat": "Jerawat", "flek": "Bekas jerawat & flek", "komedo_pori": "Komedo & pori",
                   "minyak": "Minyak berlebih", "kusam": "Kusam", "dehidrasi": "Dehidrasi / kering",
                   "sensitif": "Kemerahan / sensitif", "barrier": "Skin barrier lemah", "penuaan": "Tanda penuaan",
                   "tekstur": "Tekstur kasar", "uv": "Proteksi UV & polusi"}
CORE_SKIN = ["normal", "kering", "berminyak", "kombinasi", "sensitif"]
