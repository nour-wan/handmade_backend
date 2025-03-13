
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

def add_pillow_to_sofa_with_transparency(sofa_image, pillow_image, results):
    try:  
        """دالة دمج الوسادة مع الأريكة بعد التحليل"""
        sofa_image = np.array(Image.open(sofa_image))
        pillow_image = np.array(Image.open(pillow_image))

        # جعل الخلفية البيضاء للوسادة شفافة
        pillow_image = cv2.cvtColor(pillow_image, cv2.COLOR_RGB2BGRA)
        lower_bound = np.array([200, 200, 200, 0])
        upper_bound = np.array([255, 255, 255, 255])
        mask = cv2.inRange(pillow_image, lower_bound, upper_bound)
        pillow_image[mask == 255] = [0, 0, 0, 0]

        # تحليل النتائج وتحديد مكان المقعد
        for result in results:
            boxes = result.boxes.xyxy
            labels = result.boxes.cls
            confidences = result.boxes.conf

            threshold = 0.5
            for i, (conf, label) in enumerate(zip(confidences, labels)):
                if conf > threshold and label == 1:
                    x_min, y_min, x_max, y_max = map(int, boxes[i])

                    seat_width = x_max - x_min
                    seat_height = y_max - y_min

                    # تغيير حجم الوسادة لتتناسب مع المقعد
                    pillow_width = seat_width // 5
                    pillow_height = seat_height
                    resized_pillow = cv2.resize(pillow_image, (pillow_width, pillow_height))

                    # تحديد مكان الوسادة
                    pillow_x = x_min + (seat_width - pillow_width) // 3
                    pillow_y = y_min - (pillow_height - 3)

                    # دمج الوسادة على صورة الأريكة
                    for c in range(3):
                        sofa_image[pillow_y:pillow_y + pillow_height, pillow_x:pillow_x + pillow_width, c] = (
                                resized_pillow[:, :, c] * (resized_pillow[:, :, 3] / 255.0)
                                + sofa_image[pillow_y:pillow_y + pillow_height, pillow_x:pillow_x + pillow_width, c]
                                * (1 - resized_pillow[:, :, 3] / 255.0)
                        )

        return sofa_image
     
    except Exception as e:
        print(f"Error in processing images: {e}")
        return None


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

            # إذا نجحت العملية، نرجع الصورة النهائية
            if final_image is not None:
                _, buffer = cv2.imencode('.png', final_image)
                return HttpResponse(io.BytesIO(buffer).getvalue(), content_type="image/png")

            return JsonResponse({"error": "تعذر إنشاء الصورة النهائية."}, status=400)

        return JsonResponse({"error": "يجب رفع صورتين (أريكة ووسادة)"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
    
# import cv2
# import numpy as np
# import io
# from PIL import Image
# from django.http import HttpResponse, JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from ultralytics import YOLO

# # تحميل النموذج مرة واحدة فقط عند بدء السيرفر
# model = YOLO(r'C:\Users\NOUR\Desktop\handmade_backend\ml_model\best.pt')


# # دالة المعالجة
# def add_pillow_to_sofa_with_transparency(sofa_image, pillow_image, results):
#     # تحويل الصور إلى numpy arrays
#     sofa_image = np.array(Image.open(sofa_image))
#     pillow_image = np.array(Image.open(pillow_image))

#     # معالجة الوسادة لجعل الخلفية شفافة
#     pillow_image = cv2.cvtColor(pillow_image, cv2.COLOR_RGB2BGRA)
#     lower_bound = np.array([200, 200, 200, 0])
#     upper_bound = np.array([255, 255, 255, 255])
#     mask = cv2.inRange(pillow_image, lower_bound, upper_bound)
#     pillow_image[mask == 255] = [0, 0, 0, 0]

#     # تحليل نتائج الموديل للعثور على مكان الجلوس
#     for result in results:
#         boxes = result.boxes.xyxy
#         labels = result.boxes.cls
#         confidences = result.boxes.conf

#         threshold = 0.5
#         for i, (conf, label) in enumerate(zip(confidences, labels)):
#             if conf > threshold and label == 1:  # التأكد أن الفئة "Seat"
#                 x_min, y_min, x_max, y_max = map(int, boxes[i])

#                 seat_width = x_max - x_min
#                 seat_height = y_max - y_min

#                 # تغيير حجم الوسادة
#                 pillow_width = seat_width // 5
#                 pillow_height = seat_height
#                 resized_pillow = cv2.resize(pillow_image, (pillow_width, pillow_height))

#                 # تحديد موقع الوسادة على الأريكة
#                 pillow_x = x_min + (seat_width - pillow_width) // 3
#                 pillow_y = y_min - (pillow_height - 3)

#                 # دمج الوسادة مع صورة الأريكة
#                 for c in range(3):
#                     sofa_image[pillow_y:pillow_y + pillow_height, pillow_x:pillow_x + pillow_width, c] = \
#                         resized_pillow[:, :, c] * (resized_pillow[:, :, 3] / 255.0) + \
#                         sofa_image[pillow_y:pillow_y + pillow_height, pillow_x:pillow_x + pillow_width, c] * (
#                                 1 - resized_pillow[:, :, 3] / 255.0)

#     return sofa_image


# # دالة استلام الملفات من الفرونت
# @csrf_exempt
# def generate_image(request):
#     try:
#         if request.method == 'POST' and 'sofa_image' in request.FILES and 'pillow_image' in request.FILES:
#             sofa_image = request.FILES['sofa_image']
#             pillow_image = request.FILES['pillow_image']

#             # تشغيل الموديل لتحليل صورة الأريكة
#             results = model.predict(sofa_image)

#             # تنفيذ دمج الوسادة على الأريكة
#             final_image = add_pillow_to_sofa_with_transparency(sofa_image, pillow_image, results)

#             if final_image is not None:
#                 _, buffer = cv2.imencode('.png', final_image)
#                 return HttpResponse(io.BytesIO(buffer).getvalue(), content_type="image/png")
#             else:
#                 return JsonResponse({"error": "تعذر إنشاء الصورة النهائية."}, status=400)

#         return JsonResponse({"error": "يجب رفع صورتين (أريكة ووسادة)"}, status=400)

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)




# import cv2
# import numpy as np
# import io
# from PIL import Image
# from django.http import HttpResponse, JsonResponse
# from ultralytics import YOLO
# import matplotlib.pyplot as plt

# # تحميل النموذج المدرب
# model = YOLO(r'C:\Users\NOUR\Desktop\handmade_backend\ml_model\best.pt')
# results = model.predict(r'C:\Users\NOUR\Desktop\handmade_backend\ml_model\2024-12-26 18.56.23.jpg')


# # الدالة لمعالجة الصور
# def add_pillow_to_sofa_with_transparency(sofa_image_path, pillow_image_path, results):
#     image = cv2.imread(pillow_image_path, cv2.IMREAD_UNCHANGED)
#     if image is None:
#         return None

#     image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
#     lower_bound = np.array([200, 200, 200, 0])
#     upper_bound = np.array([255, 255, 255, 255])

#     mask = cv2.inRange(image, lower_bound, upper_bound)
#     image[mask == 255] = [0, 0, 0, 0]

#     output_path = r"C:\Users\NOUR\Desktop\handmade_backend\ml_model\pillow_image_transparent.png"
#     cv2.imwrite(output_path, image)

#     pillow_image = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)

#     if pillow_image.shape[2] == 4:
#         pillow_rgb = pillow_image[:, :, :3]
#         alpha_channel = pillow_image[:, :, 3]
#     else:
#         pillow_rgb = pillow_image
#         alpha_channel = np.ones(pillow_rgb.shape[:2], dtype=np.uint8) * 255

#     for result in results:
#         labels = result.boxes.cls
#         boxes = result.boxes.xyxy
#         confidences = result.boxes.conf

#         threshold = 0.5
#         for i, (conf, label) in enumerate(zip(confidences, labels)):
#             if conf > threshold and label == 1:
#                 x_min, y_min, x_max, y_max = map(int, boxes[i])

#                 seat_width = x_max - x_min
#                 seat_height = y_max - y_min

#                 pillow_width = seat_width // 5
#                 pillow_height = seat_height

#                 resized_pillow = cv2.resize(pillow_rgb, (pillow_width, pillow_height))
#                 resized_alpha = cv2.resize(alpha_channel, (pillow_width, pillow_height))

#                 pillow_x = x_min + (seat_width - pillow_width) // 3
#                 pillow_y = y_min - (pillow_height - 3)

#                 sofa_image = cv2.imread(sofa_image_path)
#                 sofa_image = cv2.cvtColor(sofa_image, cv2.COLOR_BGR2BGRA)

#                 roi = sofa_image[pillow_y:pillow_y + pillow_height, pillow_x:pillow_x + pillow_width]

#                 for c in range(0, 3):
#                     roi[:, :, c] = roi[:, :, c] * (1 - resized_alpha / 255.0) + resized_pillow[:, :, c] * (
#                             resized_alpha / 255.0)

#                 sofa_image[pillow_y:pillow_y + pillow_height, pillow_x:pillow_x + pillow_width] = roi

#                 return sofa_image

#     return None


# # دالة الـ View لعرض الصورة
# def generate_image(request):
#     try:
#         sofa_image_path = r"C:\Users\NOUR\Desktop\handmade_backend\ml_model\2024-12-26 18.56.23.jpg"
#         pillow_image_path = r"C:\Users\NOUR\Desktop\handmade_backend\ml_model\2024-12-26 18.56.30.jpg"

#         final_image = add_pillow_to_sofa_with_transparency(sofa_image_path, pillow_image_path, results)

#         if final_image is not None:
#             _, buffer = cv2.imencode('.png', final_image)
#             return HttpResponse(io.BytesIO(buffer).getvalue(), content_type="image/png")
#         else:
#             return JsonResponse({"error": "تعذر إنشاء الصورة النهائية."}, status=400)

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)












