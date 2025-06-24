# image_search/management/commands/rebuild_faiss_index.py
from django.core.management.base import BaseCommand
# import image_search.utils as faiss_utils  # هذا السطر السابق كان خطأ، يجب أن يكون هكذا:
from image_search import utils as faiss_utils # هذا هو الاستيراد الصحيح للوحدة
from handcrafts.models import Handcraft
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from PIL import Image
import os
import pickle # للاستخدام مع pickle.dump/load

class Command(BaseCommand):
    help = 'Rebuilds the FAISS index from all product images in the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("بدء إعادة بناء فهرس FAISS بالكامل..."))

        # استخدم الدالة من utils.py لتحميل النموذج
        model = faiss_utils.get_sentence_transformer_model()

        all_products = Handcraft.objects.all()
        embeddings_list = []
        product_ids_list = []

        for product in all_products:
            if not product.handcraft_image:
                continue
            image_path = product.handcraft_image.path
            if not os.path.exists(image_path):
                self.stdout.write(self.style.WARNING(f"تحذير: صورة المنتج {product.id} غير موجودة: {image_path}"))
                continue
            try:
                image = Image.open(image_path).convert("RGB")
                embedding = model.encode(image)
                embeddings_list.append(embedding)
                product_ids_list.append(product.id)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"خطأ في معالجة صورة المنتج {product.id}: {e}"))
                continue

        if not embeddings_list:
            self.stdout.write(self.style.WARNING("لا توجد منتجات بصور صالحة لبناء الفهرس."))
            # يجب مسح الفهرس القديم هنا إذا كان فارغاً
            if os.path.exists(faiss_utils.FAISS_INDEX_FILE): # <-- تم التعديل هنا
                os.remove(faiss_utils.FAISS_INDEX_FILE)    # <-- وتم التعديل هنا
            if os.path.exists(faiss_utils.FAISS_METADATA_FILE): # <-- وتم التعديل هنا
                os.remove(faiss_utils.FAISS_METADATA_FILE) # <-- وتم التعديل هنا
            return

        embeddings_array = np.array(embeddings_list)
        embedding_dim = embeddings_array.shape[1]

        base_index = faiss.IndexFlatL2(embedding_dim)
        new_faiss_index = faiss.IndexIDMap(base_index)
        new_faiss_index.add_with_ids(embeddings_array, np.array(product_ids_list))

        try:
            faiss.write_index(new_faiss_index, faiss_utils.FAISS_INDEX_FILE) # <-- تم التعديل هنا
            with open(faiss_utils.FAISS_METADATA_FILE, 'wb') as f:         # <-- وتم التعديل هنا
                pickle.dump({
                    'id_to_product_map': {idx: product_id for idx, product_id in enumerate(product_ids_list)},
                    'product_to_id_map': {product_id: idx for idx, product_id in enumerate(product_ids_list)}
                }, f)
            self.stdout.write(self.style.SUCCESS(f"تمت إعادة بناء وحفظ فهرس FAISS بنجاح. عدد العناصر: {new_faiss_index.ntotal}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"خطأ في حفظ الفهرس بعد إعادة البناء: {e}"))

        # إعادة تعيين المتغيرات العالمية في utils.py
        faiss_utils._faiss_index = None # <-- تم التعديل هنا
        faiss_utils._id_to_product_map = {} # <-- تم التعديل هنا
        faiss_utils._product_to_id_map = {} # <-- تم التعديل هنا
        
