from django.urls import path
from . import views
urlpatterns = [
    path('',views.DiscountList.as_view()),
    path('<int:pk>',views.DiscountDetail.as_view()),
    path('ToMaker',views.DiscountListToMaker.as_view()),
    path('addHandcraft',views.DiscountHandcraftPost.as_view()),
    path('deleteHandFromDiscount/<int:dis>/<int:hand>',views.DiscountHandcraftDelete.as_view()),
    # path('create',views.create),
    # path('getAll',views.getAll),
    # path('update/<id>',views.update),
    # path('delete/<id>',views.delete),
]