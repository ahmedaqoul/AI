import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import base64
from pathlib import Path

# ─── Sayfa yapılandırması ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Tanker İstihbarat | Maritime AI",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_PATH = Path(__file__).parent / "best_ship_model.pt"
HERO_IMAGE = Path(__file__).parent / "assets" / "ocean_hero.jpg"

@st.cache_resource
def load_model():
    return YOLO(str(MODEL_PATH))

# ─── Risk eşlemesi (Türkçe + renk) ───────────────────────────────────────────
RISK_STYLES = {
    "Düşük": ("risk-low", "#22c55e"),
    "Orta": ("risk-med", "#eab308"),
    "Yüksek": ("risk-high", "#ef4444"),
    "Kritik": ("risk-crit", "#ff1744"),
}

TANKER_DATABASE = {
    "Aframax": {
        "risk": "Yüksek",
        "fuel": "Ham Petrol",
        "capacity": "500.000 - 800.000 varil",
    },
    "Suezmax": {
        "risk": "Yüksek",
        "fuel": "Ham Petrol",
        "capacity": "~1 milyon varil",
    },
    "VLCC": {
        "risk": "Kritik",
        "fuel": "Ham Petrol",
        "capacity": "~2 milyon varil",
    },
    "ULCC": {
        "risk": "Kritik",
        "fuel": "Ham Petrol",
        "capacity": "3+ milyon varil",
    },
}

def estimate_tanker_category(width: int, height: int) -> str:
    area = width * height
    if area < 3000:
        return "Aframax"
    if area < 15000:
        return "Suezmax"
    if area < 40000:
        return "VLCC"
    return "ULCC"

def risk_badge_html(risk: str) -> str:
    css_class, _ = RISK_STYLES.get(risk, ("risk-med", "#eab308"))
    return f'<span class="risk-badge {css_class}">{risk}</span>'

