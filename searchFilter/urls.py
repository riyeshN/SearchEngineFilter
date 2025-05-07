from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('get_html_data', views.get_html_data, name = "get_html_data"),
]