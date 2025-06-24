from django.apps import AppConfig


class ImageSearchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'image_search'
    
    def ready(self):
        # هذا الكود سيتم تشغيله مرة واحدة عند بدء تشغيل Django
        # يجب أن يتم استيرادها داخل الدالة لتجنب مشاكل الاستيراد الدائرية
        from .utils import build_faiss_index_from_media_folder
        print("تهيئة فهرس FAISS من مجلد MEDIA_ROOT عند بدء تطبيق image_search...")
        build_faiss_index_from_media_folder() # استدعاء الدالة الجديدة
        print("تمت تهيئة فهرس FAISS لتطبيق image_search.")
