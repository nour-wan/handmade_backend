from django.shortcuts import render

# Create your views here.
# image_search/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import io
from .utils import search_similar_images # استيراد وظيفة البحث
# لم نعد بحاجة لاستيراد ImageItem هنا إذا كنا سنمر على الملفات مباشرة


@csrf_exempt
def search_view(request):
    """
    نقطة النهاية للبحث عن الصور المتشابهة.
    تقبل طلبات POST مع نص استعلام أو ملف صورة.
    """
    if request.method == 'POST':
        query_image = None
        query_text = None

        if 'image' in request.FILES:
            image_file = request.FILES['image']
            try:
                query_image = Image.open(io.BytesIO(image_file.read()))
            except Exception as e:
                return JsonResponse({'error': f'خطأ في معالجة الصورة المرفوعة: {e}'}, status=400)
        
        if 'text' in request.POST:
            query_text = request.POST.get('text', '').strip()
        elif request.body:
            try:
                data = json.loads(request.body)
                query_text = data.get('text', '').strip()
            except json.JSONDecodeError:
                pass

        if not query_image and not query_text:
            return JsonResponse({'error': 'يرجى تقديم صورة أو نص للاستعلام.'}, status=400)

        results_data, _ = search_similar_images(query_image or query_text) # الآن تستقبل النتائج المنسقة

        if "error" in results_data:
             return JsonResponse(results_data, status=400)

        # الـ 'image_url' في النتائج جاهز الآن، لا حاجة لـ request.build_absolute_uri
        # لأنه تم بناؤه باستخدام settings.MEDIA_URL
        return JsonResponse({'status': 'success', 'results': results_data["results"]})

    elif request.method == 'GET':
        return render(request, 'image_search/search_form.html')
    
    return JsonResponse({'error': 'طريقة الطلب غير مدعومة.'}, status=405)

# يمكنك إزالة upload_image_view إذا كنت لا تخطط لرفع صور جديدة عبر هذا التطبيق
# أو يمكنك تعديلها لرفع الصور إلى نموذج Product الخاص بك بدلاً من ImageItem
# (لكن تذكر تحديث الفهرس بعدها).