# import threading
# import uvicorn
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import StreamingResponse
# import cv2
# import numpy as np
# import io
# import cv2
# import numpy as np
# import os
# import cv2
# import numpy as np
# from PIL import Image

# from ultralytics import YOLO
# import matplotlib.pyplot as plt

# # تحميل النموذج المدرب
# model = YOLO(r'C:\Users\NOUR\Desktop\handmade_backend\ml_model\best.pt')  # استبدل هذا بالمسار الفعلي للنموذج الخاص بك
# results = model.predict(r'C:\Users\NOUR\Desktop\handmade_backend\ml_model\2024-12-26 18.56.23.jpg')  # استبدل بهذا المسار الفعلي للصورة
# # عرض الصورة مع النتائج
# for result in results:
#     img = result.plot()  # إضافة التنبؤات على الصورة
#     plt.imshow(img)
#     plt.axis('off')
#     plt.show()

# def add_pillow_to_sofa_with_transparency(sofa_image_path, pillow_image_path, results):
#     # قراءة صورة الوسادة وتطبيق الشفافية
#     image = cv2.imread(pillow_image_path, cv2.IMREAD_UNCHANGED)

#     if image is None:
#         raise ValueError("لم يتم العثور على الصورة. تأكد من المسار.")

#     # تحويل الصورة إلى RGBA (إضافة قناة ألفا)
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

