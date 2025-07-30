# vase_table_sim/views.py

import os
import io
import time
import tempfile
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import cv2
# استيراد التوابع من ملف ai_functions.py في نفس الـ App
from .ai_functions import load_yolo_model, remove_background_from_image, add_vase_to_table

# تهيئة مسار حفظ الصور المولدة
# لا حاجة لتكرارها إذا كانت موجودة بالفعل، ولكن التأكد من تعريفها هنا جيد
GENERATED_IMAGES_PATH = os.path.join(settings.MEDIA_ROOT, "generated")
os.makedirs(GENERATED_IMAGES_PATH, exist_ok=True)

# 🚨 التعديل هنا: تحديد مسار نموذج YOLO بناءً على مكانه داخل vase_table_sim App
# نفترض أن 'best (1).pt' موجود مباشرة داخل مجلد 'vase_table_sim'
# أو في مجلد فرعي داخل 'vase_table_sim' (مثال: vase_table_sim/model/best (1).pt)
# تأكدي من المسار الفعلي.
V_T_SIM_APP_DIR = os.path.dirname(os.path.abspath(__file__)) # مسار الـ App الحالي
YOLO_MODEL_PATH = os.path.join(V_T_SIM_APP_DIR, 'best (1).pt') # 👈 هذا إذا كان النموذج مباشرة في جذر الـ App
# أو إذا كان في مجلد فرعي داخل الـ App مثل 'models':
# YOLO_MODEL_PATH = os.path.join(V_T_SIM_APP_DIR, 'models', 'best (1).pt')

# تحميل النموذج مرة واحدة عند بدء الخادم
try:
    yolo_model_instance = load_yolo_model(YOLO_MODEL_PATH)
except Exception as e:
    print(f"فشل تحميل نموذج YOLO عند بدء الخادم: {e}")
    yolo_model_instance = None # تعيينها إلى None للإشارة إلى الفشل

@csrf_exempt
def simulate_table_vase(request):
    """
    API endpoint لمعالجة طلبات محاكاة الفازة على الطاولة.
    يستقبل صورتين (طاولة وفازة) ويعيد صورة مدمجة.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST requests are allowed."}, status=405)

    if not yolo_model_instance:
        return JsonResponse({"error": "YOLO model failed to load. Please check server logs."}, status=503) # Service Unavailable

    

    try:
        table_image_file = request.FILES.get('table_image')
        vase_image_file = request.FILES.get('vase_image')

        if not table_image_file or not vase_image_file:
            return JsonResponse({"error": "يجب رفع صورتين (طاولة وفازة)."}, status=400)

        # 1. قراءة بايتات الملفات مباشرة من كائنات UploadedFile
        # هذه هي الطريقة الأفضل لتجنب المشاكل مع الملفات المؤقتة إذا لم تكن ضرورية
        table_image_bytes = table_image_file.read()
        vase_image_bytes = vase_image_file.read()

        # 2. إزالة خلفية الفازة مباشرة من البايتات
        vase_no_bg_pil_image = remove_background_from_image(vase_image_bytes)

        # 3. لحفظ صورة الطاولة مؤقتًا ليتمكن OpenCV من قراءتها من المسار
        # يجب إنشاء ملف مؤقت جديد هنا وتمرير مساره
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_table:
            temp_table.write(table_image_bytes)
            temp_table_path = temp_table.name

        try:
            # 4. دمج الفازة على الطاولة
            # نمرر المسار للصور المؤقتة وليس الكائن
            final_image_cv2 = add_vase_to_table(temp_table_path, vase_no_bg_pil_image, yolo_model_instance)

            if final_image_cv2 is None:
                return JsonResponse({"error": "تعذر إنشاء الصورة النهائية للمحاكاة."}, status=500)

            # 5. حفظ الصورة النهائية المولدة
            final_image_filename = f"table_with_vase_{int(time.time())}.png"
            final_image_path = os.path.join(GENERATED_IMAGES_PATH, final_image_filename)
            cv2.imwrite(final_image_path, final_image_cv2)

            # 6. توليد رابط URL للصورة
            final_image_url = f"{settings.MEDIA_URL}generated/{final_image_filename}"

            return JsonResponse({"image_url": final_image_url})

        finally:
            # التأكد من حذف الملف المؤقت بعد الانتهاء
            os.unlink(temp_table_path) # حذف ملف الطاولة المؤقت
            # لم نعد نستخدم temp_vase كملف مؤقت على القرص بنفس الطريقة
            # vase_image_file و table_image_file يتم إغلاقهم تلقائياً بواسطة Django
            # و vase_image_bytes لا تحتاج لحذف
            # التأكد من عدم وجود os.unlink(temp_vase_path) قديم هنا
            pass # لا شيء نحذفه هنا إذا لم ننشئ temp_vase_path

    except ValueError as ve:
        return JsonResponse({"error": str(ve)}, status=400)
    except Exception as e:
        import traceback
        print(f"An unexpected error occurred in simulate_table_vase: {traceback.format_exc()}")
        return JsonResponse({"error": "An unexpected server error occurred.", "details": str(e)}, status=500)