import urllib.parse
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urlparse, parse_qs, unquote, urljoin

class SearchEngineStrategy(ABC):

    @abstractmethod
    def build_search_url(self, keyword: str) -> str:
        pass

    @abstractmethod
    def parse_results(self, html_content: str) -> list:
        pass

class BingSearchStrategy(SearchEngineStrategy):

    def build_search_url(self, keyword: str) -> str:
        base_url = "https://www.bing.com/search"
        if isinstance(keyword, bytes):
            keyword = keyword.decode('utf-8')
        # Encode the keyword properly for URL usage.
        query = urllib.parse.quote_plus(keyword)
        return f"{base_url}?q={query}"

    def parse_results(self, html_content: str) -> list:
        soup = BeautifulSoup(html_content, "html.parser")
        results = []
        BASE = "https://www.bing.com"

        def _clean_href(href: Optional[str]) -> Optional[str]:
            if not href:
                return None
            if href.startswith("/"):
                href = urljoin(BASE, href)
            p = urlparse(href)
            if p.netloc == "www.bing.com" and p.path == "/aclick":
                q = parse_qs(p.query)
                for key in ("u", "r"):
                    if key in q:
                        return unquote(q[key][0])
            return href

        for li in soup.select("#b_results > li"):
            cls = li.get("class", [])
            kind = ("ad" if any("b_ad" in c for c in cls)
                    else "promo" if any("b_ans" in c for c in cls)
            else "organic")

            # title / link / desc
            h2 = li.find("h2")
            a = h2.find("a", href=True) if h2 else li.find("a", href=True)
            para = li.find("p")

            title = (h2.get_text(strip=True) if h2 and h2.get_text(strip=True)
                     else a.get_text(strip=True) if a else None)
            link = _clean_href(a["href"]) if a else None
            desc = para.get_text(strip=True) if para else None

            if title:
                if title in {"Previous", "Next"} or title.startswith("Related searches"):
                    continue
                print(f"[{kind.upper()}] title: {title}  --  link: {link}")

                if title and link and desc:
                    results.append({
                        "searchEngine": "Bing",
                        "baseUrl": BASE,
                        "title": title,
                        "link": link,
                        "description": desc,
                        "is_ad": kind == "ad",
                        "is_promo": kind == "promo",
                    })

        return results

class GoogleSearchStrategy(SearchEngineStrategy):

    def build_search_url(self, keyword: str) -> str:
        base_url = "https://www.google.com/search"
        if isinstance(keyword, bytes):
            keyword = keyword.decode('utf-8')
        # Encode the keyword properly for URL usage.
        query = urllib.parse.quote_plus(keyword)
        return f"{base_url}?q={query}"

    def parse_results(self, html_content: str) -> list:
        """Return organic, ad, and promo results with clean title / link text;
        also prints each row for quick debugging."""
        soup = BeautifulSoup(html_content, "html.parser")
        results = []
        BASE = "https://www.google.com"

        def _clean_href(href: Optional[str]) -> Optional[str]:
            if not href:
                return None
            if href.startswith("/"):
                href = urljoin(BASE, href)
            if href.startswith("/url"):
                return parse_qs(urlparse(href).query).get("q", [href])[0]
            return href

        # ── 1. organic ────────────────────────────────────────────────────────
        for item in soup.select("#rso .yuRUbf"):
            title_tag = item.find("h3")
            link_tag = item.find("a", href=True)
            desc_tag = item.find_next("div", class_="VwiC3b")

            title = title_tag.get_text(strip=True) if title_tag else None
            link = _clean_href(link_tag["href"]) if link_tag else None
            desc = desc_tag.get_text(strip=True) if desc_tag else None

            if title and link and desc:
                print(f"ORG  title: {title}  --  link: {link}")
                results.append({
                    "searchEngine": "Google",
                    "baseUrl": BASE,
                    "title": title,
                    "link": link,
                    "description": desc,
                    "is_ad": False,
                    "is_promo": False,
                })

        # ── 2. ads ────────────────────────────────────────────────────────────
        ad_selector = (
            "#tads .uEierd, #taw .uEierd, "
            "#tads [data-text-ad], #taw [data-text-ad], "
            "div[aria-label='Ads'] *, div[aria-label='Sponsored'] *"
        )
        for item in soup.select(ad_selector):
            title_tag = item.find("h3")
            link_tag = item.find("a", href=True)
            desc_tag = item.find("div", class_="MUxGbd") or item.find("div", class_="VwiC3b")

            title = title_tag.get_text(strip=True) if title_tag else None
            link = _clean_href(link_tag["href"]) if link_tag else None
            desc = desc_tag.get_text(strip=True) if desc_tag else None

            if title and link and desc:
                print(f"AD   title: {title}  --  link: {link}  ")
                results.append({
                    "searchEngine": "Google",
                    "baseUrl": BASE,
                    "title": title,
                    "link": link,
                    "description": desc,
                    "is_ad": True,
                    "is_promo": False,
                })

        # ── 3. promos / rich blocks ───────────────────────────────────────────
        promo_selector = (
            ".kp-blk, .g-blk, .FLP8od, "
            ".xpdopen, .VkpGBb, "
            "[data-content-feature='1']"
        )
        for item in soup.select(promo_selector):
            title_tag = item.find("h3")
            link_tag = item.find("a", href=True)
            if not (title_tag and link_tag):
                continue
            desc_tag = item.find("div", class_="MUxGbd") or item.find("div", class_="VwiC3b")

            title = title_tag.get_text(strip=True)
            link = _clean_href(link_tag["href"])
            desc = desc_tag.get_text(strip=True) if desc_tag else None

            if title and link and desc:

                print(f"PROM title: {title}  --  link: {link}")
                results.append({
                    "searchEngine": "Google",
                    "baseUrl": BASE,
                    "title": title,
                    "link": link,
                    "description": desc,
                    "is_ad": False,
                    "is_promo": True,
                })

        return results

