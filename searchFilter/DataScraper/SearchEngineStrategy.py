from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import urllib.parse

class SearchEngineStrategy(ABC):

    @abstractmethod
    def build_search_url(self, keyword: str) -> str:
        pass

    @abstractmethod
    def parse_results(self, html_content: str) -> list:
        pass


class GoogleSearchStrategy(SearchEngineStrategy):

    def build_search_url(self, keyword: str) -> str:
        base_url = "https://www.google.com/search"
        if isinstance(keyword, bytes):
            keyword = keyword.decode('utf-8')
        # Encode the keyword properly for URL usage.
        query = urllib.parse.quote_plus(keyword)
        return f"{base_url}?q={query}"

    def parse_results(self, html_content: str) -> list:
        results = []
        soup = BeautifulSoup(html_content, "html.parser")
        container = soup.find("div", {"id": "rso"})
        if not container:
            return results

        for item in container.find_all("div", class_="yuRUbf"):
            link_tag = item.find("a")
            link = link_tag.get("href") if link_tag else None

            title_tag = item.find("h3")
            title = title_tag.text if title_tag else None

            desc_tag = item.find("div", class_="VwiC3b")
            description = desc_tag.text if desc_tag else None

            is_ad = False
            ad_marker = item.find("span")
            if ad_marker and ad_marker.text.strip().lower() in ["ad", "sponsored"]:
                is_ad = True

            results.append({
                "title": title,
                "link": link,
                "description": description,
                "is_ad": is_ad
            })
        return results