#     # تحديد اللون الأبيض كخلفية (لإزالة الخلفية البيضاء)
#     lower_bound = np.array([200, 200, 200, 0])  
#     upper_bound = np.array([255, 255, 255, 255])  

#     # إنشاء القناع لتحديد الخلفية البيضاء
#     mask = cv2.inRange(image, lower_bound, upper_bound)

#     # جعل الخلفية شفافة
#     image[mask == 255] = [0, 0, 0, 0]

#     # حفظ الصورة المعدلة (التي أصبحت شفافة)
#     output_path = r"C:\Users\NOUR\Desktop\handmade_backend\ml_model\pillow_image_transparent.png"
#     cv2.imwrite(output_path, image)

#     # قراءة صورة الوسادة مع الشفافية
#     pillow_image = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)

#     if pillow_image.shape[2] == 4:  # إذا كانت الصورة تحتوي على قناة ألفا (شفافية)
#         pillow_rgb = pillow_image[:, :, :3]  # RGB فقط
#         alpha_channel = pillow_image[:, :, 3]  # قناة ألفا (الشفافية)
#     else:
#         pillow_rgb = pillow_image  # إذا كانت الصورة 3 قنوات (RGB)
#         alpha_channel = np.ones(pillow_rgb.shape[:2], dtype=np.uint8) * 255  # قناة شفافية افتراضية

#     # استعراض نتائج التنبؤ (لكل كائن تم اكتشافه)
#     for result in results:
#         labels = result.boxes.cls  
#         boxes = result.boxes.xyxy  # إحداثيات (x_min, y_min, x_max, y_max)
#         confidences = result.boxes.conf  

