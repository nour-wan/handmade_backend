# image_search/apps.py
from django.apps import AppConfig

class ImageSearchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'image_search'

    def ready(self):
        pass
        # يجب أن يتم استيرادها داخل الدالة لتجنب مشاكل الاستيراد الدائرية
        # وتأكد أن models.py لتطبيق Products قد تم تحميله بالفعل
        # import sys
        # if 'runserver' in sys.argv or 'gunicorn' in sys.argv: # تأكد من التشغيل عند بدء الخادم فقط
            # from .utils import init_faiss_index
            # print("تهيئة فهرس FAISS عند بدء تطبيق image_search (تحميل أو بناء)...")
            # init_faiss_index() # استدعاء الدالة الجديدة
            # print("تمت تهيئة فهرس FAISS لتطبيق image_search.")