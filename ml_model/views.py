from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import cv2
import numpy as np
import io
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from .utils import model  # استيراد YOLO
from django.http import HttpResponse
# ✅ الدالة التي تضيف الوسادة إلى الأريكة مع الحفاظ على الشفافية
def add_pillow_to_sofa_with_transparency(sofa_image, pillow_image, results):
    image = cv2.imdecode(np.frombuffer(pillow_image.read(), np.uint8), cv2.IMREAD_UNCHANGED)

    if image is None:
        raise ValueError("لم يتم العثور على صورة الوسادة.")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    lower_bound = np.array([200, 200, 200, 0])
    upper_bound = np.array([255, 255, 255, 255])
    mask = cv2.inRange(image, lower_bound, upper_bound)
    image[mask == 255] = [0, 0, 0, 0]

    pillow_image = image
    if pillow_image.shape[2] == 4:
        pillow_rgb = pillow_image[:, :, :3]
        alpha_channel = pillow_image[:, :, 3]
    else:
        pillow_rgb = pillow_image
        alpha_channel = np.ones(pillow_rgb.shape[:2], dtype=np.uint8) * 255

    for result in results:
        labels = result.boxes.cls
        boxes = result.boxes.xyxy
        confidences = result.boxes.conf
        threshold = 0.5  

        for i, (conf, label) in enumerate(zip(confidences, labels)):
            if conf > threshold and label == 1:  
                x_min, y_min, x_max, y_max = map(int, boxes[i])
                seat_width = x_max - x_min
                seat_height = y_max - y_min
                back_height = seat_height
                pillow_width = seat_width // 4
                pillow_height = back_height  

                resized_pillow = cv2.resize(pillow_rgb, (pillow_width, pillow_height))
                resized_alpha = cv2.resize(alpha_channel, (pillow_width, pillow_height))

                pillow_x = x_min + (seat_width - pillow_width) // 3  
                pillow_y = y_min - (pillow_height - 2)

                sofa_image = cv2.imdecode(np.frombuffer(sofa_image.read(), np.uint8), cv2.IMREAD_UNCHANGED)
                sofa_image = cv2.cvtColor(sofa_image, cv2.COLOR_BGR2BGRA)  

                roi = sofa_image[pillow_y:pillow_y + pillow_height, pillow_x:pillow_x + pillow_width]

                for c in range(3):  
                    roi[:, :, c] = roi[:, :, c] * (1 - resized_alpha / 255.0) + resized_pillow[:, :, c] * (resized_alpha / 255.0)

                sofa_image[pillow_y:pillow_y + pillow_height, pillow_x:pillow_x + pillow_width] = roi

                return sofa_image  

    return None  

def preprocess_image(image_file):
    image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)
    return image

# ✅ API لمعالجة الصور وإضافة الوسادة للأريكة
class ProcessImagesView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if 'sofa_image' not in request.FILES or 'pillow_image' not in request.FILES:
            return Response({"error": "يرجى إرسال صورتين (الأريكة + الوسادة)."}, status=400)

        sofa_image = request.FILES['sofa_image']
        pillow_image = request.FILES['pillow_image']

        # تمرير صورة الأريكة إلى YOLO للحصول على الإحداثيات
        sofa_array = preprocess_image(sofa_image)
        results = model(sofa_array)
        # results = model(sofa_image)

        # إضافة الوسادة إلى الأريكة
        output_image = add_pillow_to_sofa_with_transparency(sofa_image, pillow_image, results)

        if output_image is None:
            return Response({"error": "لم يتم العثور على مكان مناسب لوضع الوسادة."}, status=400)

        # تحويل الصورة الناتجة إلى استجابة HTTP
        _, img_encoded = cv2.imencode('.jpg', output_image)
        img_bytes = img_encoded.tobytes()

        return HttpResponse(img_bytes, content_type="image/jpeg")