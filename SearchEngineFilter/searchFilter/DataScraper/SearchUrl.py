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
        seen_links = set()
        start_page = 0
        starting_size = 0

        while len(results) < 250:
            search_urls = self.strategy.build_search_url(keyword)

            if isinstance(self.strategy, SearchEngineStrategy.GoogleSearchStrategy):
                url = f"{search_urls}&start={start_page}"
            elif isinstance(self.strategy, SearchEngineStrategy.BingSearchStrategy):
                url = f"{search_urls}&first={start_page + 1}"
            elif isinstance(self.strategy, SearchEngineStrategy.DuckDuckGoSearchStrategy):
                url = search_urls if start_page == 0 else f"{search_urls}&s={start_page * 3}"
            elif isinstance(self.strategy, SearchEngineStrategy.YahooSearchStrategy):
                url = f"{search_urls}&first={start_page + 1}"
            else:
                url = search_urls

            print(f"Fetching: {url}")
            html = self.request_handle.get(url)
            page_results = self.strategy.parse_results(html)

            for result in page_results:
                link = result.get("link")
                ad_promo = result.get("ad_promo")
                if (not link or link in seen_links) and ad_promo:
                    continue

                seen_links.add(link)
                #
                # if result.get("ad_promo", False):
                #     ad_promo_results.append(result)
                # else:
                #     organic_results.append(result)

                results.append(result)

            if len(results) >= total_results or starting_size == len(results):
                break

            print(f"In page - {start_page} - size: {len(results)}")
            time.sleep(1)
            start_page += 10
            starting_size = len(results)

        # final_results = []
        # ad_count = min(len(ad_promo_results), total_results // 3)

        # if ad_count > 0:
        #     print(f"Including {ad_count} ads/promos in the final results")
        #     final_results.extend(ad_promo_results[:ad_count])
        #
        # organic_count = total_results - len(final_results)
        # final_results.extend(organic_results[:organic_count])
        #
        # print(f"Final results: {len(final_results)} total, {ad_count} ads/promos")
        return results