def inject_css(hero_b64: str | None = None) -> None:
    hero_bg = (
        f"url('data:image/jpeg;base64,{hero_b64}')"
        if hero_b64
        else "linear-gradient(135deg, #0a1628 0%, #001a33 50%, #000814 100%)"
    )
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Rajdhani:wght@400;600;700&display=swap');

        .stApp {{
            background: linear-gradient(180deg, #030712 0%, #0a1628 40%, #000814 100%);
            font-family: 'Rajdhani', sans-serif;
        }}

        #MainMenu, footer, header {{ visibility: hidden; }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0c1929 0%, #061018 100%);
            border-right: 1px solid rgba(0, 212, 255, 0.25);
            box-shadow: 4px 0 24px rgba(0, 180, 255, 0.08);
        }}
        [data-testid="stSidebar"] .stMarkdown h1 {{
            font-family: 'Orbitron', sans-serif;
            color: #00d4ff;
            text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
            font-size: 1.1rem;
            letter-spacing: 0.15em;
        }}

        .hero {{
            position: relative;
            padding: 4rem 2rem;
            border-radius: 16px;
            overflow: hidden;
            margin-bottom: 2rem;
            border: 1px solid rgba(0, 212, 255, 0.3);
            box-shadow: 0 0 40px rgba(0, 150, 255, 0.15), inset 0 0 80px rgba(0, 50, 100, 0.2);
        }}
        .hero::before {{
            content: '';
            position: absolute;
            inset: 0;
            background: {hero_bg} center/cover no-repeat;
            filter: blur(2px) brightness(0.35);
            z-index: 0;
        }}
        .hero::after {{
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(90deg, rgba(3,7,18,0.92) 0%, rgba(10,22,40,0.75) 50%, rgba(0,20,40,0.6) 100%);
            z-index: 1;
        }}
        .hero-content {{ position: relative; z-index: 2; }}
        .hero h1 {{
            font-family: 'Orbitron', sans-serif;
            font-size: clamp(1.6rem, 4vw, 2.4rem);
            color: #e0f7ff;
            text-shadow: 0 0 30px rgba(0, 212, 255, 0.6);
            margin-bottom: 0.5rem;
        }}
        .hero p {{
            color: #94a3b8;
            font-size: 1.15rem;
            max-width: 720px;
            line-height: 1.6;
        }}
        .hero-tag {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border: 1px solid #00d4ff;
            color: #00d4ff;
            border-radius: 4px;
            font-size: 0.75rem;
            letter-spacing: 0.2em;
            margin-bottom: 1rem;
            text-transform: uppercase;
        }}

        .intel-card {{
            background: rgba(12, 25, 45, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin: 0.75rem 0;
            transition: all 0.25s ease;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
        }}
        .intel-card:hover {{
            border-color: rgba(0, 212, 255, 0.55);
            box-shadow: 0 0 28px rgba(0, 212, 255, 0.2);
            transform: translateY(-2px);
        }}
        .intel-card h3 {{
            font-family: 'Orbitron', sans-serif;
            color: #00d4ff;
            font-size: 1rem;
            margin: 0 0 0.75rem 0;
        }}
        .intel-row {{
            display: flex;
            justify-content: space-between;
            padding: 0.35rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            color: #cbd5e1;
        }}
        .intel-row span:first-child {{ color: #64748b; }}

        .risk-badge {{
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.85rem;
        }}
        .risk-low {{ background: rgba(34,197,94,0.2); color: #22c55e; border: 1px solid #22c55e; }}
        .risk-med {{ background: rgba(234,179,8,0.2); color: #eab308; border: 1px solid #eab308; }}
        .risk-high {{ background: rgba(239,68,68,0.2); color: #ef4444; border: 1px solid #ef4444; }}
        .risk-crit {{
            background: rgba(255,23,68,0.25);
            color: #ff1744;
            border: 1px solid #ff1744;
            box-shadow: 0 0 12px rgba(255, 23, 68, 0.6);
        }}

        div[data-testid="stFileUploader"] {{
            background: rgba(8, 20, 38, 0.9);
            border: 2px dashed rgba(0, 212, 255, 0.4);
            border-radius: 12px;
            padding: 1.5rem;
        }}
        div[data-testid="stFileUploader"]:hover {{
            border-color: #00d4ff;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.15);
        }}

        .stButton > button {{
            background: linear-gradient(135deg, #0066aa 0%, #00d4ff 100%) !important;
            color: #030712 !important;
            font-family: 'Orbitron', sans-serif !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 8px !important;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.4) !important;
            transition: all 0.2s !important;
        }}
        .stButton > button:hover {{
            box-shadow: 0 0 32px rgba(0, 212, 255, 0.7) !important;
            transform: scale(1.02);
        }}

        .metric-panel {{
            background: rgba(12, 25, 45, 0.6);
            border: 1px solid rgba(0, 212, 255, 0.15);
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
        }}
        .metric-panel .val {{ color: #00d4ff; font-size: 1.5rem; font-weight: 700; }}
        .metric-panel .lbl {{ color: #64748b; font-size: 0.8rem; text-transform: uppercase; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def get_hero_b64() -> str | None:
    if HERO_IMAGE.exists():
        return base64.b64encode(HERO_IMAGE.read_bytes()).decode()
    return None

def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("# MARITIME OPS")
        st.caption("Naval Intelligence Console v2.0")
        st.divider()
        page = st.radio(
            "Navigasyon",
            [
                "Ana Sayfa",
                "AI Detection",
                "Proje Hakkında",
                "Sistem Durumu",
            ],
            label_visibility="collapsed",
        )
        st.divider()
        st.markdown(
            '<p style="color:#64748b;font-size:0.75rem;">YOLO · Satellite · Tanker</p>',
            unsafe_allow_html=True,
        )
    return page

def page_home():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-content">
                <span class="hero-tag">Satellite Intelligence · AI Detection</span>
                <h1>Yapay Zeka Destekli Tanker İstihbarat Sistemi</h1>
                <p>
                    Uydu görüntülerinden gerçek zamanlı gemi tespiti ve tanker sınıflandırması.
                    Denizcilik güvenliği ve enerji lojistiği için gelişmiş YOLO tabanlı analiz platformu.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            '<div class="metric-panel"><div class="val">YOLOv8</div><div class="lbl">Detection Engine</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="metric-panel"><div class="val">4</div><div class="lbl">Tanker Sınıfı</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            '<div class="metric-panel"><div class="val">AI</div><div class="lbl">Risk Analizi</div></div>',
            unsafe_allow_html=True,
        )
    if st.button("AI Detection Başlat →", use_container_width=True):
        st.session_state["page"] = "AI Detection"
        st.rerun()

def page_detection(model):
    st.markdown("## AI Detection")
    st.markdown(
        '<p style="color:#94a3b8;">Uydu veya deniz görüntüsü yükleyin. Sistem otomatik tanker tespiti ve istihbarat kartları üretir.</p>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Uydu Görüntüsü Yükle (JPG / PNG)",
        type=["jpg", "png", "jpeg"],
        help="Drag & drop veya dosya seçin",
    )

    if uploaded is None:
        st.info("Analiz için bir görüntü yükleyin.")
        return

    image = Image.open(uploaded)
    img = np.array(image)
    results = model(img)
    detections = []

    for box in results[0].boxes.xyxy:
        x1, y1, x2, y2 = map(int, box)
        w, h = x2 - x1, y2 - y1
        tanker_type = estimate_tanker_category(w, h)
        info = TANKER_DATABASE[tanker_type]
        detections.append((tanker_type, info, (x1, y1, x2, y2)))

        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 212, 255), 2)
        cv2.putText(
            img, tanker_type, (x1, y1 - 8),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2,
        )

    col_img, col_cards = st.columns([1.2, 1])
    with col_img:
        st.image(img, caption="Detection Result · Uydu Analizi", use_container_width=True)

    with col_cards:
        if not detections:
            st.warning("Tespit edilen tanker bulunamadı.")
            return
        for i, (ttype, info, _) in enumerate(detections, 1):
            st.markdown(
                f"""
                <div class="intel-card">
                    <h3>Tespit #{i} · {ttype}</h3>
                    <div class="intel-row"><span>Tanker Tipi</span><span>{ttype}</span></div>
                    <div class="intel-row"><span>Risk Seviyesi</span>{risk_badge_html(info['risk'])}</div>
                    <div class="intel-row"><span>Yakıt Türü</span><span>{info['fuel']}</span></div>
                    <div class="intel-row"><span>Kapasite</span><span>{info['capacity']}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

def page_about():
    st.markdown("## Proje Hakkında")
    st.markdown(
        """
        Bu platform, **uydu görüntüleri** üzerinde **YOLO** tabanlı gemi **Detection**
        ile tanker sınıflandırması ve **Intelligence** raporlama sunar.

        - Denizcilik gözetleme ve enerji nakliye analizi
        - Aframax, Suezmax, VLCC, ULCC kategorileri
        - Otomatik risk değerlendirmesi
        """
    )

def page_status():
    st.markdown("## Sistem Durumu")
    ok = MODEL_PATH.exists()
    st.markdown(
        f"""
        | Bileşen | Durum |
        |---------|--------|
        | YOLO Model | {'🟢 Aktif' if ok else '🔴 Model bulunamadı'} |
        | AI Pipeline | 🟢 Hazır |
        | Satellite Input | 🟢 Beklemede |
        """
    )

def main():
    hero_b64 = get_hero_b64()
    inject_css(hero_b64)

    if "page" not in st.session_state:
        st.session_state["page"] = None

    page = render_sidebar()
    if st.session_state.get("page"):
        page = st.session_state["page"]
        st.session_state["page"] = None

    if page == "Ana Sayfa":
        page_home()
    elif page == "AI Detection":
        model = load_model()
        page_detection(model)
    elif page == "Proje Hakkında":
        page_about()
    elif page == "Sistem Durumu":
        page_status()

if __name__ == "__main__":
    main()