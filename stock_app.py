import streamlit as st
import cv2
import tempfile
import os
from ultralytics import YOLO
from twilio.rest import Client
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time
import json
from streamlit_autorefresh import st_autorefresh

# ==============================
# Twilio Setup (from Streamlit Secrets)
# ==============================
account_sid = st.secrets["twilio"]["account_sid"]
auth_token = st.secrets["twilio"]["auth_token"]
twilio_number = st.secrets["twilio"]["from_number"]
target_number = st.secrets["twilio"]["to_number"]
client = Client(account_sid, auth_token)

def send_sms_alert(stock_count):
    message = client.messages.create(
        body=f"⚠️ Smart Shelf Alert: Only {stock_count} products left. Restock needed!",
        from_=twilio_number,
        to=target_number
    )
    print("✅ SMS sent:", message.sid)

# ==============================
# Google Sheets Setup (Streamlit Cloud Secure)
# ==============================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds_dict = json.loads(json.dumps(st.secrets["gcp_service_account"]))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gs_client = gspread.authorize(creds)
sheet = gs_client.open("SmartShelfLogs").sheet1

def ensure_headers():
    """Ensure headers exist in sheet: time, count"""
    first_row = sheet.row_values(1)
    if not first_row or first_row[0].lower() != "time":
        sheet.insert_row(["time", "count"], 1)

def log_to_gsheet(count):
    ensure_headers()
    sheet.append_row([time.strftime("%Y-%m-%d %H:%M:%S"), count])
    print(f"✅ Logged {count} to Google Sheets")

@st.cache_data(ttl=8)
def get_df():
    """Fetch logs from Google Sheets and return DataFrame"""
    values = sheet.get_all_values()
    if not values:
        return pd.DataFrame(columns=["time", "count"])

    header = [h.strip().lower() for h in values[0]]
    if "time" in header and "count" in header:
        df = pd.DataFrame(values[1:], columns=header)
    else:
        df = pd.DataFrame(values, columns=["time", "count"][:len(values[0])])

    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
    if "count" in df.columns:
        df["count"] = pd.to_numeric(df["count"], errors="coerce")

    df = df.dropna(subset=["time", "count"]).sort_values("time")
    return df

# ==============================
# Streamlit Page Config
# ==============================
st.set_page_config(page_title="Smart Shelf Monitoring", page_icon="🛒", layout="wide")

# ==============================
# Sidebar Navigation
# ==============================
st.sidebar.header("⚙️ Settings")
page = st.sidebar.radio("Select Page", ["Detection", "Dashboard"])
threshold = st.sidebar.slider("Stock Threshold", 1, 20, 5)

