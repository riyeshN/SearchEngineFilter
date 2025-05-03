from searchFilter.DataInsertAndAccess.SearchQueryAdd import SearchQueryAdd
from django.http import JsonResponse
from . import RequestHandler, SearchEngineStrategy, SearchUrl

class DataScraper:

    @staticmethod
    def get_urls(keyword : str, url_size : int):
        print(f"Getting searches for {keyword} total urls: {url_size}")

        request_handler = RequestHandler.RequestHandler()

        google_strategy = SearchEngineStrategy.GoogleSearchStrategy()
        bing_strategy = SearchEngineStrategy.BingSearchStrategy()

        search_urls = SearchUrl.SearchUrls(strategy=google_strategy, request_handle=request_handler)
        search_bing_url = SearchUrl.SearchUrls(strategy=bing_strategy, request_handle=request_handler)

        list_of_engine_search = [search_urls, search_bing_url ]

        try:
            found_urls = list()
            for curr in list_of_engine_search:
                found_urls.append(curr.search(keyword, url_size))

            SearchQueryAdd.add_search_results(keyword, found_urls)
            return JsonResponse({
                "success": True,
                "urls": found_urls
            })
        except Exception as e:
            return JsonResponse({
                "success" : False,
                "error": str(e)
            })

