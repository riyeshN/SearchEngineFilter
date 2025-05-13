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

        # Track ads and organic results separately to ensure we return a mix
        organic_results = []
        ad_promo_results = []

        while len(results) < 250:
            search_urls = self.strategy.build_search_url(keyword)
            url = ""
            if type(self.strategy) == SearchEngineStrategy.GoogleSearchStrategy:
                url = f"{search_urls}&start={start_page}"
            if type(self.strategy) == SearchEngineStrategy.BingSearchStrategy:
                url = f"{search_urls}&first={start_page + 1}"
            if type(self.strategy) == SearchEngineStrategy.DuckDuckGoSearchStrategy:
                # For first page, no parameter needed
                if start_page == 0:
                    url = search_urls
                else:
                    # DuckDuckGo HTML version uses 's' parameter with increments of 30
                    url = f"{search_urls}&s={start_page * 3}"  # 30 results per page, adjust if needed

            if type(self.strategy) == SearchEngineStrategy.YahooSearchStrategy:
                url = f"{search_urls}&first={start_page + 1}"

            print(f"Fetching: {url}")
            html = self.request_handle.get(url)
            page_results = self.strategy.parse_results(html)

            # Separate the results into ads/promos and organic
            for result in page_results:
                if result.get("ad_promo", False):
                    ad_promo_results.append(result)
                else:
                    organic_results.append(result)

            # Add all results to the main list
            results.extend(page_results)

            # Stop if we've reached the desired total.
            if len(results) >= total_results or starting_size == len(results):
                break

            print(f"In page - {start_page} - size: {len(results)}")
            time.sleep(1)  # small delay to be more human-like
            start_page += 10
            starting_size = len(results)

        # Prepare the final results - prioritize including some ads
        final_results = []

        # Make sure we include ads/promos in the final results
        ad_count = min(len(ad_promo_results), total_results // 3)  # Use up to 1/3 of the slots for ads
        if ad_count > 0:
            print(f"Including {ad_count} ads/promos in the final results")
            final_results.extend(ad_promo_results[:ad_count])

        # Fill the rest with organic results
        organic_count = total_results - len(final_results)
        final_results.extend(organic_results[:organic_count])

        # Shuffle the results to mix ads and organic (optional)
        # random.shuffle(final_results)

        print(f"Final results: {len(final_results)} total, {ad_count} ads/promos")
        return final_results