"""
URL configuration for handmake project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('admins/',include('admin.urls')),
    path('maker/',include('maker.urls')),
    path('customers/',include('customers.urls')),
    path('categories/',include('categories.urls')),
    path('reset/',include('users.urls')),
    path('handcraft/',include('handcrafts.urls')),
    path('rating/',include('rating.urls')),
    path('comment/',include('comment.urls')),
    path('discount/',include('discount.urls')),
    path('order/',include('order.urls')),
    path('ml_model/', include('ml_model.urls')),
    path('auctions/', include('auction.urls')),
]+ static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)
