# image_search/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from PIL import Image
import io
import base64 # ما زلنا نحتاجها إذا كنت تريد تحويل صورة إلى Base64 في وظيفة البحث
from .utils import search_similar_images, get_embedding_for_text, get_sentence_transformer_model
from handcrafts.models import Handcraft # <--- تأكد من المسار الصحيح لنموذجك

@csrf_exempt
def search_view(request):
    if request.method == 'POST':
        try:
            query_text = ''
            image_file = None
            results = []

            # 1. حاول قراءة البيانات كـ multipart/form-data أولاً
            # هذا هو المسار الأكثر شيوعًا لرفع الملفات مع بيانات نصية أخرى.
            if request.POST or request.FILES: # تحقق إذا كان هناك أي بيانات POST أو ملفات
                query_text = request.POST.get('query_text', '').strip()
                image_file = request.FILES.get('query_image_file') # اسم الحقل لملف الصورة

            # 2. إذا لم تكن هناك بيانات POST/FILES، جرب قراءة JSON (خيار احتياطي)
            # هذا الجزء سيعمل فقط إذا لم يتم قراءة stream البيانات بواسطة request.POST/request.FILES
            # وبالتالي، لن يتعارض مع الطريقة الأساسية (multipart/form-data)
            elif request.body:
                content_type = request.headers.get('Content-Type', '').lower()
                if 'application/json' in content_type:
                    data = json.loads(request.body)
                    query_text = data.get('query_text', '').strip()
                    # إذا كنت لا تزال تريد دعم Base64 من JSON كخيار
                    image_base64 = data.get('image_base64', '').strip()
                    if image_base64:
                        try:
                            img_data = base64.b64decode(image_base64)
                            image_file = io.BytesIO(img_data) # حولها إلى ملف شبيه بـ file object
                            # ملاحظة: إذا كنت ترسل Base64، فلن يكون 'image_file' بالضرورة من request.FILES
                            # ستحتاج إلى التعامل معها كـ PIL Image مباشرة بعد فك التشفير.
                            # لتجنب التعقيد، دعنا نركز على Form Data لرفع الصور
                            # إذا أردت دعم Base64، ستحتاج إلى إعادة هيكلة هذا الجزء.
                            # للتوضيح: إذا كان request.body موجوداً، فلن يكون request.FILES موجوداً.
                            # لذا، يجب عليك اختيار إما Form Data أو Base64 (وليس كلاهما بنفس الأسلوب الأولي).
                            # الأفضل أن نركز على Form Data بناءً على طلبك.
                            # سنزيل التعامل مع image_base64 هنا لتجنب التعقيد.
                            pass # لا نفعل شيئاً هنا إذا كانت الأولوية لـ Form Data
                        except:
                            print("except in search view")
                else:
                    return JsonResponse({'error': 'Unsupported Content-Type for POST request.'}, status=400)
            else:
                return JsonResponse({'error': 'No data provided in the request.'}, status=400)


            # الآن، عالج البيانات المستلمة
            if not query_text and not image_file:
                return JsonResponse({'error': 'No query_text or image_file provided'}, status=400)

            # معالجة البحث النصي
            if query_text:
                text_results = search_similar_images(query_text=query_text, top_k=4)
                results.extend(text_results)

            # معالجة البحث بالصور
            if image_file:
                try:
                    image = Image.open(image_file).convert("RGB")
        # بدلاً من استدعاء search_similar_images مباشرة هنا، يمكنك تمرير الـ embedding
        # أو تعديل search_similar_images لتقبل كائن PIL.Image
        # لنفترض أن search_similar_images تتوقع PIL Image الآن
                    image_results = search_similar_images(query_image=image, top_k=4)
                    results.extend(image_results)
                except Exception as e:
                    import traceback
                    print(f"Error processing uploaded image: {traceback.format_exc()}")
                    return JsonResponse({'error': f'Failed to process uploaded image file: {str(e)}'}, status=400)

            return JsonResponse({'status': 'success', 'results': results})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body (if Content-Type was application/json).'}, status=400)
        except Exception as e:
            import traceback
            print(f"An unexpected error occurred: {traceback.format_exc()}")
            return JsonResponse({'error': 'An unexpected server error occurred.', 'details': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)









# from django.shortcuts import render

# # Create your views here.
# # image_search/views.py
# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from PIL import Image
# import io
# from .utils import search_similar_images # استيراد وظيفة البحث
# # لم نعد بحاجة لاستيراد ImageItem هنا إذا كنا سنمر على الملفات مباشرة
# import base64
# from handcrafts.models import Handcraft

# @csrf_exempt
# def search_view(request):
#     if request.method == 'POST':
#         try:
#             # التحقق من نوع المحتوى (Content-Type)
#             content_type = request.headers.get('Content-Type', '').lower()

#             if 'application/json' in content_type:
#                 # إذا كانت البيانات JSON في الـ body
#                 data = json.loads(request.body)
#                 query_text = data.get('query_text', '').strip()
#                 image_base64 = data.get('image_base64', '').strip()

#                 results = []
#                 if query_text:
#                     # البحث بالنص
#                     text_results = search_similar_images(query_text=query_text, top_k=4) # أو عدد النتائج الذي تريده
#                     results.extend(text_results)

#                 if image_base64:
#                     # البحث بالصورة (تحتاج إلى فك تشفير base64 وتحويلها إلى PIL Image)
#                     try:
#                         # فك تشفير الصورة من base64
#                         img_data = base64.b64decode(image_base64)
#                         image = Image.open(io.BytesIO(img_data)).convert("RGB")
#                         image_results = search_similar_images(query_image=image, top_k=4)
#                         results.extend(image_results)
#                     except Exception as e:
#                         return JsonResponse({'error': f'Invalid image_base64: {str(e)}'}, status=400)

#                 if not query_text and not image_base64:
#                     return JsonResponse({'error': 'No query_text or image_base64 provided'}, status=400)

#                 return JsonResponse({'status': 'success', 'results': results})

#             elif 'multipart/form-data' in content_type and 'query_image_file' in request.FILES:
#                 # إذا كانت البيانات ملف صورة مرفوع مباشرة (أقل شيوعا لـ API ولكن ممكن)
#                 image_file = request.FILES['query_image_file']
#                 try:
#                     image = Image.open(image_file).convert("RGB")
#                     results = search_similar_images(query_image=image, top_k=4)
#                     return JsonResponse({'status': 'success', 'results': results})
#                 except Exception as e:
#                     return JsonResponse({'error': f'Failed to process uploaded image file: {str(e)}'}, status=400)

#             else:
#                 return JsonResponse({'error': 'Unsupported Content-Type or missing data.'}, status=400)

#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
#         except Exception as e:
#             # هذا سيلتقط أي أخطاء أخرى غير متوقعة
#             import traceback
#             print(f"An unexpected error occurred: {traceback.format_exc()}")
#             return JsonResponse({'error': 'An unexpected server error occurred.', 'details': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)

# # def search_view(request):
# #     """
# #     نقطة النهاية للبحث عن الصور المتشابهة.
# #     تقبل طلبات POST مع نص استعلام أو ملف صورة.
# #     """
# #     if request.method == 'POST':
# #         query_image = None
# #         query_text = None

# #         if 'image' in request.FILES:
# #             image_file = request.FILES['image']
# #             try:
# #                 query_image = Image.open(io.BytesIO(image_file.read()))
# #             except Exception as e:
# #                 return JsonResponse({'error': f'خطأ في معالجة الصورة المرفوعة: {e}'}, status=400)
        
# #         if 'text' in request.POST:
# #             query_text = request.POST.get('text', '').strip()
# #         elif request.body:
# #             try:
# #                 data = json.loads(request.body)
# #                 query_text = data.get('text', '').strip()
# #             except json.JSONDecodeError:
# #                 pass

# #         if not query_image and not query_text:
# #             return JsonResponse({'error': 'يرجى تقديم صورة أو نص للاستعلام.'}, status=400)

# #         results_data, _ = search_similar_images(query_image or query_text) # الآن تستقبل النتائج المنسقة

# #         if "error" in results_data:
# #              return JsonResponse(results_data, status=400)

# #         # الـ 'image_url' في النتائج جاهز الآن، لا حاجة لـ request.build_absolute_uri
# #         # لأنه تم بناؤه باستخدام settings.MEDIA_URL
# #         return JsonResponse({'status': 'success', 'results': results_data["results"]})

# #     elif request.method == 'GET':
# #         return render(request, 'image_search/search_form.html')
    
# #     return JsonResponse({'error': 'طريقة الطلب غير مدعومة.'}, status=405)

# # يمكنك إزالة upload_image_view إذا كنت لا تخطط لرفع صور جديدة عبر هذا التطبيق
# # أو يمكنك تعديلها لرفع الصور إلى نموذج Product الخاص بك بدلاً من ImageItem
# # (لكن تذكر تحديث الفهرس بعدها).