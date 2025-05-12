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
                        "is_ad_promo": False,
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

            # ── 1. Organic results ──────────────────────────────
        for item in soup.select(".MjjYud .yuRUbf"):
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
                    "is_ad_promo": False,
                })

        # ── 2. Ads ─────────────────────────────────────────
        ad_blocks = soup.select("div[aria-label='Ads'] a.sVXRqc")
        for a in ad_blocks:
            title = a.get_text(strip=True)
            link = _clean_href(a.get("href"))
            # Try to find description in parent or next sibling
            desc_tag = a.find_parent().find_next("div", class_="VwiC3b")
            desc = desc_tag.get_text(strip=True) if desc_tag else ""

            if title and link:
                print(f"AD   title: {title}  --  link: {link}")
                results.append({
                    "searchEngine": "Google",
                    "baseUrl": BASE,
                    "title": title,
                    "link": link,
                    "description": desc,
                    "is_ad_promo": False,
                })

        # ── 3. Promos ──────────────────────────────────────
        promo_selectors = [".xpdopen", ".kp-blk", ".VkpGBb", ".FLP8od"]
        for selector in promo_selectors:
            for item in soup.select(selector):
                # Attempt to get standard title and description
                title_tag = item.find("h3")
                desc_tag = item.find("div", class_="VwiC3b")

                # Try any anchor with a valid link
                link_tag = item.find("a", href=True)
                link = _clean_href(link_tag["href"]) if link_tag else None

                # Fallback title if no <h3>
                title = (
                    title_tag.get_text(strip=True) if title_tag
                    else item.get_text(" ", strip=True).strip()
                )

                # Fallback desc (skip if totally empty)
                desc = (
                    desc_tag.get_text(strip=True) if desc_tag
                    else None
                )

                if title and link:
                    print(f"PROM title: {title}  --  link: {link}")
                    results.append({
                        "searchEngine": "Google",
                        "baseUrl": BASE,
                        "title": title,
                        "link": link,
                        "description": desc or "",
                        "is_ad_promo": False,
                    })

        return results

class DuckDuckGoSearchStrategy(SearchEngineStrategy):
    def build_search_url(self, keyword: str) -> str:
        base_url = "https://duckduckgo.com/html/"
        if isinstance(keyword, bytes):
            keyword = keyword.decode('utf-8')
        query = urllib.parse.quote_plus(keyword)
        return f"{base_url}?q={query}"

    def parse_results(self, html_content: str) -> list:
        soup = BeautifulSoup(html_content, "html.parser")
        results = []
        BASE = "https://duckduckgo.com"

        def _clean_href(href: Optional[str]) -> Optional[str]:
            if not href:
                return None
            if href.startswith("/"):
                href = urljoin(BASE, href)
            if href.startswith("/l/?uddg="):
                return unquote(href.split("uddg=")[1].split("&")[0])
            return href

        # Organic results
        # attempt change
        # for item in soup.select("article[data-testid='result']"):
        #     title_tag = item.find("h2")
        #     link_tag = title_tag.find("a", href=True) if title_tag else None
        #     desc_tag = item.find("div", class_="C1r0kB6hBP3a4dE1jPK3dw")
        #
        #     title = title_tag.get_text(strip=True) if title_tag else None
        #     link = _clean_href(link_tag["href"]) if link_tag else None
        #     desc = desc_tag.get_text(strip=True) if desc_tag else None

            # HTML version uses a simpler structure with CSS class "result"
        for result in soup.select(".result"):
            title_link = result.select_one(".result__a")
            desc_elem = result.select_one(".result__snippet")

            title = title_link.get_text(strip=True) if title_link else None
            link = _clean_href(title_link["href"]) if title_link and title_link.has_attr("href") else None
            desc = desc_elem.get_text(strip=True) if desc_elem else None

            if title and link and desc:
                print(f"ORG  title: {title}  --  link: {link}")
                results.append({
                    "searchEngine": "DuckDuckGo",
                    "baseUrl": BASE,
                    "title": title,
                    "link": link,
                    "description": desc,
                    "is_ad_promo": False,
                })

        # For ads
        for item in soup.select("div[data-testid='ad']"):
            title_tag = item.find("a", attrs={"data-testid": "ad-title"})
            link_tag = title_tag if title_tag else None
            desc_tag = item.find("div", class_="ad__desc")

            title = title_tag.get_text(strip=True) if title_tag else None
            link = _clean_href(link_tag["href"]) if link_tag else None
            desc = desc_tag.get_text(strip=True) if desc_tag else None

            if title and link and desc:
                print(f"AD   title: {title}  --  link: {link}")
                results.append({
                    "searchEngine": "DuckDuckGo",
                    "baseUrl": BASE,
                    "title": title,
                    "link": link,
                    "description": desc,
                    "is_ad_promo": False,
                })

        # Promotions
        for item in soup.select("div[data-testid='zci']"):
            title_tag = item.find("h2")
            link_tag = item.find("a", href=True)
            desc_tag = item.find("div", class_="zci__content")

            title = title_tag.get_text(strip=True) if title_tag else None
            link = _clean_href(link_tag["href"]) if link_tag else None
            desc = desc_tag.get_text(strip=True) if desc_tag else None

            if title and link and desc:
                print(f"PROM title: {title}  --  link: {link}")
                results.append({
                    "searchEngine": "DuckDuckGo",
                    "baseUrl": BASE,
                    "title": title,
                    "link": link,
                    "description": desc,
                    "is_ad_promo": False,
                })

        return results


