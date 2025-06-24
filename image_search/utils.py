# image_search/utils.py

import os
import numpy as np
import faiss
from PIL import Image
from sentence_transformers import SentenceTransformer
from django.conf import settings
# لم نعد بحاجة لاستيراد ImageItem هنا إذا كنا سنمر على الملفات مباشرة

_model = None
_faiss_index = None
_image_paths = []     # لتخزين المسارات الكاملة للصور (بدلاً من filenames)
_image_urls = []      # لتخزين URLs لـ Django للصور (لعرضها في الواجهة)

def get_sentence_transformer_model():
    """يحمل نموذج SentenceTransformer مرة واحدة."""
    global _model
    if _model is None:
        print("تحميل نموذج CLIP-ViT-B-32...")
        _model = SentenceTransformer('clip-ViT-B-32')
        print("تم تحميل النموذج.")
    return _model

def build_faiss_index_from_media_folder():
    """
    يبني فهرس FAISS من جميع الصور الموجودة في مجلد MEDIA_ROOT.
    """
    global _faiss_index, _image_paths, _image_urls

    if _faiss_index is not None:
        print("الفهرس موجود بالفعل، لن يتم إعادة بنائه.")
        return _faiss_index, _image_paths, _image_urls

    print("بناء فهرس FAISS من مجلد MEDIA_ROOT...")
    model = get_sentence_transformer_model()
    image_embeddings = []
    _image_paths = []
    _image_urls = []

    # المسار الأساسي لمجلد الوسائط
    media_root = settings.MEDIA_ROOT
    media_url_base = settings.MEDIA_URL

    # التأكد من وجود مجلد media_root
    if not os.path.isdir(media_root):
        print(f"خطأ: مجلد MEDIA_ROOT غير موجود أو غير صالح: {media_root}")
        return None, [], []

    # البحث عن جميع ملفات الصور (jpg, jpeg, png, gif) داخل مجلد MEDIA_ROOT والمجلدات الفرعية
    supported_extensions = ('.jpg', '.jpeg', '.png', '.gif')
    for root_dir, _, files in os.walk(media_root):
        for file in files:
            if file.lower().endswith(supported_extensions):
                image_path = os.path.join(root_dir, file)
                # حساب المسار النسبي من MEDIA_ROOT للحصول على URL الصحيح
                relative_path = os.path.relpath(image_path, media_root)
                image_url = os.path.join(media_url_base, relative_path).replace(os.sep, '/') # استبدال فواصل المسار لـ URL

                try:
                    image = Image.open(image_path).convert("RGB")
                    embedding = model.encode(image)
                    image_embeddings.append(embedding)
                    _image_paths.append(image_path)
                    _image_urls.append(image_url)

                except Exception as e:
                    print(f"خطأ في معالجة الصورة {image_path}: {e}")
                    continue

    if not image_embeddings:
        print("لا توجد متجهات صور صالحة للبناء الفهرس من مجلد الوسائط.")
        return None, [], []

    embedding_dim = image_embeddings[0].shape[0]
    _faiss_index = faiss.IndexFlatL2(embedding_dim)
    _faiss_index.add(np.array(image_embeddings))
    print(f"تم بناء فهرس FAISS بنجاح من مجلد MEDIA_ROOT. عدد العناصر: {_faiss_index.ntotal}")

    return _faiss_index, _image_paths, _image_urls


def search_similar_images(query_input, top_k=4, threshold=150):
    """
    وظيفة البحث الرئيسية المستخدمة في الـ View.
    تقبل استعلام نصي أو صورة.
    """
    model = get_sentence_transformer_model()
    # استدعاء الدالة الجديدة لبناء الفهرس من مجلد الوسائط
    faiss_index, image_paths, image_urls = build_faiss_index_from_media_folder()

    if faiss_index is None:
        return {"error": "فهرس البحث غير جاهز. يرجى التأكد من وجود صور في مجلد MEDIA_ROOT."}, []

    query_embedding = None
    if isinstance(query_input, Image.Image):
        query_input = query_input.convert("RGB")
        query_embedding = model.encode(query_input)
    elif isinstance(query_input, str) and query_input.strip():
        query_embedding = model.encode(query_input)
    else:
        return {"error": "يرجى تقديم صورة أو نص للاستعلام."}, []

    D, I = faiss_index.search(np.array([query_embedding]), k=top_k)

    results = []
    for i, idx in enumerate(I[0]):
        distance = D[0][i]
        if distance < threshold:
            # استخدام _image_urls و _image_paths التي تم جمعها عند بناء الفهرس
            full_path = image_paths[idx]
            # يمكنك هنا استخراج اسم الملف إذا كنت تريده
            filename = os.path.basename(full_path)
            image_url = image_urls[idx]

            results.append({
                'image_url': image_url, # هذا هو URL الذي سيخدمه Django
                'filename': filename,
                'distance': float(distance)
            })

    return {"results": results, "query_embedding": query_embedding.tolist()}, results