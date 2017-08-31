"""aggregaattori URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

from stories.api import APIRouter
from stories.views import import_activity_stream

admin.autodiscover()

router = APIRouter()


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^v1/', include(router.urls)),
    url(r'^v1/activity_stream/', import_activity_streams),
    url(r'^$', RedirectView.as_view(url='v1/'))
]
