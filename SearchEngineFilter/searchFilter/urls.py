from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('get_html_data', views.get_html_data, name = "get_html_data"),
    path('get_list_of_links_for_keyword', views.get_list_of_links_for_keyword, name = "get_list_of_links_for_keyword"),
    path('get_list_of_ads_none_ads', views.get_list_of_ads_none_ads, name = "get_list_of_ads_none_ads"),
    path('get_list_of_dups', views.get_list_of_dups, name = "get_list_of_dups")
]