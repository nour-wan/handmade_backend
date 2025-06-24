# image_search/urls.py
from django.urls import path
from . import views

app_name = 'image_search' # لتسمية التطبيق

urlpatterns = [
    # المسار الرئيسي للتطبيق (مثل /search/)
    path('', views.search_view, name='search'),

    # المسار لرفع الصور إذا قررت الاحتفاظ به
    # ملاحظة: إذا كنت تعتمد فقط على الصور الموجودة في MEDIA_ROOT،
    # فقد لا تحتاج إلى هذه الـ View الخاصة بالرفع.
    # ولكن إذا أردت وظيفة لرفع صور جديدة إلى MEDIA_ROOT عبر Django، فستحتاجها.
    path('upload/', views.upload_image_view, name='upload_image'),
]