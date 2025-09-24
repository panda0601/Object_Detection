import streamlit as st
import cv2
import tempfile
import os
from ultralytics import YOLO

# ==============================
# Streamlit Page Config
# ==============================
st.set_page_config(
    page_title="Smart Shelf Monitoring",
    page_icon="🛒",
    layout="wide"
)

# ==============================
# Custom CSS for Vibrant Modern UI
# ==============================
st.markdown("""
<style>
/* Background Gradient */
.stApp {
    background: linear-gradient(135deg, #ffecd2, #fcb69f); /* Peach to soft pink */
    font-family: 'Poppins', sans-serif;
    color: #1a1a1a; /* Dark text */
}

/* Main Title */
h1 {
    text-align: center;
    color: #1a1a1a;
    font-size: 48px !important;
    font-weight: bold;
    text-shadow: 2px 2px 8px rgba(255,255,255,0.5);
    margin-bottom: 20px;
}

/* Paragraphs & Text */
p, label, .stRadio label {
    color: #1a1a1a !important;
}

/* Card Style */
.card {
    background: linear-gradient(145deg, rgba(255,255,255,0.9), rgba(255,255,255,0.8));
    padding: 20px;
    border-radius: 25px;
    box-shadow: 0px 10px 25px rgba(0,0,0,0.15);
    margin-bottom: 20px;
    transition: transform 0.3s ease-in-out;
}
.card:hover {
    transform: translateY(-5px);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #ff7e5f, #feb47b);
    color: white;
    border: none;
    padding: 12px 25px;
    border-radius: 15px;
    font-size: 18px;
    font-weight: bold;
    transition: 0.3s ease-in-out;
    box-shadow: 0px 5px 15px rgba(255,126,95,0.4);
}
.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: 0px 8px 20px rgba(255,126,95,0.6);
    background: linear-gradient(90deg, #feb47b, #ff7e5f);
}

/* Fix Browse File Button */
[data-testid="stFileUploader"] button {
    background: linear-gradient(90deg, #ff7e5f, #feb47b) !important;
    color: white !important;
    border: none !important;
    padding: 12px 25px !important;
    border-radius: 12px !important;
    font-weight: bold !important;
    font-size: 16px !important;
    box-shadow: 0px 5px 15px rgba(255,126,95,0.4) !important;
    cursor: pointer !important;
}
[data-testid="stFileUploader"] button:hover {
    background: linear-gradient(90deg, #feb47b, #ff7e5f) !important;
    box-shadow: 0px 8px 20px rgba(255,126,95,0.6) !important;
}

/* Fix Camera Button */
[data-testid="stCameraInput"] button {
    background: linear-gradient(90deg, #ff7e5f, #feb47b) !important;
    color: white !important;
    border: none !important;
    padding: 12px 25px !important;
    border-radius: 12px !important;
    font-weight: bold !important;
    font-size: 16px !important;
    box-shadow: 0px 5px 15px rgba(255,126,95,0.4) !important;
    cursor: pointer !important;
}
[data-testid="stCameraInput"] button:hover {
    background: linear-gradient(90deg, #feb47b, #ff7e5f) !important;
    box-shadow: 0px 8px 20px rgba(255,126,95,0.6) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #ffecd2, #ffb199);
}
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] label, 
section[data-testid="stSidebar"] div {
    color: #1a1a1a !important;
    font-weight: bold;
}

/* Alerts */
.alert {
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    font-weight: bold;
    font-size: 16px;
}
.alert-success { background: linear-gradient(to right, #28a745, #85e085); color: white; }
.alert-warning { background: linear-gradient(to right, #ffc107, #ffec80); color: black; }
.alert-danger { background: linear-gradient(to right, #dc3545, #ff6b6b); color: white; }

/* Image Styling */
img {
    border-radius: 15px;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

# ==============================
# YOLO Model Load
# ==============================
import gdown

# Path where best.pt should be
MODEL_PATH = "best.pt"

# Google Drive file ID (replace with yours)
FILE_ID = "1LAR_IQRVWVFamowFUOkmgo8ccTs3W3Rm"
URL = f"https://drive.google.com/uc?id={FILE_ID}"

# Download if not exists
if not os.path.exists(MODEL_PATH):
    print("⏬ Downloading model...")
    gdown.download(URL, MODEL_PATH, quiet=False)

model = YOLO(MODEL_PATH)
# ==============================
# App Title
# ==============================
st.markdown("<h1>🛒 Smart Shelf Monitoring System</h1>", unsafe_allow_html=True)
st.write("<p style='text-align:center; font-size:18px; color:#1a1a1a;'>AI-powered shelf detection to monitor product availability in real-time</p>", unsafe_allow_html=True)

# ==============================
# Sidebar
# ==============================
st.sidebar.header("⚙️ Settings")
option = st.sidebar.radio("Select Input Method", ["Upload Image", "Capture from Camera"])
threshold = st.sidebar.slider("Stock Threshold", 1, 20, 5)

# ==============================
# Two Column Layout
# ==============================
col1, col2 = st.columns([1, 1])
img_source = None

# ==============================
# Input Section
# ==============================
with col1:
    st.markdown("<div class='card'><h3 style='text-align:center; color:#1a1a1a;'>📂 Input Section</h3>", unsafe_allow_html=True)
    
    if option == "Upload Image":
        uploaded_file = st.file_uploader("Upload a shelf image", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
                temp.write(uploaded_file.read())
                img_source = temp.name

    elif option == "Capture from Camera":
        camera_image = st.camera_input("Capture an image")
        if camera_image is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
                temp.write(camera_image.getbuffer())
                img_source = temp.name
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# Detection Results
# ==============================
with col2:
    st.markdown("<div class='card'><h3 style='text-align:center; color:#1a1a1a;'>🔍 Detection Results</h3>", unsafe_allow_html=True)
    if img_source:
        # Run YOLO detection
        results = model(img_source)
        output_img = results[0].plot()

        # Show detection image
        st.image(output_img, caption="Detected Products", use_column_width=True, channels="BGR")

        # Count products
        num_products = len(results[0].boxes)

        # Alerts based on count
        if num_products < threshold:
            st.markdown(f"<div class='alert alert-danger'>⚠️ ALERT: Only {num_products} products detected. Restock needed!</div>", unsafe_allow_html=True)
        elif num_products == threshold:
            st.markdown(f"<div class='alert alert-warning'>⚠️ Warning: Product stock is exactly at threshold ({threshold}).</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='alert alert-success'>✅ Stock level is sufficient: {num_products} products detected.</div>", unsafe_allow_html=True)

        os.remove(img_source)
    else:
        st.write("<p style='color:#1a1a1a;'>Upload or capture an image to see results.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# Footer
# ==============================
st.markdown("""
<hr style='border:1px solid #1a1a1a;'>
<p style='text-align:center; color:#1a1a1a; font-size:14px;'>
    ©️ 2025 Smart Shelf Monitoring | Built with ❤️ using Streamlit & YOLOv8
</p>
""", unsafe_allow_html=True)
