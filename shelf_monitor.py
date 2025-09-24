import cv2
from ultralytics import YOLO
import matplotlib.pyplot as plt
import os

# Load model
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
def detect_from_image(img_path):
    """Run YOLO detection on an uploaded image"""
    if not os.path.exists(img_path):
        print("⚠️ File not found.")
        return

    results = model(img_path)
    output_img = results[0].plot()

    # Show detections
    plt.figure(figsize=(10, 10))
    plt.imshow(cv2.cvtColor(output_img, cv2.COLOR_BGR2RGB))
    plt.axis("off")
    plt.show()

    # Count products
    num_products = len(results[0].boxes)
    print(f"🛒 Detected Products: {num_products}")

    # Stock alert
    threshold = 5
    if num_products < threshold:
        print("⚠️ ALERT: Restock needed!")
    else:
        print("✅ Stock level is sufficient")


def capture_and_detect():
    """Capture image from webcam and run YOLO detection"""
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("⚠️ Could not access webcam.")
        return

    print("📸 Press SPACE to capture image | Press ESC to exit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Press SPACE to capture | ESC to exit", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC to exit
            print("❌ Exiting without capture.")
            break
        elif key == 32:  # SPACE to capture
            img_path = "captured_image.jpg"
            cv2.imwrite(img_path, frame)
            print(f"✅ Image saved as {img_path}")
            cap.release()
            cv2.destroyAllWindows()

            # Run YOLO detection
            detect_from_image(img_path)
            return

    cap.release()
    cv2.destroyAllWindows()


# ---------- Main Menu ----------
while True:
    print("\n👉 Choose an option:")
    print("1. Upload an image for detection")
    print("2. Capture an image with camera")
    print("3. Exit")
    choice = input("Enter choice (1/2/3): ").strip()

    if choice == "1":
        path = input("Enter image file path: ").strip()
        detect_from_image(path)
    elif choice == "2":
        capture_and_detect()
    elif choice == "3":
        print("✅ Exiting program.")
        break
    else:
        print("⚠️ Invalid choice. Try again.")
