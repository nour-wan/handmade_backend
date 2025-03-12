import gdown
import os
from ultralytics import YOLO

MODEL_URL = "https://drive.google.com/uc?id=1EH9H4lZ4yKXnLY7g4ThBK7-6kF2kNEtO"
# MODEL_PATH = "ml_model/best.pt"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml_model", "best.pt")
print("@@@@@@@@@@@@@@@@@@@")
print(MODEL_PATH)

if not os.path.exists(MODEL_PATH):
    print("Downloading model from Google Drive...")
    gdown.download(MODEL_URL, MODEL_PATH, quiet=False)

# model = torch.load(MODEL_PATH, map_location="cpu")

try:
    model = YOLO(MODEL_PATH)
    print("تم تحميل النموذج بنجاح!")
except Exception as e:
    print(f"خطأ أثناء تحميل النموذج: {e}")