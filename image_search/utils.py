# image_search/utils.py

import os
import numpy as np
import faiss
from PIL import Image
from sentence_transformers import SentenceTransformer
from django.conf import settings
import pickle
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# استيراد نموذج المنتج من تطبيقك (تأكد من المسار الصحيح)
# ستحتاج إلى استبدال 'products.models' بالمسار الفعلي لنموذج Product الخاص بك
from handcrafts.models import Handcraft 


_model = None
# FAISS_INDEX_FILE و FAISS_METADATA_FILE
FAISS_INDEX_FILE = os.path.join(settings.MEDIA_ROOT, 'faiss_index.bin')
FAISS_METADATA_FILE = os.path.join(settings.MEDIA_ROOT, 'faiss_metadata.pkl')

# المتغيرات العالمية للفهرس والبيانات
# سنستخدم قاموس لربط معرف FAISS بـ Product ID
# _faiss_index: فهرس FAISS الفعلي
# _id_to_product_map: قاموس يربط فهرس FAISS بـ Product ID في قاعدة البيانات
# _product_to_id_map: قاموس يربط Product ID بفهرس FAISS (للوصول السريع)

_faiss_index = None
_id_to_product_map = {}  # {faiss_idx: product_id}
_product_to_id_map = {}  # {product_id: faiss_idx}


def get_sentence_transformer_model():
    """يحمل نموذج SentenceTransformer مرة واحدة."""
    global _model
    if _model is None:
        print("تحميل نموذج CLIP-ViT-B-32...")
        # تم تغيير النموذج للعمل على السيرفر
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("تم تحميل النموذج.")
    return _model

def get_embedding_for_text(text: str):
    model = get_sentence_transformer_model()
    embedding = model.encode(text, convert_to_tensor=True).cpu().numpy()
    return embedding.flatten() # يجب أن يكون متجه أحادي الأبعاد

def _get_embedding_for_image(image_path):
    """
    دالة مساعدة لاستخراج المتجه من مسار الصورة.
    """
    model = get_sentence_transformer_model()
    if not os.path.exists(image_path):
        print(f"تحذير: الصورة {image_path} غير موجودة على القرص.")
        return None
    try:
        image = Image.open(image_path).convert("RGB")
        embedding = model.encode(image, convert_to_tensor=True).cpu().numpy()
        return embedding.flatten()
    except Exception as e:
        print(f"خطأ في معالجة الصورة {image_path}: {e}")
        return None

def save_faiss_index():
    """يحفظ فهرس FAISS والبيانات الوصفية على القرص."""
    global _faiss_index, _id_to_product_map, _product_to_id_map
    try:
        if _faiss_index:
            # يمكن حفظ IndexIDMap مباشرة
            faiss.write_index(_faiss_index, FAISS_INDEX_FILE)
            with open(FAISS_METADATA_FILE, 'wb') as f:
                pickle.dump({
                    'id_to_product_map': _id_to_product_map,
                    'product_to_id_map': _product_to_id_map
                }, f)
            print(f"تم حفظ فهرس FAISS في: {FAISS_INDEX_FILE}")
            print(f"تم حفظ بيانات الفهرس الوصفية في: {FAISS_METADATA_FILE}")
        else:
            print("تحذير: الفهرس غير موجود لحفظه.")
    except Exception as e:
        print(f"خطأ في حفظ فهرس FAISS أو البيانات الوصفية: {e}")

def load_faiss_index():
    """يحاول تحميل فهرس FAISS والبيانات الوصفية من القرص."""
    global _faiss_index, _id_to_product_map, _product_to_id_map
    if os.path.exists(FAISS_INDEX_FILE) and os.path.exists(FAISS_METADATA_FILE):
        print(f"تحميل فهرس FAISS من: {FAISS_INDEX_FILE}")
        try:
            _faiss_index = faiss.read_index(FAISS_INDEX_FILE)
            with open(FAISS_METADATA_FILE, 'rb') as f:
                metadata = pickle.load(f)
                _id_to_product_map = metadata.get('id_to_product_map', {})
                _product_to_id_map = metadata.get('product_to_id_map', {})
            print("تم تحميل فهرس FAISS وبياناته الوصفية.")
            return True
        except Exception as e:
            print(f"خطأ في تحميل فهرس FAISS أو البيانات الوصفية: {e}")
            _faiss_index = None
            _id_to_product_map = {}
            _product_to_id_map = {}
            return False
    return False

