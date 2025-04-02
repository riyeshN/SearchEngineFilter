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
        # Google returns 10 results per page.
        results_per_page = 10
        num_pages = (total_results // results_per_page) + (1 if total_results % results_per_page else 0)

        for page in range(num_pages):
            start = page * results_per_page
            search_urls = self.strategy.build_search_url(keyword)
            url = f"{search_urls}&start={start}"
            print(f"Fetching: {url}")
            html = self.request_handle.get(url)
            page_results = self.strategy.parse_results(html)
            results.extend(page_results)
            # Stop if we've reached the desired total.
            if len(results) >= total_results:
                break
            print(f"In page - {page} - size: {len(results)}")
            time.sleep(1)  # small delay to be more human-like
        return results[:total_results]