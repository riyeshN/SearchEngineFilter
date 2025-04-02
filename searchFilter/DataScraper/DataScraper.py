from django.http import JsonResponse
from . import RequestHandler, SearchEngineStrategy, SearchUrl

class DataScraper:

    @staticmethod
    def get_urls(keyword : str, url_size : int):
        print(f"Getting searches for {keyword} total urls: {url_size}")
        request_handler = RequestHandler.RequestHandler()
        google_strategy = SearchEngineStrategy.GoogleSearchStrategy()
        search_urls = SearchUrl.SearchUrls(strategy=google_strategy, request_handle=request_handler)

        try:
            found_urls = search_urls.search(keyword, url_size)
            return JsonResponse({
                "success": True,
                "urls": found_urls
            })
        except Exception as e:
            return JsonResponse({
                "success" : False,
                "error": str(e)
            })