def init_faiss_index():
    """
    تهيئة الفهرس عند بدء التطبيق.
    يحاول التحميل أولاً، وإذا فشل، يقوم ببناء الفهرس من جميع المنتجات.
    """
    global _faiss_index, _id_to_product_map, _product_to_id_map

    # إذا كان الفهرس موجودًا بالفعل في الذاكرة (من استدعاء سابق في نفس عملية الخادم)
    if _faiss_index is not None:
        print("الفهرس موجود بالفعل في الذاكرة، لن يتم إعادة تهيئته.")
        return

    # حاول تحميل الفهرس من القرص
    if load_faiss_index():
        return # تم التحميل بنجاح

    # إذا لم يتم التحميل، قم ببناء الفهرس من جميع المنتجات
    print("الفهرس غير موجود على القرص أو فشل التحميل، سيتم بناؤه من جميع المنتجات...")
    all_products = Handcraft.objects.all() # استرجاع جميع المنتجات
    embeddings_list = []
    product_ids_list = [] # لربط فهرس FAISS بـ Product ID

    for product in all_products:
        if not product.handcraft_image: # تخطي المنتجات بدون صور
            continue

        embedding = _get_embedding_for_image(product.handcraft_image.path)
        if embedding is not None:
            embeddings_list.append(embedding)
            product_ids_list.append(product.id) # إضافة Product ID

    if not embeddings_list:
        print("لا توجد منتجات بصور صالحة لبناء الفهرس.")
        _faiss_index = None
        _id_to_product_map = {}
        _product_to_id_map = {}
        return

    embeddings_array = np.array(embeddings_list)
    embedding_dim = embeddings_array.shape[1]

    # إنشاء فهرس FAISS مع معرفات مخصصة
    # IndexIDMap يأخذ فهرس base index (مثل IndexFlatL2)
    base_index = faiss.IndexFlatL2(embedding_dim)
    _faiss_index = faiss.IndexIDMap(base_index)
    _faiss_index.add_with_ids(embeddings_array, np.array(product_ids_list))

    # بناء خرائط product_id <> faiss_idx
    _id_to_product_map = {idx: product_id for idx, product_id in enumerate(product_ids_list)}
    _product_to_id_map = {product_id: idx for idx, product_id in enumerate(product_ids_list)}


    print(f"تم بناء فهرس FAISS بنجاح. عدد العناصر: {_faiss_index.ntotal}")
    save_faiss_index() # حفظ الفهرس بعد البناء الأولي


