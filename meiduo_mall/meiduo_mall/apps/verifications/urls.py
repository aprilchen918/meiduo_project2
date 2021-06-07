from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),
    url(r'^sms_codes/(?P<mobile>\d{10})/$', views.SMSCodeView.as_view()),
]