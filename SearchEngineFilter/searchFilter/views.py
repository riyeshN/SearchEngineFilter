from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .DataInsertAndAccess.GetSQLData import GetSQLData
from .DataScraper import DataScraper


# Create your views here.
def index(request):
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


def get_html_data(request):
    keyword = request.GET.get("keyword", "")
    if keyword:
        return DataScraper.DataScraper.get_html_from_urls(keyword=keyword)
    else:
        return DataScraper.DataScraper.get_html_from_urls()


def get_list_of_links_for_keyword(request):
    keyword = request.GET.get("keyword", "")
    if not keyword:
        return JsonResponse({
            "success": False,
            "error": "No keyword provided"
        })
    try:
        list_of_links = GetSQLData.get_list_of_links_for_keyword(keyword=keyword)

        # Debug: Print ad_promo values
        ad_count = sum(1 for link in list_of_links if link.get('ad_promo'))
        print(f"Found {len(list_of_links)} links, {ad_count} ads/promos")
        for link in list_of_links[:5]:  # Print the first 5 for debugging
            print(f"Link: {link.get('title')} - ad_promo: {link.get('ad_promo')}")

        return JsonResponse({
            "success": True,
            "data": list_of_links
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Exception - {e}"
        })

def get_list_of_ads_none_ads(request):
    keyword = request.GET.get("keyword", "")
    if not keyword:
        return JsonResponse({
            "success": False,
            "error": "No keyword provided"
        })
    try:
        list_of_links = GetSQLData.get_list_of_ads_none_ads(keyword=keyword)
        return JsonResponse({
            "success": True,
            "data": list_of_links
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Exception - {e}"
        })