def add_product_to_faiss_index(product):
    """
    يضيف منتجاً واحداً إلى فهرس FAISS.
    """
    global _faiss_index, _id_to_product_map, _product_to_id_map

    # تأكد من تهيئة الفهرس أولاً
    init_faiss_index()

    if _faiss_index is None:
        print("الفهرس غير جاهز لإضافة المنتج.")
        return

    # إذا كان المنتج لديه صورة بالفعل وتمت فهرستها، قم بإزالتها أولاً (إن أمكن) أو تجاهلها
    if product.id in _product_to_id_map:
        # FAISS IndexFlatL2 و IndexIDMap لا يدعمان الإزالة المباشرة بسهولة
        # بالنسبة لـ IndexFlatL2، يجب أن تعيد بناء الفهرس بالكامل لإزالة عنصر
        # IndexIDMap يمكن أن تكون أكثر تعقيداً في إدارة الحذف الفعال
        # لغرض هذا التطبيق، إذا كان المنتج موجوداً، سنتجاهل إعادة إضافته.
        # إذا تغيرت الصورة، فستحتاج لإعادة بناء كاملة للفهرس يدوياً أو بجدولة
        print(f"المنتج ID {product.id} موجود بالفعل في الفهرس، لن تتم إضافته مرة أخرى.")
        return

    if not product.image:
        print(f"المنتج {product.id} ليس لديه صورة، لن تتم إضافته للفهرس.")
        return

    embedding = _get_embedding_for_image(product.image_path)
    if embedding is not None:
        # إضافة المتجه باستخدام product.id كـ ID
        _faiss_index.add_with_ids(np.array([embedding]), np.array([product.id]))

        # تحديث الخرائط
        _id_to_product_map[_faiss_index.ntotal - 1] = product.id # هذا قد لا يكون صحيحاً تماماً لـ IDMap
                                                              # IndexIDMap يستخدم IDs مباشرة
        _product_to_id_map[product.id] = _faiss_index.ntotal - 1 # هذا أيضاً غير دقيق لـ IDMap

        # الأفضل: عند استخدام IndexIDMap، الفهارس الداخلية هي Product IDs
        # لذا، لا حاجة لـ _id_to_product_map و _product_to_id_map بالشكل السابق
        # يكفي أن _faiss_index.add_with_ids() هي التي تربط Product ID مباشرة

        print(f"تمت إضافة المنتج ID {product.id} إلى فهرس FAISS. عدد العناصر: {_faiss_index.ntotal}")
        save_faiss_index() # حفظ الفهرس بعد الإضافة


@receiver(post_save, sender=Handcraft)
def product_post_save_handler(sender, instance, created, **kwargs):
    """
    يتم استدعاء هذه الوظيفة بعد حفظ/إنشاء منتج.
    تضيف المنتج الجديد إلى فهرس FAISS.
    """
    if created: # إذا تم إنشاء المنتج حديثاً
        print(f"Product {instance.id} created, adding to FAISS index.")
        add_product_to_faiss_index(instance)
    else: # إذا تم تحديث المنتج
        # هذا الجزء يتطلب معالجة خاصة.
        # إذا تغيرت صورة المنتج، فإن المتجه القديم لا يزال في الفهرس.
        # IndexFlatL2 لا يدعم الإزالة. IndexIDMap يدعم إعادة الإضافة بنفس ID
        # لكن لا يدعم التحديث الفعلي.
        # للتبسيط، في حالة التحديث، قد تحتاج إلى:
        # 1. إزالة المتجه القديم (صعب مع IndexFlatL2/IndexIDMap)
        # 2. إضافة المتجه الجديد
        # أو ببساطة: جدولة إعادة بناء كاملة للفهرس كل فترة لتنظيف هذه الحالات.
        print(f"Product {instance.id} updated. For now, manual index rebuild or soft deletion is needed for image changes.")
        # للحالة التي نريد فيها تحديث الفهرس فورًا عند تحديث الصورة
        # هذا سيعيد إضافة المنتج إذا تم تحديثه، وقد يؤدي إلى وجود إدخال قديم.
        # لحل هذه المشكلة بشكل كامل، قد نحتاج إلى مسح الفهرس وإعادة بنائه جزئياً
        # أو استخدام فهارس FAISS أكثر تقدماً.
        # حالياً، أفضل حل هو إعادة بناء كاملة مجدولة.
        # ولكن كحل مؤقت:
        # add_product_to_faiss_index(instance) # سيضيف المنتج مرة أخرى
        pass # نختار عدم القيام بأي شيء للتحديث الآن لتجنب التعقيد


