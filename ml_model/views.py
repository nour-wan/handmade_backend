import cv2
import numpy as np
import io
from PIL import Image
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ultralytics import YOLO
import tempfile
import os
from django.conf import settings
from ultralytics import YOLO
import tempfile
import time

from rembg import remove
import matplotlib.pyplot as plt


# ✅ قائمة الامتدادات المدعومة
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png']


# ✅ التحقق من امتداد الملف
def is_allowed_file(filename):
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)


# ✅ تحميل النموذج مرة واحدة عند بدء السيرفر
model = None


def load_model():
    global model
    if model is None:
        model_path = os.path.join(settings.BASE_DIR, 'ml_model', 'best.pt')
        model = YOLO(model_path)


load_model()
def add_pillow_to_sofa_with_transparency(sofa_image_path, pillow_image_path, results):
    # قراءة صورة الوسادة وتطبيق إزالة الخلفية باستخدام rembg
    pillow_image = Image.open(pillow_image_path)

    # حفظ الصورة في ذاكرة الـ bytes
    input_buffer = io.BytesIO()
    pillow_image.save(input_buffer, format="PNG")
    input_buffer.seek(0)

    # تحويل محتويات input_buffer إلى bytes
    input_bytes = input_buffer.read()

    # تطبيق إزالة الخلفية باستخدام rembg مع force_return_bytes=True
    output_bytes = remove(input_bytes, force_return_bytes=True)

    # تحميل الصورة الناتجة من الـ bytes
    pillow_image_no_background = Image.open(io.BytesIO(output_bytes))

    # تحويل الصورة إلى تنسيق OpenCV
    pillow_image_no_background = pillow_image_no_background.convert("RGBA")
    pillow_image_no_background = np.array(pillow_image_no_background)
    pillow_image_no_background = cv2.cvtColor(pillow_image_no_background, cv2.COLOR_RGBA2BGRA)

    # استعراض نتائج التنبؤ (لكل كائن تم اكتشافه)
    for result in results:
        labels = result.boxes.cls  
        boxes = result.boxes.xyxy  # إحداثيات (x_min, y_min, x_max, y_max)
        confidences = result.boxes.conf  

        threshold = 0.5  
        # تصفية الكائنات بناءً على الاحتمالية والفئة
        for i, (conf, label) in enumerate(zip(confidences, labels)):
            if conf > threshold:  
                if label == 1:  # التأكد من أن الفئة هي "Seat"
                    x_min, y_min, x_max, y_max = boxes[i]
                    print(f"الإحداثيات لمقعد الأريكة: ({x_min}, {y_min}), ({x_max}, {y_max})")

                    # تحويل الإحداثيات إلى قيم صحيحة
                    x_min, y_min, x_max, y_max = map(int, [x_min, y_min, x_max, y_max])

                    # تحديد أبعاد المقعد
                    seat_width = x_max - x_min
                    seat_height = y_max - y_min

                    # حساب حجم الوسادة بناءً على حجم المقعد
                    back_height = seat_height  
                    pillow_width = seat_width // 4  
                    pillow_height = back_height   

                    # تغيير حجم الوسادة لتناسب المقعد
                    resized_pillow = cv2.resize(pillow_image_no_background, (pillow_width, pillow_height))

                    # تحديد مكان الوسادة على المقعد
                    pillow_x = x_min + (seat_width - pillow_width) // 3  
                    pillow_y = y_min - (pillow_height - 18) 

                    # تحميل صورة الأريكة
                    sofa_image = cv2.imread(sofa_image_path)
                    sofa_image = cv2.cvtColor(sofa_image, cv2.COLOR_BGR2BGRA)  # دعم الشفافية

                    # دمج الوسادة مع الأريكة
                    roi = sofa_image[pillow_y:pillow_y + pillow_height, pillow_x:pillow_x + pillow_width]

                    # دمج الألوان وقناة الشفافية
                    for c in range(0, 3):  # RGB
                        roi[:, :, c] = roi[:, :, c] * (1 - resized_pillow[:, :, 3] / 255.0) + resized_pillow[:, :, c] * (resized_pillow[:, :, 3] / 255.0)

                    # استبدال المنطقة المحدثة في الصورة الأصلية
                    sofa_image[pillow_y:pillow_y + pillow_height, pillow_x:pillow_x + pillow_width] = roi

                    # إرجاع الصورة النهائية بعد الدمج
                    return sofa_image  

# تأكد أن مجلد media/generated موجود
GENERATED_IMAGES_PATH = os.path.join(settings.MEDIA_ROOT, "generated")
os.makedirs(GENERATED_IMAGES_PATH, exist_ok=True)

@csrf_exempt
def generate_image(request):
    """دالة استقبال الصور من الفرونت ومعالجة النتائج"""
    try:
        if request.method == 'POST' and 'sofa_image' in request.FILES and 'pillow_image' in request.FILES:
            sofa_image = request.FILES['sofa_image']
            pillow_image = request.FILES['pillow_image']

            # حفظ الصور في ملفات مؤقتة (لتتوافق مع YOLO)
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_sofa:
                temp_sofa.write(sofa_image.read())
                temp_sofa_path = temp_sofa.name

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_pillow:
                temp_pillow.write(pillow_image.read())
                temp_pillow_path = temp_pillow.name

            # تشغيل الموديل على صورة الأريكة
            results = model.predict(temp_sofa_path)

            # تنفيذ عملية الدمج
            final_image = add_pillow_to_sofa_with_transparency(temp_sofa_path, temp_pillow_path, results)

            # إذا نجحت العملية، نحفظ الصورة ونرجع رابطها
            if final_image is not None:
                # تحديد مسار حفظ الصورة النهائية
                final_image_filename = f"sofa_with_pillow_{int(time.time())}.png"
                final_image_path = os.path.join(GENERATED_IMAGES_PATH, final_image_filename)

                # حفظ الصورة على القرص
                cv2.imwrite(final_image_path, final_image)

                # توليد رابط URL للصورة
                final_image_url = f"{settings.MEDIA_URL}generated/{final_image_filename}"
                

                return JsonResponse({"image_url": final_image_url})

            return JsonResponse({"error": "تعذر إنشاء الصورة النهائية."}, status=400)

        return JsonResponse({"error": "يجب رفع صورتين (أريكة ووسادة)"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
