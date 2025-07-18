"""
URL configuration for sysprobi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from sysswkd import views as swkdview

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', swkdview.index, name='index'),
    path('invmovement_test',swkdview.invmovements_view, name='invmovement_test'),
    path('invmovement',swkdview.invmovements, name='invmovement'),
    path('test',swkdview.testmove, name='test'),
    path('sales-analytic',swkdview.sale_analytic, name='sales-analytic')
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)