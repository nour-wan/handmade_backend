 # vase_table_sim/ai_functions.py

import os
import cv2
import numpy as np
import io
from PIL import Image
from rembg import remove # تأكدي أن هذه المكتبة مثبتة في بيئة Django
from ultralytics import YOLO # تأكدي من تثبيت ultralytics

# تحميل نموذج YOLO مرة واحدة
_yolo_model = None

def load_yolo_model(model_path):
    """
    يحمل نموذج YOLO المدرب. يُستدعى مرة واحدة عند بدء التطبيق.
    """
    global _yolo_model
    if _yolo_model is None:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"YOLO model not found at {model_path}")
        _yolo_model = YOLO(model_path)
        print(f"تم تحميل نموذج YOLO من: {model_path}")
    return _yolo_model

def remove_background_from_image(image_bytes: bytes):
    """
    يقوم بإزالة الخلفية من الصورة المعطاة كـ bytes ويعيد الصورة الناتجة ككائن PIL Image.
    """
    input_buffer = io.BytesIO(image_bytes)
    input_buffer.seek(0)
    output_bytes = remove(input_buffer.read(), force_return_bytes=True)
    image_no_background = Image.open(io.BytesIO(output_bytes))
    return image_no_background

def add_vase_to_table(table_image_path, vase_image_no_bg_pil_image, yolo_model):
    """
    يقوم بدمج صورة فازة (مع خلفية شفافة) على صورة طاولة.
    table_image_path: مسار الصورة الأصلية للطاولة.
    vase_image_no_bg_pil_image: كائن PIL.Image للفازة بعد إزالة الخلفية.
    yolo_model: نموذج YOLO المُحمّل لاكتشاف الطاولة.
    """
    image = cv2.imread(table_image_path)
    if image is None:
        raise ValueError(f"تعذر قراءة صورة الطاولة من المسار: {table_image_path}")

    # تشغيل النموذج على صورة الطاولة لاكتشاف الطاولة
    results = yolo_model(image)

    table_box = None
    for result in results:
        boxes = result.boxes
        if len(boxes) == 0:
            continue
        # فرز الصناديق بناءً على الثقة وأخذ النتيجة الأعلى فقط (للتأكد من اختيار الطاولة)
        highest_confidence_box = max(boxes, key=lambda box: box.conf[0].item())
        table_box = highest_confidence_box.xywh[0].tolist()
        break # نأخذ أول طاولة مكتشفة بأعلى ثقة

    if table_box is None:
        raise ValueError("لم يتم اكتشاف طاولة في الصورة.")

    # x_center, y_center, width, height = map(int, table_box)
    highest_confidence_box = max(boxes, key=lambda box: box.conf[0].item())
    x_center, y_center, width, height = highest_confidence_box.xywh[0].tolist()
    x_center, y_center, width, height = int(x_center), int(y_center), int(width), int(height)

    # تحويل صورة الفازة إلى تنسيق OpenCV RGBA
    # vase = np.array(vase_image_no_bg_pil_image.convert("RGBA"))
    # vase = cv2.cvtColor(vase, cv2.COLOR_RGBA2BGRA)
    vase = cv2.imread(vase_image_no_bg_pil_image, cv2.IMREAD_UNCHANGED)
    
    # استخراج قناة alpha لتحديد أين تبدأ الفازة فعليًا
    alpha = vase[:, :, 3]
    rows = np.any(alpha != 0, axis=1)
    if not np.any(rows):
        raise ValueError("صورة الفازة بعد إزالة الخلفية فارغة أو شفافة بالكامل.")
    top = np.argmax(rows)
    bottom = len(rows) - np.argmax(rows[::-1])
    vase_cropped = vase[top:bottom, :, :]

    # إعادة تحجيم الفازة لتناسب حجم الطاولة
    new_width = width // 2
    scale_ratio = new_width / vase_cropped.shape[1]
    new_height = int(vase_cropped.shape[0] * scale_ratio)
    vase_resized = cv2.resize(vase_cropped, (new_width, new_height))

    # تحديد مكان الفازة بحيث قاعدتها تلامس سطح الطاولة
    x = int(x_center - new_width / 2)
    y = int(y_center - height / 2) - vase_resized.shape[0]+20

    # تأكد أن الفازة ضمن حدود الصورة
    if y < 0: y = 0
    if x < 0: x = 0
    if y + vase_resized.shape[0] > image.shape[0]:
        vase_resized = vase_resized[:image.shape[0] - y]
    if x + vase_resized.shape[1] > image.shape[1]:
        vase_resized = vase_resized[:, :image.shape[1] - x]

    # تحويل الصورة الأصلية إلى RGBA للدمج
    image_rgba = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    # دمج الفازة فوق الصورة الأصلية بناءً على الشفافية (alpha blending)
    roi_y_end = min(y + vase_resized.shape[0], image_rgba.shape[0])
    roi_x_end = min(x + vase_resized.shape[1], image_rgba.shape[1])

    roi = image_rgba[y:roi_y_end, x:roi_x_end]

    if roi.shape[0] != vase_resized.shape[0] or roi.shape[1] != vase_resized.shape[1]:
        vase_resized_cropped = vase_resized[:roi.shape[0], :roi.shape[1]]
    else:
        vase_resized_cropped = vase_resized

    alpha_channel = vase_resized_cropped[:, :, 3] / 255.0
    alpha_rgb = np.stack([alpha_channel, alpha_channel, alpha_channel, np.ones_like(alpha_channel)], axis=2)

    image_rgba[y:roi_y_end, x:roi_x_end] = roi * (1 - alpha_rgb) + vase_resized_cropped * alpha_rgb

    # تحويل الناتج إلى BGR للحفظ
    output_image = cv2.cvtColor(image_rgba, cv2.COLOR_BGRA2BGR)
    return output_image


