import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image

# MODELİ YÜKLE
model = YOLO("best_ship_model.pt")

# SAYFA BAŞLIK
st.title("AI Maritime Tanker Intelligence System")

st.write(
    "Upload a satellite image for ship detection and tanker analysis."
)

# RESİM YÜKLEME
uploaded_file = st.file_uploader(
    "Upload Image",
    type=["jpg", "png", "jpeg"]
)

# TANKER DATABASE
tanker_database = {

    "Aframax": {
        "risk": "High",
        "fuel": "Crude Oil",
        "capacity": "500,000 - 800,000 barrels"
    },

    "Suezmax": {
        "risk": "Very High",
        "fuel": "Crude Oil",
        "capacity": "~1 million barrels"
    },

    "VLCC": {
        "risk": "Critical",
        "fuel": "Crude Oil",
        "capacity": "~2 million barrels"
    },

    "ULCC": {
        "risk": "Extreme",
        "fuel": "Crude Oil",
        "capacity": "3+ million barrels"
    }
}

# TANKER TAHMİNİ
def estimate_tanker_category(width, height):

    area = width * height

    if area < 3000:
        return "Aframax"

    elif area < 15000:
        return "Suezmax"

    elif area < 40000:
        return "VLCC"

    else:
        return "ULCC"

# RESİM GELDİYSE
if uploaded_file is not None:

    image = Image.open(uploaded_file)

    img = np.array(image)

    results = model(img)

    for box in results[0].boxes.xyxy:

        x1, y1, x2, y2 = map(int, box)

        width = x2 - x1
        height = y2 - y1

        tanker_type = estimate_tanker_category(
            width,
            height
        )

        tanker_info = tanker_database[tanker_type]

        # KUTU ÇİZ
        cv2.rectangle(
            img,
            (x1, y1),
            (x2, y2),
            (0,255,0),
            2
        )

        # YAZI
        cv2.putText(
            img,
            tanker_type,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,255,0),
            2
        )

        # BİLGİLER
        st.subheader("Detected Tanker Information")

        st.write(f"Type: {tanker_type}")
        st.write(f"Risk Level: {tanker_info['risk']}")
        st.write(f"Fuel Type: {tanker_info['fuel']}")
        st.write(f"Capacity: {tanker_info['capacity']}")

    st.image(img, caption="Detection Result")