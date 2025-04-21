from functools import total_ordering
import time
from . import SearchEngineStrategy, RequestHandler

class SearchUrls:

    def __init__(self, strategy: SearchEngineStrategy, request_handle: RequestHandler):
        self.strategy = strategy
        self.request_handle = request_handle

    def search(self, keyword: str, total_results: int) -> list:
        return self.get_search_results(keyword=keyword, total_results=total_results)

    def get_search_results(self, keyword: str, total_results: int = 300) -> list:
        results = []
        start_page = 0
        starting_size = 0
        while len(results) < 250:

            search_urls = self.strategy.build_search_url(keyword)
            url = ""
            if type(self.strategy) == SearchEngineStrategy.GoogleSearchStrategy:
                url = f"{search_urls}&start={start_page}"
            if type(self.strategy) == SearchEngineStrategy.BingSearchStrategy:
                url = f"{search_urls}&first={start_page + 1}"
            print(f"Fetching: {url}")
            html = self.request_handle.get(url)
            page_results = self.strategy.parse_results(html)
            results.extend(page_results)
            # Stop if we've reached the desired total.
            if len(results) >= total_results or starting_size == len(results):
                break
            print(f"In page - {start_page} - size: {len(results)}")
            time.sleep(1)  # small delay to be more human-like
            start_page += 10
            starting_size = len(results)
        return results[:total_results]