@receiver(post_delete, sender=Handcraft)
def product_post_delete_handler(sender, instance, **kwargs):
    """
    يتم استدعاء هذه الوظيفة بعد حذف منتج.
    """
    global _faiss_index, _id_to_product_map, _product_to_id_map
    print(f"Product {instance.id} deleted. FAISS index will need a full rebuild to remove it completely.")
    # FAISS IndexFlatL2 لا يدعم الإزالة المباشرة.
    # IndexIDMap يدعم الإزالة
    # _faiss_index.remove_ids(np.array([instance.id]))
    # ولكن إزالة IDs من IndexIDMap قد تسبب مشاكل إذا لم تتم إدارتها بعناية.
    # الحل الأكثر أماناً هو إعادة بناء الفهرس بشكل دوري.
    # أو يمكننا عمل "soft delete" بحيث لا يظهر في نتائج البحث ولكن يبقى في الفهرس مؤقتًا.
    # save_faiss_index() # إذا تم تنفيذ إزالة

def search_similar_images(query_text=None, query_image=None, top_k=5): # <--- MODIFIED LINE
    global _faiss_index, _product_ids
    if _faiss_index is None:
        print("الفهرس غير مهيأ. لا يمكن إجراء البحث.")
        return []

    query_embedding = None
    if query_text:
        query_embedding = get_embedding_for_text(query_text)
    elif query_image: # Now it will correctly use query_image
        query_embedding = _get_embedding_for_image(query_image) # Make sure this calls the right image embedding function

    if query_embedding is None:
        return []

    # FAISS expects a 2D array (batch_size, vector_dim)
    query_embedding = np.array([query_embedding]).astype('float32')

    # البحث في الفهرس
    distances, indices = _faiss_index.search(query_embedding, top_k)

    results = []
    for i in indices[0]:
        if 0 <= i < len(_product_ids):
            product_id = _product_ids[i]
            try:
                # Make sure you import Handcraft at the top of utils.py if not already
                from handcrafts.models import Handcraft # <--- Add this import if missing
                product = Handcraft.objects.get(id=product_id)
                results.append({
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'image_url': product.handcraft_image.url if product.handcraft_image else None
                })
            except Handcraft.DoesNotExist:
                print(f"تحذير: المنتج ذو المعرف {product_id} غير موجود في قاعدة البيانات.")
                continue
    return results

# ... (rest of
# def search_similar_images(query_input, top_k=4, threshold=150):
    # """
    # وظيفة البحث الرئيسية المستخدمة في الـ View.
    # تقبل استعلام نصي أو صورة.
    # """
    # model = get_sentence_transformer_model()
    # init_faiss_index() # تأكد من تهيئة الفهرس

    # if _faiss_index is None or _faiss_index.ntotal == 0:
    #     return {"error": "فهرس البحث غير جاهز أو فارغ."}, []

    # query_embedding = None
    # if isinstance(query_input, Image.Image):
    #     query_input = query_input.convert("RGB")
    #     query_embedding = model.encode(query_input)
    # elif isinstance(query_input, str) and query_input.strip():
    #     query_embedding = model.encode(query_input)
    # else:
    #     return {"error": "يرجى تقديم صورة أو نص للاستعلام."}, []

    # D, I = _faiss_index.search(np.array([query_embedding]), k=top_k)

    # results = []
    # # I[0] الآن يحتوي على Product IDs مباشرة (إذا استخدمت IndexIDMap بشكل صحيح)
    # for i, product_id in enumerate(I[0]):
    #     distance = D[0][i]
    #     if distance < threshold:
    #         try:
    #             # استرجاع كائن Product من قاعدة البيانات باستخدام Product ID
    #             product = Handcraft.objects.get(id=product_id)
    #             results.append({
    #                 'product_id': product.id,
    #                 'name': product.handcraft_name,
    #                 'image_url': product.handcraft_image.url,
    #                 'distance': float(distance)
    #             })
    #         except Handcraft.DoesNotExist:
    #             print(f"تحذير: المنتج ID {product_id} لم يعد موجوداً في قاعدة البيانات.")
    #             # هذا يحدث إذا تم حذف منتج ولم يتم إعادة بناء الفهرس
    #             continue

    # return {"results": results, "query_embedding": query_embedding.tolist()}, results