class YahooSearchStrategy(SearchEngineStrategy):

    def build_search_url(self, keyword: str) -> str:
        base_url = "https://search.yahoo.com/search"
        if isinstance(keyword, bytes):
            keyword = keyword.decode('utf-8')
        query = urllib.parse.quote_plus(keyword)
        return f"{base_url}?p={query}"

    def parse_results(self, html_content: str) -> list:
        soup = BeautifulSoup(html_content, "html.parser")
        results = []
        BASE = "https://search.yahoo.com"

        def _clean_href(href: Optional[str]) -> Optional[str]:
            if not href:
                return None
            if href.startswith("/"):
                href = urljoin(BASE, href)
            if "r.search.yahoo.com" in href:
                parts = href.split("/RU=")
                if len(parts) > 1:
                    return unquote(parts[1].split("/")[0])
            return href

        # Organic results
        for item in soup.select("#web .algo"):
            title_tag = item.find("h3")
            link_tag = item.find("a", href=True)

            # Updated selector for description - look for paragraph elements with multiple possible classes
            desc_tag = item.find("p",
                                 class_=lambda c: c and any(cls in c for cls in ["s-desc", "fc-dustygray", "compText"]))
            if not desc_tag:
                # Fallback: look for any paragraph in the item
                desc_tag = item.find("p")

            # Also try the compText div which might contain the description
            if not desc_tag:
                comp_text = item.find("div", class_="compText")
                if comp_text:
                    desc_tag = comp_text.find("p")

            title = title_tag.get_text(strip=True) if title_tag else None
            link = _clean_href(link_tag["href"]) if link_tag else None
            desc = desc_tag.get_text(strip=True) if desc_tag else None

            if title and link:  # Make description optional
                print(f"ORG  title: {title}  --  link: {link}")
                results.append({
                    "searchEngine": "Yahoo",
                    "baseUrl": BASE,
                    "title": title,
                    "link": link,
                    "description": desc or "",  # Use empty string if no description
                    "is_ad_promo": False,
                })

        # For ads - similar updates for description extraction
        for item in soup.select("#web .ad"):
            title_tag = item.find("h3")
            link_tag = item.find("a", href=True)
            desc_tag = item.find("p",
                                 class_=lambda c: c and any(cls in c for cls in ["s-desc", "fc-dustygray", "compText"]))
            if not desc_tag:
                desc_tag = item.find("p")
            if not desc_tag and item.find("div", class_="compText"):
                desc_tag = item.find("div", class_="compText").find("p")

            title = title_tag.get_text(strip=True) if title_tag else None
            link = _clean_href(link_tag["href"]) if link_tag else None
            desc = desc_tag.get_text(strip=True) if desc_tag else None

            if title and link:
                print(f"AD   title: {title}  --  link: {link}")
                results.append({
                    "searchEngine": "Yahoo",
                    "baseUrl": BASE,
                    "title": title,
                    "link": link,
                    "description": desc or "",
                    "is_ad_promo": False,
                })

        # Promotions - similar updates for description extraction
        for item in soup.select("#web .compArticleList, #web .compText"):
            title_tag = item.find("h3")
            link_tag = item.find("a", href=True)
            desc_tag = item.find("p", class_=lambda c: c and any(cls in c for cls in ["s-desc", "fc-dustygray"]))
            if not desc_tag:
                desc_tag = item.find("p")

            title = title_tag.get_text(strip=True) if title_tag else None
            link = _clean_href(link_tag["href"]) if link_tag else None
            desc = desc_tag.get_text(strip=True) if desc_tag else None

            if title and link:
                print(f"PROM title: {title}  --  link: {link}")
                results.append({
                    "searchEngine": "Yahoo",
                    "baseUrl": BASE,
                    "title": title,
                    "link": link,
                    "description": desc or "",
                    "is_ad_promo": False,
                })

        return results
