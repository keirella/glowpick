CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root{
  --accent:#E0457B; --accent2:#F06292; --ink:#3B1F2B; --muted:#8E6B79; --line:#F6D5E2; --soft:#FFF0F6; --soft2:#FDE4EE;
  --grad:linear-gradient(135deg,#F4739F 0%,#E0457B 100%);
  --grad2:linear-gradient(135deg,#F9A8C6 0%,#EC6B9C 100%);
}
.stApp, .stApp p, .stApp label, .stApp button, .stApp input, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp textarea{
  font-family:'Plus Jakarta Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
}
.stApp [data-testid="stMarkdownContainer"] *, .stApp button p, .stApp [data-testid="stSelectbox"] *{
  font-family:'Plus Jakarta Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
}
.st-key-login_card [data-testid="stMarkdownContainer"], .st-key-login_card [data-testid="stMarkdownContainer"] div{text-align:center}
.st-key-login_card [data-testid="stElementContainer"]{width:100%}
.stApp{ color:var(--ink); background:#FFF7FA; }
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stSidebar"], [data-testid="collapsedControl"]{display:none !important}
[data-testid="stMainBlockContainer"]{max-width:1080px; padding:1.2rem 1.4rem 4rem}

/* ---------- tombol ---------- */
.stButton > button, .stDownloadButton > button{
  border-radius:999px; font-weight:700; padding:.65rem 1.5rem; border:1.5px solid #F0BAD0;
  background:#fff; color:var(--ink);
  transition:transform .25s ease, box-shadow .25s ease, background .25s ease, color .25s ease, border-color .25s;
}
.stButton > button:hover, .stDownloadButton > button:hover{
  transform:translateY(-2px); border-color:var(--ink); background:#fff; color:var(--ink);
  box-shadow:0 10px 24px rgba(224,69,123,.12);
}
button[data-testid="stBaseButton-primary"]{
  background:var(--grad); color:#fff !important; border:none; font-size:1.05rem; padding:.85rem 1.6rem;
  box-shadow:0 10px 26px rgba(224,69,123,.25);
}
button[data-testid="stBaseButton-primary"] p{color:#fff !important}
button[data-testid="stBaseButton-primary"]:hover{
  background:#C2185B; color:#fff !important; transform:translateY(-3px) scale(1.025); box-shadow:0 16px 34px rgba(224,69,123,.35);
}
button[data-testid="stBaseButton-primary"]:active{transform:translateY(0) scale(.99)}

/* ---------- login ---------- */
.st-key-login_card{
  position:relative; overflow:hidden; width:min(470px,100%); margin:9vh auto 0; text-align:center;
  padding:2.8rem 2.4rem 2.6rem; border-radius:32px; background:#fff; border:1px solid var(--line);
  box-shadow:0 30px 70px rgba(224,69,123,.10);
  transition:transform .4s ease, box-shadow .4s ease;
}
.st-key-login_card::before{
  content:""; position:absolute; top:-10%; left:-90%; width:55%; height:120%; z-index:5; pointer-events:none;
  background:linear-gradient(105deg,transparent 0%,rgba(255,255,255,0) 20%,rgba(255,255,255,.95) 50%,rgba(255,255,255,0) 80%,transparent 100%);
  transform:skewX(-22deg);
}
.st-key-login_card:hover{transform:translateY(-6px); box-shadow:0 40px 90px rgba(224,69,123,.18)}
.st-key-login_card:hover::before{left:150%; transition:left 1.1s cubic-bezier(.4,.1,.2,1)}
.logo-ring{
  width:132px; height:132px; margin:0 auto 1.3rem; border-radius:50%; padding:5px;
  background:conic-gradient(from 200deg,#E0457B,#F8A1C0,#F6CADB,#EC6B9C,#E0457B);
  box-shadow:0 14px 34px rgba(224,69,123,.25); animation:float 5s ease-in-out infinite;
}
.logo-ring img{width:100%; height:100%; border-radius:50%; display:block; background:#fff; border:4px solid #fff}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
.login-title{font-size:2.1rem; font-weight:800; margin:.2rem 0 .35rem; color:var(--ink); letter-spacing:-.02em}
.login-sub{font-size:1.02rem; color:var(--muted); margin:0 auto 1.6rem; max-width:340px; line-height:1.55; font-weight:500}

/* ---------- navbar ---------- */
.st-key-navbar{
  background:#fff; border:1px solid var(--line); border-radius:26px; padding:1.1rem 1.4rem 1.1rem 1.4rem;
  box-shadow:0 8px 24px rgba(224,69,123,.06); margin-bottom:1.6rem; min-height:92px; overflow:visible;
}
.st-key-navbar [data-testid="stMarkdownContainer"], .st-key-navbar [data-testid="stElementContainer"]{overflow:visible}
.brand{display:flex; align-items:center; gap:.9rem; padding:.2rem 0}
.brand img{width:52px; height:52px; flex-shrink:0; border-radius:50%; box-shadow:0 4px 12px rgba(224,69,123,.25); border:2px solid #fff}
.brand b{font-size:1.2rem; font-weight:800; color:var(--ink); display:block; line-height:1.1}
.brand small{display:block; margin-top:.25rem; color:var(--muted); font-weight:500; font-size:.78rem; line-height:1.3}

/* ---------- hero & section ---------- */
.hero{padding:.4rem .2rem 1.2rem}
.hero h1{font-size:2.15rem; font-weight:800; letter-spacing:-.02em; margin:0 0 .3rem; line-height:1.2}
.hero h1 span{color:var(--muted)}
.hero p{color:var(--muted); font-size:1.02rem; margin:0; max-width:680px}
[class*="st-key-card_"]{
  background:#fff; border:1px solid var(--line); border-radius:26px;
  padding:1.4rem 1.6rem 1.5rem; box-shadow:0 10px 30px rgba(224,69,123,.05); margin-bottom:1.1rem;
  transition:box-shadow .3s ease;
}
[class*="st-key-card_"]:hover{box-shadow:0 16px 40px rgba(224,69,123,.10)}
.sec-head{display:flex; align-items:center; gap:.75rem; margin-bottom:.25rem}
.sec-num{width:34px; height:34px; border-radius:12px; display:grid; place-items:center; color:#fff; font-weight:800; background:var(--grad); box-shadow:0 6px 14px rgba(224,69,123,.25)}
.sec-num.t{background:var(--grad2)} .sec-num.a{background:linear-gradient(135deg,#F29AB9,#F28AB0)}
.sec-title{font-size:1.18rem; font-weight:800}
.sec-cap{color:var(--muted); font-size:.9rem; margin:0 0 .8rem 2.65rem}
.sub-label{font-weight:700; font-size:.92rem; margin:1rem 0 .35rem; color:var(--ink)}
.sub-label small{font-weight:500; color:var(--muted)}

/* selectbox pencarian */
[data-testid="stSelectbox"] [role="group"]{border-radius:16px !important; border:1.5px solid #F0BAD0 !important; background:#fff !important; min-height:54px; transition:box-shadow .2s, border-color .2s}
[data-testid="stSelectbox"] [role="group"]:hover{border-color:var(--ink) !important}
[data-testid="stSelectbox"] [role="group"]:focus-within{border-color:var(--ink) !important; box-shadow:0 0 0 4px rgba(224,69,123,.08)}
[data-testid="stSelectbox"] input{font-size:1rem; font-weight:500}

/* pills */
button[data-variant="pills"]{
  border-radius:999px !important; padding:.5rem 1.05rem !important; font-weight:600; transition:all .2s ease;
  background:#fff !important; border:1.5px solid #F0BAD0 !important; color:var(--ink) !important;
}
button[data-variant="pills"] *{color:inherit !important}
button[data-variant="pills"]:hover{border-color:var(--ink) !important; transform:translateY(-2px); box-shadow:0 8px 18px rgba(224,69,123,.12)}
button[data-variant="pills"][data-selected="true"], button[data-variant="pills"][aria-pressed="true"]{
  background:var(--ink) !important; color:#fff !important; border:1.5px solid var(--ink) !important; box-shadow:0 8px 18px rgba(224,69,123,.25)}
button[data-variant="pills"][aria-pressed="true"]:hover{color:#fff !important}

/* kartu bobot */
.w-q{font-weight:700; font-size:.98rem; line-height:1.4; margin:.1rem 0 .2rem}
.w-ico{font-size:1.6rem}
.w-hint{background:var(--c,#FFEDF4); border-radius:12px; padding:.45rem .7rem; font-size:.84rem; color:var(--ink); font-weight:500; margin-top:.2rem}
[class*="st-key-wcard_"]{background:#FFF9FB; border:1px solid var(--line); border-radius:20px; padding:1rem 1.1rem 1.15rem}

/* ---------- hasil ---------- */
.summary{
  border-radius:26px; padding:1.5rem 1.7rem; color:#fff; background:var(--grad);
  box-shadow:0 18px 44px rgba(224,69,123,.25); margin-bottom:1.2rem; position:relative; overflow:hidden;
}
.summary::after{content:""; position:absolute; right:-60px; top:-60px; width:220px; height:220px; border-radius:50%; background:rgba(255,255,255,.08)}
.summary h2{margin:0 0 .3rem; font-size:1.55rem; font-weight:800; color:#fff}
.summary p{margin:0 0 .8rem; opacity:.9}
.chip{display:inline-block; padding:.28rem .75rem; border-radius:999px; font-size:.8rem; font-weight:600; margin:0 .3rem .35rem 0}
.summary .chip{background:rgba(255,255,255,.18); color:#fff}
.chip.s{background:#FDE4EE; color:#6E1F3F} .chip.t{background:#F9D3E2; color:#8F2A52} .chip.m{background:#FFEDF4; color:#B03060}
.chip.b{background:#E0457B; color:#fff}
.sec-divider{margin:1.4rem 0 .8rem; font-weight:800; font-size:1.05rem; display:flex; align-items:center; gap:.6rem}
.sec-divider::after{content:""; flex:1; height:2px; background:linear-gradient(90deg,#F0BAD0,transparent)}
.grid{display:grid; grid-template-columns:1fr; gap:1rem}
.rec{
  position:relative; display:grid; grid-template-columns:auto 1fr auto; gap:1.1rem; align-items:center;
  background:#fff; border:1px solid var(--line); border-radius:24px; padding:1.1rem 1.4rem 1.1rem 1.1rem;
  box-shadow:0 10px 28px rgba(224,69,123,.06); transition:transform .3s ease, box-shadow .3s ease;
}
.rec:hover, .rec:focus-within{transform:translateY(-4px); box-shadow:0 18px 40px rgba(224,69,123,.14); z-index:5}
.rec::before{content:""; position:absolute; left:0; top:0; bottom:0; width:24px; border-radius:24px 0 0 24px; pointer-events:none;
  background:linear-gradient(90deg,var(--accent-bar,#F29AB9) 0 6px,transparent 6px)}
.rec.top1{--accent-bar:#E0457B} .rec.top2{--accent-bar:#F28AB0} .rec.top3{--accent-bar:#F7B2CB}
.rec.alt{background:#FFF9FB}
.ava{position:relative; width:84px; height:84px; border-radius:50%; display:grid; place-items:center; font-size:2.3rem; margin-left:.4rem; background:var(--g); box-shadow:0 10px 22px rgba(224,69,123,.14); border:4px solid #fff}
.rank{position:absolute; top:-6px; left:-8px; min-width:30px; height:30px; padding:0 .3rem; border-radius:999px; background:#C2386A; color:#fff; font-size:.82rem; font-weight:800; display:grid; place-items:center; border:2px solid #fff}
.top1 .rank{background:#E0457B} .top2 .rank{background:#F28AB0} .top3 .rank{background:#F7B2CB}
.brand-tag{font-size:.72rem; font-weight:800; letter-spacing:.12em; color:var(--muted); text-transform:uppercase}
.p-name{font-size:1.08rem; font-weight:800; line-height:1.3; margin:.1rem 0 .45rem}
.mrow{display:flex; flex-wrap:wrap; gap:.4rem .9rem; margin:.15rem 0 .5rem}
.mi{font-size:.84rem; color:var(--muted); font-weight:500} .mi b{color:var(--ink); font-weight:700}
.badge{display:inline-block; padding:.12rem .55rem; border-radius:999px; font-size:.75rem; font-weight:700}
.match0{background:#FDE4EE; color:#C2386A} .match1{background:#F3BDD3; color:#6E1F3F} .match2{background:#E0457B; color:#fff}
.alt-badge{background:#FBDDE9; color:#B03060}
.detail{font-size:.8rem; color:var(--muted); margin-top:.35rem; line-height:1.5}
.detail b{color:var(--ink)}
.score{position:relative; text-align:center; min-width:150px}
.ring{--p:0; width:92px; height:92px; border-radius:50%; margin:0 auto .35rem; display:grid; place-items:center;
  background:conic-gradient(#E0457B calc(var(--p)*1%), #FBDDE9 0)}
.ring span{width:72px; height:72px; border-radius:50%; background:#fff; display:grid; place-items:center; font-weight:800; font-size:1.25rem; color:var(--ink)}
.score small{display:block; color:var(--muted); font-size:.72rem; font-weight:600}
.bars{margin-top:.5rem; text-align:left}
.bar{display:flex; align-items:center; gap:.4rem; font-size:.68rem; color:var(--muted); font-weight:600; margin:.12rem 0}
.bar i{flex:1; height:6px; border-radius:99px; background:#FBDDE9; overflow:hidden; display:block}
.bar i em{display:block; height:100%; border-radius:99px; background:#EC6B9C}
.bar span{width:44px}
/* tooltip angka saat hover di batang pink */
.bar{position:relative; cursor:help}
.bar::after{content:attr(data-tip); position:absolute; right:0; bottom:calc(100% + 6px); white-space:nowrap; z-index:30;
  background:var(--ink); color:#fff; font-size:.72rem; font-weight:600; padding:.3rem .65rem; border-radius:8px;
  box-shadow:0 8px 20px rgba(59,31,43,.25); opacity:0; visibility:hidden; pointer-events:none; transform:translateY(4px);
  transition:opacity .15s ease, transform .15s ease, visibility .15s}
.bar:hover::after{opacity:1; visibility:visible; transform:translateY(0)}
.note{background:#fff; border:1px dashed #F29AB9; border-radius:16px; padding:.7rem 1rem; color:var(--muted); font-size:.86rem; margin:.5rem 0 1rem}
.err{background:#FFEDF4; border:1px solid #F0BAD0; border-radius:14px; padding:.7rem 1rem; color:#E0457B; font-weight:600; margin:.5rem 0}
@media (max-width:760px){
  .rec{grid-template-columns:1fr; text-align:left} .score{min-width:0; text-align:left} .ring{margin:0 0 .35rem}
  .hero h1{font-size:1.7rem}
  .bar::after{right:auto; left:0}
}
/* ---------- tambahan Bab 3 ---------- */
.rec details{margin-top:.55rem; font-size:.8rem}
.rec details summary{cursor:pointer; font-weight:700; color:var(--ink); list-style:none}
.rec details summary::before{content:"▸ "; color:var(--muted)} .rec details[open] summary::before{content:"▾ "}
.rec details table{border-collapse:collapse; margin-top:.4rem; width:100%; font-size:.78rem}
.rec details td, .rec details th{border-bottom:1px solid var(--line); padding:.25rem .5rem; text-align:left}
.rec details th{color:var(--muted); font-weight:600}
.limited{background:#FFF3E0; border:1px solid #F4C98B; border-radius:16px; padding:.75rem 1rem; color:#6B4A12; font-size:.88rem; margin:.6rem 0 1rem}
.empty{background:#fff; border:1px dashed #F29AB9; border-radius:20px; padding:1.4rem; text-align:center; color:var(--muted)}
.st-key-splash_card{position:relative; width:min(470px,100%); margin:14vh auto 0; text-align:center; padding:2.6rem 2.4rem; border-radius:32px; background:#fff; border:1px solid var(--line); box-shadow:0 30px 70px rgba(224,69,123,.10)}
.st-key-splash_card [data-testid="stMarkdownContainer"]{text-align:center}
.hist-item{border:1px solid var(--line); border-radius:16px; padding:.6rem .85rem; margin-bottom:.4rem; background:#FFF9FB; font-size:.85rem}
.hist-item b{display:block; font-size:.92rem}
.hist-item span{color:var(--muted)}
.w-chip{display:inline-block; background:#fff; border:1px solid var(--line); border-radius:12px; padding:.35rem .7rem; margin:.15rem .3rem .15rem 0; font-size:.82rem}
/* ---------- checkbox pilihan (CBF) ---------- */
[data-testid="stCheckbox"]{background:#fff; border:1.5px solid var(--line); border-radius:14px; padding:.4rem .75rem; margin-bottom:.45rem; transition:all .2s ease}
[data-testid="stCheckbox"]:hover{border-color:var(--accent); box-shadow:0 6px 16px rgba(224,69,123,.14); transform:translateY(-1px)}
[data-testid="stCheckbox"]:has(input:checked){background:var(--soft); border-color:var(--accent)}
[data-testid="stCheckbox"] label p{font-weight:600; font-size:.92rem; color:var(--ink)}
[data-testid="stNumberInput"] input{font-weight:600}
</style>
"""
