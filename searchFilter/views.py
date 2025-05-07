from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .DataScraper import DataScraper
# Create your views here.
def index(request) :
    keyword = request.GET.get("keyword", "")
    if not keyword:
        return JsonResponse({
            "success": False,
            "error": "No keyword provided"
        })
    url_size_param = request.GET.get("url_size", "")
    try:
        url_size = int(url_size_param) if url_size_param else 10
    except ValueError:
        return JsonResponse({
            "success": False,
            "error": " Invalid size provided"
        })

    return DataScraper.DataScraper.get_urls(keyword, url_size)

def get_html_data(request) :
    keyword = request.GET.get("keyword", "")
    if keyword:
        return DataScraper.DataScraper.get_html_from_urls(keyword=keyword)
    else:
        return DataScraper.DataScraper.get_html_from_urls()