#         threshold = 0.5  
#         # تصفية الكائنات بناءً على الاحتمالية والفئة
#         for i, (conf, label) in enumerate(zip(confidences, labels)):
#             if conf > threshold:  
#                 if label == 1:  # التأكد من أن الفئة هي "Seat"
#                     x_min, y_min, x_max, y_max = boxes[i]
#                     print(f"الإحداثيات لمقعد الأريكة: ({x_min}, {y_min}), ({x_max}, {y_max})")

#                     # تحويل الإحداثيات إلى قيم صحيحة
#                     x_min, y_min, x_max, y_max = map(int, [x_min, y_min, x_max, y_max])

#                     # تحديد أبعاد المقعد
#                     seat_width = x_max - x_min
#                     seat_height = y_max - y_min

#                     # حساب حجم الوسادة بناءً على حجم المقعد
#                     back_height = seat_height  
#                     pillow_width = seat_width //5  
#                     pillow_height = back_height   

#                     # تغيير حجم الوسادة لتناسب المقعد
#                     resized_pillow = cv2.resize(pillow_rgb, (pillow_width, pillow_height))
#                     resized_alpha = cv2.resize(alpha_channel, (pillow_width, pillow_height))

#                     # تحديد مكان الوسادة على المقعد
#                     pillow_x = x_min + (seat_width - pillow_width) // 3  
#                     pillow_y = y_min - (pillow_height - 3) 

#                     # تحميل صورة الأريكة
#                     sofa_image = cv2.imread(sofa_image_path)
#                     sofa_image = cv2.cvtColor(sofa_image, cv2.COLOR_BGR2BGRA)  # دعم الشفافية

#                     # دمج الوسادة مع الأريكة
#                     roi = sofa_image[pillow_y:pillow_y + pillow_height, pillow_x:pillow_x + pillow_width]

#                     # دمج الألوان وقناة الشفافية
#                     for c in range(0, 3):  # RGB
#                         roi[:, :, c] = roi[:, :, c] * (1 - resized_alpha / 255.0) + resized_pillow[:, :, c] * (resized_alpha / 255.0)

#                     # استبدال المنطقة المحدثة في الصورة الأصلية
#                     sofa_image[pillow_y:pillow_y + pillow_height, pillow_x:pillow_x + pillow_width] = roi

#                     # إرجاع الصورة النهائية بعد الدمج
#                     return sofa_image  

# # استدعاء الدالة في الملف
# sofa_image_path = r"C:\Users\NOUR\Desktop\handmade_backend\ml_model\2024-12-26 18.56.23.jpg"
# pillow_image_path = r"C:\Users\NOUR\Desktop\handmade_backend\ml_model\2024-12-26 18.56.30.jpg"
# final_image = add_pillow_to_sofa_with_transparency(sofa_image_path, pillow_image_path, results)



# app = FastAPI()
# @app.get("/image")
# def get_image():
#     print("تم الوصول إلى رابط /image")  # للتحقق من الوصول إلى الرابط
#     try:
#         sofa_image_path = r"C:\Users\NOUR\Desktop\handmade_backend\ml_model\2024-12-26 18.56.23.jpg"
#         pillow_image_path = r"C:\Users\NOUR\Desktop\handmade_backend\ml_model\2024-12-26 18.56.30.jpg"

#         final_image = add_pillow_to_sofa_with_transparency(sofa_image_path, pillow_image_path, results)

#         if final_image is not None:
#             # تحويل الصورة إلى تنسيق يمكن إرجاعه في استجابة HTTP
#             _, buffer = cv2.imencode('.png', final_image)
#             io_buf = io.BytesIO(buffer)
#             return StreamingResponse(io_buf, media_type="image/png")
#         else:
#             raise HTTPException(status_code=400, detail="تعذر إنشاء الصورة النهائية.")

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # تشغيل الخادم في خيط منفصل لتجنب خطأ asyncio
# def start_uvicorn():
#     uvicorn.run(app, host="127.0.0.1", port=8000)

# if __name__ == "__main__":
#     threading.Thread(target=start_uvicorn).start()


# if final_image is None:
#     raise ValueError("الصورة الناتجة فارغة.")

# sofa_image = cv2.imread(sofa_image_path)
# if sofa_image is None:
#     print("فشل تحميل صورة الأريكة، تأكد من المسار.")









# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.parsers import MultiPartParser, FormParser
# import cv2
# import numpy as np
# import io
# from PIL import Image
# from django.core.files.uploadedfile import InMemoryUploadedFile
# from .utils import model  # استيراد YOLO
# from django.http import HttpResponse
# # ✅ الدالة التي تضيف الوسادة إلى الأريكة مع الحفاظ على الشفافية
# def add_pillow_to_sofa_with_transparency(sofa_image, pillow_image, results):
#     image = cv2.imdecode(np.frombuffer(pillow_image.read(), np.uint8), cv2.IMREAD_UNCHANGED)

#     if image is None:
#         raise ValueError("لم يتم العثور على صورة الوسادة.")

#     image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
#     lower_bound = np.array([200, 200, 200, 0])
#     upper_bound = np.array([255, 255, 255, 255])
#     mask = cv2.inRange(image, lower_bound, upper_bound)
#     image[mask == 255] = [0, 0, 0, 0]

#     pillow_image = image
#     if pillow_image.shape[2] == 4:
#         pillow_rgb = pillow_image[:, :, :3]
#         alpha_channel = pillow_image[:, :, 3]
#     else:
#         pillow_rgb = pillow_image
#         alpha_channel = np.ones(pillow_rgb.shape[:2], dtype=np.uint8) * 255

#     for result in results:
#         labels = result.boxes.cls
#         boxes = result.boxes.xyxy
#         confidences = result.boxes.conf
#         threshold = 0.5  

#         for i, (conf, label) in enumerate(zip(confidences, labels)):
#             if conf > threshold and label == 1:  
#                 x_min, y_min, x_max, y_max = map(int, boxes[i])
#                 seat_width = x_max - x_min
#                 seat_height = y_max - y_min
#                 back_height = seat_height
#                 pillow_width = seat_width // 4
#                 pillow_height = back_height  

#                 resized_pillow = cv2.resize(pillow_rgb, (pillow_width, pillow_height))
#                 resized_alpha = cv2.resize(alpha_channel, (pillow_width, pillow_height))

#                 pillow_x = x_min + (seat_width - pillow_width) // 3  
#                 pillow_y = y_min - (pillow_height - 2)

#                 sofa_image = cv2.imdecode(np.frombuffer(sofa_image.read(), np.uint8), cv2.IMREAD_UNCHANGED)
#                 sofa_image = cv2.cvtColor(sofa_image, cv2.COLOR_BGR2BGRA)  

#                 roi = sofa_image[pillow_y:pillow_y + pillow_height, pillow_x:pillow_x + pillow_width]

#                 for c in range(3):  
#                     roi[:, :, c] = roi[:, :, c] * (1 - resized_alpha / 255.0) + resized_pillow[:, :, c] * (resized_alpha / 255.0)

#                 sofa_image[pillow_y:pillow_y + pillow_height, pillow_x:pillow_x + pillow_width] = roi

#                 return sofa_image  

#     return None  

# def preprocess_image(image_file):
#     image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)
#     return image

# # ✅ API لمعالجة الصور وإضافة الوسادة للأريكة
# class ProcessImagesView(APIView):
#     parser_classes = (MultiPartParser, FormParser)

#     def post(self, request, *args, **kwargs):
#         if 'sofa_image' not in request.FILES or 'pillow_image' not in request.FILES:
#             return Response({"error": "يرجى إرسال صورتين (الأريكة + الوسادة)."}, status=400)

#         sofa_image = request.FILES['sofa_image']
#         pillow_image = request.FILES['pillow_image']

#         # تمرير صورة الأريكة إلى YOLO للحصول على الإحداثيات
#         sofa_array = preprocess_image(sofa_image)
#         results = model(sofa_array)
#         # results = model(sofa_image)

#         # إضافة الوسادة إلى الأريكة
#         output_image = add_pillow_to_sofa_with_transparency(sofa_image, pillow_image, results)

#         if output_image is None:
#             return Response({"error": "لم يتم العثور على مكان مناسب لوضع الوسادة."}, status=400)

#         # تحويل الصورة الناتجة إلى استجابة HTTP
#         _, img_encoded = cv2.imencode('.jpg', output_image)
#         img_bytes = img_encoded.tobytes()

#         return HttpResponse(img_bytes, content_type="image/jpeg")