# ==============================
# Custom CSS (Your Original Style)
# ==============================
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #ffecd2, #fcb69f); font-family: 'Poppins', sans-serif; color: #1a1a1a; }
h1 { text-align: center; color: #1a1a1a; font-size: 48px !important; font-weight: bold; text-shadow: 2px 2px 8px rgba(255,255,255,0.5); margin-bottom: 20px; }
p, label, .stRadio label { color: #1a1a1a !important; }
.card { background: linear-gradient(145deg, rgba(255,255,255,0.9), rgba(255,255,255,0.8)); padding: 20px; border-radius: 25px; box-shadow: 0px 10px 25px rgba(0,0,0,0.15); margin-bottom: 20px; transition: transform 0.3s ease-in-out; }
.card:hover { transform: translateY(-5px); }
.stButton>button { background: linear-gradient(90deg, #ff7e5f, #feb47b); color: white; border: none; padding: 12px 25px; border-radius: 15px; font-size: 18px; font-weight: bold; transition: 0.3s ease-in-out; box-shadow: 0px 5px 15px rgba(255,126,95,0.4); }
.stButton>button:hover { transform: translateY(-3px); box-shadow: 0px 8px 20px rgba(255,126,95,0.6); background: linear-gradient(90deg, #feb47b, #ff7e5f); }
[data-testid="stFileUploader"] button, [data-testid="stCameraInput"] button { background: linear-gradient(90deg, #ff7e5f, #feb47b) !important; color: white !important; border: none !important; padding: 12px 25px !important; border-radius: 12px !important; font-weight: bold !important; font-size: 16px !important; box-shadow: 0px 5px 15px rgba(255,126,95,0.4) !important; cursor: pointer !important; }
[data-testid="stFileUploader"] button:hover, [data-testid="stCameraInput"] button:hover { background: linear-gradient(90deg, #feb47b, #ff7e5f) !important; box-shadow: 0px 8px 20px rgba(255,126,95,0.6) !important; }
section[data-testid="stSidebar"] { background: linear-gradient(to bottom, #ffecd2, #ffb199); }
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] div { color: #1a1a1a !important; font-weight: bold; }
.alert { padding: 15px; border-radius: 12px; text-align: center; font-weight: bold; font-size: 16px; }
.alert-success { background: linear-gradient(to right, #28a745, #85e085); color: white; }
.alert-warning { background: linear-gradient(to right, #ffc107, #ffec80); color: black; }
.alert-danger { background: linear-gradient(to right, #dc3545, #ff6b6b); color: white; }
img { border-radius: 15px; box-shadow: 0px 8px 20px rgba(0,0,0,0.2); }
</style>
""", unsafe_allow_html=True)

# ==============================
# YOLO Model Load
# ==============================
model = YOLO("best.pt")  # Ensure best.pt is uploaded with your app or model path updated

# ==============================
# Detection Page
# ==============================
if page == "Detection":
    st.markdown("<h1>🛒 Smart Shelf Monitoring System</h1>", unsafe_allow_html=True)
    st.write("<p style='text-align:center; font-size:18px; color:#1a1a1a;'>AI-powered shelf detection to monitor product availability in real-time</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    img_source = None

    with col1:
        st.markdown("<div class='card'><h3 style='text-align:center; color:#1a1a1a;'>📂 Input Section</h3>", unsafe_allow_html=True)
        option = st.radio("Select Input Method", ["Upload Image", "Capture from Camera"])
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

    with col2:
        st.markdown("<div class='card'><h3 style='text-align:center; color:#1a1a1a;'>🔍 Detection Results</h3>", unsafe_allow_html=True)
        if img_source:
            results = model(img_source)
            output_img = results[0].plot()
            st.image(output_img, caption="Detected Products", use_container_width=True, channels="BGR")

            num_products = len(results[0].boxes)

            if num_products < threshold:
                st.markdown(f"<div class='alert alert-danger'>⚠️ ALERT: Only {num_products} products detected. Restock needed!</div>", unsafe_allow_html=True)
                try:
                    send_sms_alert(num_products)
                    st.write("✅ SMS alert triggered.")
                except Exception as e:
                    st.write(f"❌ SMS alert error: {e}")
            elif num_products == threshold:
                st.markdown(f"<div class='alert alert-warning'>⚠️ Warning: Stock is exactly at threshold ({threshold}).</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='alert alert-success'>✅ Stock is sufficient: {num_products} products detected.</div>", unsafe_allow_html=True)

            try:
                log_to_gsheet(num_products)
            except Exception as e:
                st.write(f"❌ GSheet logging error: {e}")

            os.remove(img_source)
        else:
            st.write("<p style='color:#1a1a1a;'>Upload or capture an image to see results.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# Dashboard Page
# ==============================
elif page == "Dashboard":
    st.markdown("<h1>📊 Stock Monitoring Dashboard</h1>", unsafe_allow_html=True)

    st_autorefresh(interval=10000, key="datarefresh")

    if st.button("🔄 Refresh Now"):
        st.cache_data.clear()

    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        if not df.empty:
            if "time" not in df.columns or "count" not in df.columns:
                st.warning("⚠️ Please make sure your Google Sheet has headers: time | count")
            else:
                st.markdown("### 📝 Logged Stock Data")
                st.dataframe(df)

                st.markdown("### 📈 Stock Level Trend")
                df["time"] = pd.to_datetime(df["time"])
                st.line_chart(df.set_index("time")["count"])

                st.markdown("### 📊 Stock Summary")
                st.bar_chart(df.set_index("time")["count"])

                last_update = df["time"].max()
                st.caption(f"🕒 Last Updated: {last_update}")
        else:
            st.info("ℹ️ No stock data logged yet. Run a detection first.")
    except Exception as e:
        st.error(f"❌ Error fetching data from Google Sheets: {e}")

# ==============================
# Footer
# ==============================
st.markdown("""
<hr style='border:1px solid #1a1a1a;'>
<p style='text-align:center; color:#1a1a1a; font-size:14px;'>
    ©️ 2025 Smart Shelf Monitoring | Built with ❤️ using Streamlit, YOLOv8, Twilio & Google Sheets
</p>
""", unsafe_allow_html=True)
