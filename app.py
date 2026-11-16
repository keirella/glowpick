import base64
import html
import io

import pandas as pd
import streamlit as st

import config as C
import engine as E
import smart
import storage
from style import CSS

st.set_page_config(page_title="GlowPick · SPK Skincare Lokal", page_icon="🧴", layout="wide", initial_sidebar_state="collapsed")
st.markdown(CSS, unsafe_allow_html=True)

LOGO_SVG = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 120'>
<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#F8A1C0'/><stop offset='.55' stop-color='#EC6B9C'/><stop offset='1' stop-color='#E0457B'/></linearGradient>
<linearGradient id='l' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#FBC3D8'/><stop offset='1' stop-color='#F8A1C0'/></linearGradient></defs>
<circle cx='60' cy='60' r='60' fill='url(#g)'/>
<circle cx='96' cy='24' r='20' fill='#fff' opacity='.12'/><circle cx='20' cy='100' r='26' fill='#fff' opacity='.10'/>
<rect x='55' y='20' width='10' height='20' rx='5' fill='#FFE3EE'/>
<rect x='50' y='38' width='20' height='11' rx='3' fill='#fff'/>
<rect x='40' y='48' width='40' height='54' rx='13' fill='#fff'/>
<rect x='47' y='62' width='26' height='26' rx='9' fill='url(#l)'/>
<path d='M60 66 C55 73 54 76 60 82 C66 76 65 73 60 66Z' fill='#fff'/>
<path d='M92 56 l2.4 6 6 2.4 -6 2.4 -2.4 6 -2.4 -6 -6 -2.4 6 -2.4z' fill='#fff'/>
<path d='M26 38 l1.8 4.5 4.5 1.8 -4.5 1.8 -1.8 4.5 -1.8 -4.5 -4.5 -1.8 4.5 -1.8z' fill='#fff' opacity='.9'/>
</svg>"""
LOGO_URI = "data:image/svg+xml;base64," + base64.b64encode(LOGO_SVG.encode()).decode()

TYPE_STYLE = {
    "Facial Wash": ("🫧", "linear-gradient(135deg,#FFE3EE,#F9B4CE)"), "Toner": ("💧", "linear-gradient(135deg,#FFE9F1,#F7A8C6)"),
    "Serum": ("🧪", "linear-gradient(135deg,#FFDDEA,#F29AB9)"), "Moisturizer": ("🧴", "linear-gradient(135deg,#FFEDF4,#F8BBD3)"),
    "Sunscreen": ("☀️", "linear-gradient(135deg,#FFE6EF,#F5A3C1)"), "Masker": ("🎭", "linear-gradient(135deg,#FFEAF3,#F4A9C7)"),
}

WEIGHT_LABELS = {
    "harga": {1: "Harga tidak jadi soal", 2: "Sedikit memperhatikan harga", 3: "Harga cukup penting",
              4: "Penting, cari yang terjangkau", 5: "Wajib semurah mungkin"},
    "rating": {1: "Rating tidak terlalu penting", 2: "Sedikit melihat rating", 3: "Rating cukup penting",
               4: "Penting, cari yang rating tinggi", 5: "Wajib rating tertinggi"},
    "bahan_aktif": {1: "Bahan aktif tidak terlalu penting", 2: "Sedikit melihat bahan aktif", 3: "Bahan aktif cukup penting",
                    4: "Penting, cari bahan aktif yang pas", 5: "Wajib bahan aktif yang paling cocok"},
}
WEIGHT_QUESTIONS = [
    ("harga", "💸", "Seberapa penting harga yang terjangkau (semakin murah semakin baik) bagimu?"),
    ("rating", "⭐", "Seberapa penting rating produk yang tinggi dari pengguna lain bagimu?"),
    ("bahan_aktif", "🧬", "Seberapa penting produk punya bahan aktif yang cocok dengan jenis kulit & masalah kulitmu?"),
]

# Helper

def check_group(options: dict, prefix: str, selected, ncols: int = 4) -> list:
    """Kelompok checkbox (boleh pilih lebih dari satu). Mengembalikan daftar kunci yang dicentang."""
    chosen, cols = [], st.columns(ncols)
    for i, (key, label) in enumerate(options.items()):
        if cols[i % ncols].checkbox(label, value=(key in selected), key=f"{prefix}_{key}"):
            chosen.append(key)
    return chosen

def h(s: str) -> str:
    return " ".join(line.strip() for line in s.splitlines() if line.strip())

def rupiah(x: float) -> str:
    return "Rp " + f"{int(round(x / 100.0) * 100):,}".replace(",", ".")

def esc(x) -> str:
    return html.escape(str(x), quote=True)

@st.cache_data(show_spinner=False)
def _load(_version: float) -> pd.DataFrame:
    return E.load_data()

def get_data():
    if not C.BERSIH_PATH.exists():
        return None
    return _load(C.BERSIH_PATH.stat().st_mtime)      # cache otomatis dibuang bila produk_bersih.csv berubah

def go(page: str):
    st.session_state.page = page

def navbar(show_back: bool = False):
    with st.container(key="navbar"):
        c1, c2 = st.columns([6, 2], vertical_alignment="center")
        c1.markdown(h(f"""<div class='brand'><img src='{LOGO_URI}'/>
            <div><b>GlowPick</b><small>SPK Base Skincare Lokal</small></div></div>"""), unsafe_allow_html=True)
        if show_back:
            c2.button("← Ubah kriteria", key="back", on_click=go, args=("home",), use_container_width=True)

def sec_head(num: str, title: str, caption: str, cls: str = ""):
    st.markdown(h(f"""<div class='sec-head'><div class='sec-num {cls}'>{num}</div><div class='sec-title'>{title}</div></div>
        <div class='sec-cap'>{caption}</div>"""), unsafe_allow_html=True)

# Splash Screen  

def page_splash():
    with st.container(key="splash_card"):
        st.markdown(h(f"""<div class='logo-ring'><img src='{LOGO_URI}' alt='logo'/></div>
            <div class='login-title'>Selamat Datang</div>
            <div class='login-sub'>Sistem Pendukung Keputusan Pemilihan Produk Base Skincare Lokal</div>"""), unsafe_allow_html=True)
        st.button("Mulai", key="start", type="primary", use_container_width=True, on_click=go, args=("home",))

# Halaman Utama 

def open_history(rid: str):
    loaded = storage.load(rid)
    if loaded:
        inputs, ranked, info = loaded
        st.session_state.loaded = (inputs, ranked, info)
        st.session_state.inputs = inputs
        st.session_state.saved_id = rid
        st.session_state.page = "results"

def form(saved: dict):
    st.markdown(h("""<div class='hero'><h1>Temukan base skincare lokal yang <span>pas untuk kulitmu</span></h1>
        <p>Isi profil kulit, budget, dan prioritasmu. Sistem menyaring produk dengan Content-Based Filtering (TF-IDF &amp; cosine similarity),
        lalu memeringkat kandidatnya dengan SMART sesuai bobot yang kamu tentukan.</p></div>"""), unsafe_allow_html=True)

    with st.container(key="card_produk"):
        sec_head("1", "Cari jenis produk", "Ketik atau pilih jenis base skincare yang kamu butuhkan.")
        ptype = st.selectbox("Jenis produk", C.PRODUCT_TYPES,
                             index=(C.PRODUCT_TYPES.index(saved["ptype"]) if saved.get("ptype") in C.PRODUCT_TYPES else None),
                             placeholder="🔍  Cari jenis produk, mis. Serum, Sunscreen…", label_visibility="collapsed")

    with st.container(key="card_profil"):
        sec_head("2", "Profil kulit & preferensi produk", "Centang semua yang sesuai (boleh lebih dari satu). Bagian ini diproses dengan Content-Based Filtering.", "t")
        st.markdown("<div class='sub-label'>Jenis kulit <small>(wajib, minimal satu)</small></div>", unsafe_allow_html=True)
        skin = check_group(C.SKIN_OPTIONS, "skin", saved.get("skin", []), 4)
        st.markdown("<div class='sub-label'>Masalah kulit <small>(wajib, minimal satu)</small></div>", unsafe_allow_html=True)
        concern = check_group(C.CONCERN_OPTIONS, "concern", saved.get("concern", []), 4)
        st.markdown("<div class='sub-label'>Tekstur produk <small>(opsional)</small></div>", unsafe_allow_html=True)
        tex = check_group(C.TEXTURE_OPTIONS, "tex", saved.get("tex", []), 4)

    with st.container(key="card_budget"):
        sec_head("3", "Budget maksimal", "Produk dengan harga di atas budget tidak akan ditampilkan (penyaringan CBF).", "a")
        budget = st.number_input("Budget maksimal (Rp)", min_value=10000, max_value=2000000, step=5000,
                                 value=int(saved.get("budget", 100000)), format="%d", label_visibility="collapsed", key="in_budget")

    with st.container(key="card_bobot"):
        sec_head("4", "Seberapa penting tiap hal buatmu?", "Beri bobot 1-5 (1 = kurang penting, 5 = sangat penting). Bagian ini diproses dengan metode SMART.", "a")
        weights, cols = {}, st.columns(3)
        for col, (key, ico, q) in zip(cols, WEIGHT_QUESTIONS):
            with col, st.container(key=f"wcard_{key}"):
                st.markdown(f"<div class='w-ico'>{ico}</div><div class='w-q'>{q}</div>", unsafe_allow_html=True)
                weights[key] = st.select_slider(q, options=[1, 2, 3, 4, 5], value=saved.get("w", {}).get(key, 3),
                                                label_visibility="collapsed", key=f"in_w_{key}")
                st.markdown(f"<div class='w-hint'><b>{weights[key]}</b> · {WEIGHT_LABELS[key][weights[key]]}</div>", unsafe_allow_html=True)

    err = st.session_state.pop("form_error", None)
    if err:
        st.markdown(f"<div class='err'>⚠️ {err}</div>", unsafe_allow_html=True)

    if st.button("✨  Cari rekomendasi produk", type="primary", use_container_width=True, key="submit"):
        if not ptype:
            st.session_state.form_error = "Pilih jenis produk dulu di bagian 1."
        elif not skin:
            st.session_state.form_error = "Pilih minimal satu jenis kulit di bagian 2."
        elif not concern:
            st.session_state.form_error = "Pilih minimal satu masalah kulit di bagian 2."
        else:
            st.session_state.inputs = dict(ptype=ptype, skin=list(skin), tex=list(tex), concern=list(concern),
                                           budget=int(budget), w=dict(weights))
            st.session_state.pop("loaded", None)
            st.session_state.pop("saved_id", None)
            st.session_state.show_n = 10
            st.session_state.page = "results"
        st.rerun()

def history_panel(hist: pd.DataFrame):
    st.markdown("<div class='sec-title' style='margin:.3rem 0 .6rem'>🕘 Riwayat hasil</div>", unsafe_allow_html=True)
    for r in hist.head(8).itertuples():
        st.markdown(f"<div class='hist-item'><b>{esc(r.jenis_produk)}</b><span>{esc(r.waktu)}</span></div>", unsafe_allow_html=True)
        c1, c2 = st.columns([3, 1])
        c1.button("Buka", key=f"open_{r.id}", on_click=open_history, args=(r.id,), use_container_width=True)
        if c2.button("🗑", key=f"del_{r.id}"):
            storage.delete(r.id); st.rerun()

def page_home():
    navbar()
    if get_data() is None:
        st.markdown("<div class='err'>Data produk belum tersedia. Hubungi pengelola sistem.</div>", unsafe_allow_html=True)
        return
    saved = st.session_state.get("inputs", {})
    hist = storage.list_history()
    if hist.empty:                                   # pengguna baru -> langsung formulir
        form(saved)
    else:                                            # sudah punya riwayat -> riwayat di samping formulir
        left, right = st.columns([2.3, 1])
        with left:
            form(saved)
        with right:
            history_panel(hist)

# Halaman Hasil 

def stars(r, est=False) -> str:
    if pd.isna(r):
        return "<b>Belum ada data</b>"
    return f"<b>★ {r:.1f}</b> / 5" + (" <span class='badge alt-badge'>estimasi</span>" if est else "")


def card_html(row, w) -> str:
    emoji, grad = TYPE_STYLE.get(row.jenis_produk, ("🧴", "linear-gradient(135deg,#FFEDF4,#F8BBD3)"))
    rank = int(row.peringkat)
    cls = {1: "top1", 2: "top2", 3: "top3"}.get(rank, "")
    tags = "".join([
        f"<span class='chip s'>{esc(row.jenis_kulit)}</span>" if str(row.jenis_kulit).strip() else "",
        f"<span class='chip t'>{esc(row.tekstur_produk)}</span>" if str(row.tekstur_produk).strip() else "",
        f"<span class='chip m'>{esc(row.masalah_kulit)}</span>" if str(row.masalah_kulit).strip() else ""])
    n = int(row.jumlah_bahan_cocok)
    bar = lambda name, v: f"<div class='bar'><span>{name}</span><i><em style='width:{v*100:.0f}%'></em></i></div>"
    detail = h(f"""<details><summary>Rincian nilai</summary><table>
        <tr><th>Komponen</th><th>Nilai</th><th>Bobot</th></tr>
        <tr><td>sim(u, p) - CBF</td><td>{row.sim:.4f}</td><td>-</td></tr>
        <tr><td>Utilitas harga (cost)</td><td>{row.u_harga:.4f}</td><td>{w['harga']:.4f}</td></tr>
        <tr><td>Utilitas rating (benefit)</td><td>{row.u_rating:.4f}</td><td>{w['rating']:.4f}</td></tr>
        <tr><td>Utilitas bahan aktif (benefit)</td><td>{row.u_bahan:.4f}</td><td>{w['bahan_aktif']:.4f}</td></tr>
        <tr><th>Skor akhir U<sub>i</sub></th><th>{row.smart:.4f}</th><th></th></tr></table></details>""")
    return h(f"""
    <div class='rec {cls}'>
      <div class='ava' style='--g:{grad}'><div class='rank'>#{rank}</div>{emoji}</div>
      <div>
        <div class='brand-tag'>{esc(row.brand)}</div>
        <div class='p-name'>{esc(row.nama_produk)}</div>
        <div>{tags}</div>
        <div class='mrow'>
          <span class='mi'>Harga <b>{rupiah(row.harga_num)}</b></span>
          <span class='mi'>Rating {stars(row.rating_num, bool(row.rating_estimasi))}</span>
          <span class='mi'>Bahan aktif sesuai <b>{n}</b></span>
        </div>
        <div class='detail'><b>Bahan aktif:</b> {esc(row.bahan_aktif) if str(row.bahan_aktif).strip() else '-'}</div>
        {detail}
      </div>
      <div class='score'>
        <div class='ring' style='--p:{row.smart*100:.0f}'><span>{row.smart*100:.0f}</span></div>
        <small>Skor akhir U<sub>i</sub> = {row.smart:.3f}</small>
        <div class='bars'>{bar('CBF', min(row.sim,1))}{bar('Harga', row.u_harga)}{bar('Rating', row.u_rating)}{bar('Bahan', row.u_bahan)}</div>
      </div>
    </div>""")


def page_results():
    inp = st.session_state.get("inputs")
    df = get_data()
    if not inp or df is None:
        go("home"); st.rerun()
    navbar(show_back=True)

    if "loaded" in st.session_state:                              # dibuka dari riwayat: tampilkan hasil tersimpan
        inp, ranked, info = st.session_state.loaded
        ranked = ranked.copy()
    else:
        ranked, info = E.recommend(df, inp["ptype"], inp["skin"], inp["tex"], inp["concern"], inp["budget"], inp["w"])
    w = info["weights"]

    chips = "".join(f"<span class='chip'>{esc(C.SKIN_OPTIONS[k])}</span>" for k in inp["skin"])
    chips += "".join(f"<span class='chip'>{esc(C.CONCERN_OPTIONS[k])}</span>" for k in inp["concern"])
    chips += "".join(f"<span class='chip'>{esc(C.TEXTURE_OPTIONS[k])}</span>" for k in inp["tex"])
    chips += f"<span class='chip'>Budget ≤ {rupiah(inp['budget'])}</span>"
    st.markdown(h(f"""<div class='summary'><h2>Rekomendasi {esc(inp['ptype'])} untukmu</h2>
        <p>{info['n_candidates']} dari {info['n_total']} produk lolos penyaringan CBF (sim ≥ {info['theta']:.2f} dan harga ≤ budget),
        lalu diperingkat dengan SMART. Bobot kepentinganmu: harga {w['harga']:.2f}, rating {w['rating']:.2f}, bahan aktif {w['bahan_aktif']:.2f}.</p>
        <div>{chips}</div></div>"""), unsafe_allow_html=True)

    # ---- tidak ada kandidat / hasil terbatas (θ TIDAK diturunkan otomatis)
    if info["n_candidates"] == 0:
        if info["n_pass_sim"] == 0:
            why = "Tidak ada produk yang cukup mirip dengan profilmu. Coba kurangi pilihan tekstur/masalah kulit atau ganti jenis produk."
        else:
            why = (f"{info['n_pass_sim']} produk cocok dengan profilmu, tetapi semuanya di atas budget. "
                   f"Harga termurah yang cocok: <b>{rupiah(info['min_price_pass'])}</b>.")
        st.markdown(f"<div class='empty'><b>Tidak ada rekomendasi.</b><br>{why}</div>", unsafe_allow_html=True)
        return
    if info["limited"]:
        st.markdown(h(f"""<div class='limited'>⚠️ <b>Hasil terbatas:</b> hanya {info['n_candidates']} produk memenuhi syarat
            (batas minimum {info['min_candidates']}). Ambang kemiripan θ = {info['theta']:.2f} tidak diturunkan otomatis agar produk yang tampil
            tetap sesuai profil. {f"{info['n_over_budget']} produk cocok disingkirkan karena melebihi budget." if info['n_over_budget'] else ""}
            Coba naikkan budget atau kurangi pilihan profil.</div>"""), unsafe_allow_html=True)

    show_n = min(st.session_state.get("show_n", 10), len(ranked))
    st.markdown(h("<div class='grid'>" + "".join(card_html(r, w) for r in ranked.head(show_n).itertuples()) + "</div>"),
                unsafe_allow_html=True)
    if show_n < len(ranked):
        st.write("")
        if st.button(f"Tampilkan {len(ranked) - show_n} produk lainnya", key="more"):
            st.session_state.show_n = len(ranked); st.rerun()

    # ---- simpan ke riwayat
    st.write("")
    saved_id = st.session_state.get("saved_id")
    c1, c2 = st.columns(2)
    if saved_id:
        c1.button("✅ Tersimpan di riwayat", disabled=True, use_container_width=True, key="saved_dis")
    elif c1.button("💾 Simpan hasil", use_container_width=True, key="save"):
        st.session_state.saved_id = storage.save(inp, ranked, info)
        st.toast("Hasil disimpan ke riwayat.", icon="✅"); st.rerun()
    c2.button("← Kembali ke halaman utama", use_container_width=True, key="back2", on_click=go, args=("home",))

    if ranked["rating_estimasi"].any():
        st.markdown("<div class='note'>ℹ️ Rating berlabel <b>estimasi</b> adalah nilai rata-rata hasil pengisian data (bukan rating asli), perlakukan sebagai perkiraan.</div>", unsafe_allow_html=True)
    if ranked["rating_num"].isna().any():
        st.markdown(f"<div class='note'>ℹ️ Produk tanpa rating diberi utilitas netral ({C.RATING_NETRAL}).</div>", unsafe_allow_html=True)

    with st.expander("📊 Tabel perhitungan CBF & SMART"):
        st.caption(f"θ = {info['theta']:.2f} · profil pengguna u = {{{', '.join(info['profile'])}}} · "
                   f"bobot (harga/rating/bahan) = {w['harga']:.4f} / {w['rating']:.4f} / {w['bahan_aktif']:.4f}")
        tbl = ranked[["peringkat", "brand", "nama_produk", "sim", "harga_num", "rating_num", "jumlah_bahan_cocok",
                      "u_harga", "u_rating", "u_bahan", "smart"]].copy()
        tbl.columns = ["Peringkat", "Merek", "Produk", "sim(u,p)", "Harga (Rp)", "Rating", "Bahan aktif sesuai",
                       "U Harga", "U Rating", "U Bahan", "Skor Ui"]
        st.dataframe(tbl.round(4), hide_index=True, use_container_width=True)
        buf = io.BytesIO(); tbl.round(4).to_excel(buf, index=False, sheet_name="Hasil")
        st.download_button("⬇️ Unduh hasil (Excel)", buf.getvalue(), "hasil_rekomendasi.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Router

st.session_state.setdefault("page", "splash")
{"splash": page_splash, "home": page_home, "results": page_results}[st.session_state.page]()
