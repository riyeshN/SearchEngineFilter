import json
from typing import List

from searchFilter.DataInsertAndAccess.SearchQueryAdd import SearchQueryAdd
from django.http import JsonResponse
from . import RequestHandler, SearchEngineStrategy, SearchUrl
from ..models import SearchUrls, UrlData


class DataScraper:

    @staticmethod
    def get_html_from_urls(keyword : str = None):
        print(f"Getting HTML content for {keyword}")

        request_handler = RequestHandler.RequestHandler()

        results = DataScraper.get_list_of_search_urls(keyword = keyword)
        return_results = DataScraper.parse_list_of_searches_and_populate_url_data(rows = results, request_handler = request_handler)
        return_val = [
            {
                "id" : url_data.id,
                "searchUrls": {
                    "id": url_data.searchUrls.id,
                    "url": url_data.searchUrls.url,
                    "title": url_data.searchUrls.title,
                    "desc": url_data.searchUrls.desc
                },
                "count" : url_data.count_of_appearance
            } for url_data in return_results
        ]
        return JsonResponse({
            "success": True,
            "urls": return_val
        })

    @staticmethod
    def parse_list_of_searches_and_populate_url_data(rows : List[SearchUrls], request_handler) -> List[UrlData]:
        results: List[UrlData] = []
        for row in rows:
            if not row.ad and not row.data_scrape_time:
                html = request_handler.get(row.url)
                url_data = DataScraper.add_html_to_table(html=html, row=row)
                results.append(url_data)
        return results

    @staticmethod
    def add_html_to_table(html : str, row : SearchUrls)  -> UrlData:
        url_data = SearchQueryAdd.add_url_html_data(html=html, row=row)
        return url_data

    @staticmethod
    def get_list_of_search_urls(keyword : str = None):
        query = ""
        if keyword:
            query = f"""
                 WITH ID_TO_SEARCH AS (
            	        SELECT a.* from searchFilter_searchtermmapping a JOIN 
                            (
                                SELECT searchTerm, searchEngineName_id, MAX(time_searched) AS max_time
                                FROM searchFilter_searchtermmapping
                                GROUP BY searchTerm, searchEngineName_id
                            ) b 
                            ON a.searchTerm = b.searchTerm and a.searchEngineName_id =b.searchEngineName_id 
                            and a.time_searched = b.max_time and a.searchTerm = %s
                )SELECT * from searchFilter_searchurls where id in (select id from ID_TO_SEARCH)
            """
            latest_entry = SearchUrls.objects.raw(query, [keyword])
        else:
            query = """
                    WITH ID_TO_SEARCH AS (
            	        SELECT a.* from searchFilter_searchtermmapping a JOIN 
                            (
                                SELECT searchTerm, searchEngineName_id, MAX(time_searched) AS max_time
                                FROM searchFilter_searchtermmapping
                                GROUP BY searchTerm, searchEngineName_id
                            ) b 
                            ON a.searchTerm = b.searchTerm and a.searchEngineName_id =b.searchEngineName_id 
                            and a.time_searched = b.max_time 
                    )SELECT * from searchFilter_searchurls where id in (select id from ID_TO_SEARCH)
                    """
            latest_entry = SearchUrls.objects.raw(query)
        results = []

        for row in latest_entry:
            results.append(row)
        return results

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

