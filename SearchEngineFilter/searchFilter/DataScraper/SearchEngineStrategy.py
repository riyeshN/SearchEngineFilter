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

        # Debug: Print counts to help diagnose if selectors are matching
        print(f"Google search results - HTML length: {len(html_content)}")
        print(f"Found {len(soup.select('.MjjYud .yuRUbf'))} organic results")
        print(f"Found {len(soup.select('div[aria-label=\"Ads\"] a.sVXRqc'))} explicit ad results")

        # Write a sample of the HTML to file for inspection
        try:
            with open("google_results.html", "w", encoding="utf-8") as f:
                f.write(html_content[:10000])  # First 10K of HTML
            print("Wrote sample of Google HTML to google_results.html")
        except Exception as e:
            print(f"Failed to write HTML sample: {e}")

        # Google-specific ad indicators
        google_ad_indicators = [
            'adurl=', 'adservingdata', 'adurl?q=',
            'data-text-ad', 'data-dtld="', 'data-sokoban-container',
            'kAAxwc', 'uEierd', 'commercial-unit', 'shopping-result',
            'sponsored-label', 'DtQqvd'
        ]

        # Add fallback patterns to detect ads
        ad_indicators = [
            'sponsored', 'advertisement', 'ad-', 'ads.', 'adclick',
            '/aclk', '/ads/', 'doubleclick', 'googleadservices',
            'shopping'
        ]

        def is_likely_ad(url, text=None, html=None):
            """Check if a URL, text, or HTML contains common ad indicators"""
            if url:
                # Check URL for ad indicators
                url_lower = url.lower()
                for indicator in ad_indicators:
                    if indicator in url_lower:
                        print(f"Ad detected via URL pattern '{indicator}' in: {url}")
                        return True

            # Check if there's "Ad" or "Sponsored" text nearby
            if text and any(x in text.lower() for x in ['ad ', 'ads ', 'sponsored ', 'advertisement']):
                print(f"Ad detected via text pattern in: {text}")
                return True

            # Check the HTML for specific Google ad indicators
            if html:
                html_lower = html.lower()
                for indicator in google_ad_indicators:
                    if indicator in html_lower:
                        print(f"Ad detected via HTML pattern '{indicator}'")
                        return True

            return False

        def _clean_href(href: Optional[str]) -> Optional[str]:
            if not href:
                return None
            if href.startswith("/"):
                href = urljoin(BASE, href)
            if href.startswith("/url"):
                return parse_qs(urlparse(href).query).get("q", [href])[0]
            return href

        # Try multiple selectors for ads
        ad_selectors = [
            'div[aria-label="Ads"] a.sVXRqc',
            '.commercial-unit-desktop-top',
            '.ads-fr',
            '.ads-ad',
            '.pla-unit',
            'a[data-jsarwt="1"]',  # Often used for ads
            '[data-text-ad]',
            '#tads a',
            '.uEierd',  # Shopping ads
            'div[data-text-ad="1"]',
            'div[jscontroller="U4Hp0d"]',  # Often shopping ads
            '#tadsb'  # Bottom ads
        ]

        all_ads = []
        for selector in ad_selectors:
            found_ads = soup.select(selector)
            if found_ads:
                print(f"Found {len(found_ads)} ads with selector '{selector}'")
                all_ads.extend(found_ads)

        # Scan all search results
        all_search_results = soup.select("div.g, div.ULSxyf, div.MjjYud")
        print(f"Scanning {len(all_search_results)} general results for ad indicators")

        for item in all_search_results:
            # Check if this is a shopping result (very likely an ad)
            is_shopping = 'uEierd' in str(item) or 'commercial-unit' in str(item)

            title_tag = item.find("h3")
            link_tag = item.find("a", href=True)
            desc_tag = item.find("div", class_="VwiC3b")

            title = title_tag.get_text(strip=True) if title_tag else None
            link = _clean_href(link_tag["href"]) if link_tag else None
            desc = desc_tag.get_text(strip=True) if desc_tag else None

            if not title and not link:
                continue  # Skip items without title or link

            # Check if this div contains any ad indicators
            is_ad = is_shopping or is_likely_ad(link, title, str(item))

            # Additional check for any ad indicators
            if not is_ad:
                if "mKZH5e" in str(item):  # Elements containing price tags
                    is_ad = True
                    print(f"Detected price element - likely shopping ad")

            if title and link:
                if desc is None:
                    desc = ""  # Use empty string for missing description

                print(f"{'AD' if is_ad else 'ORG'}  title: {title}  --  link: {link}")
                results.append({
                    "searchEngine": "Google",
                    "baseUrl": BASE,
                    "title": title,
                    "link": link,
                    "description": desc,
                    "ad_promo": is_ad,
                })

        # Process specific ads from dedicated ad sections
        for a in all_ads:
            if a in [r.get("link_tag") for r in results if hasattr(r, "link_tag")]:
                continue  # Skip if we already processed this link

            title = a.get_text(strip=True)
            link = _clean_href(a.get("href"))

            # Try to find description in parent or next sibling
            desc_tag = None
            parent = a.find_parent()
            if parent:
                desc_tag = parent.find("div", class_="VwiC3b")
                if not desc_tag:
                    # Look in siblings
                    next_sib = parent.find_next_sibling()
                    if next_sib:
                        desc_tag = next_sib.find("div", class_="VwiC3b")

            desc = desc_tag.get_text(strip=True) if desc_tag else ""

            if title and link:
                print(f"AD   title: {title}  --  link: {link}")
                results.append({
                    "searchEngine": "Google",
                    "baseUrl": BASE,
                    "title": title,
                    "link": link,
                    "description": desc,
                    "ad_promo": True,  # This is an ad
                })

        # ── 3. Promos ──────────────────────────────────────
        promo_selectors = [
            ".xpdopen", ".kp-blk", ".VkpGBb", ".FLP8od",
            ".knowledge-panel", ".ifM9O", ".g-blk",
            ".related-question-pair", ".JolIg", ".ULSxyf"
        ]

        for selector in promo_selectors:
            for item in soup.select(selector):
                # Skip if this seems like a regular result we've already processed
                if item.find("h3") and item.find("a", href=True) and item in all_search_results:
                    continue

                # Attempt to get standard title and description
                title_tag = item.find("h3") or item.find("h2")
                desc_tag = item.find("div", class_="VwiC3b")

                # Try any anchor with a valid link
                link_tag = item.find("a", href=True)
                link = _clean_href(link_tag["href"]) if link_tag else None

                # Fallback title if no <h3>
                title = (
                    title_tag.get_text(strip=True) if title_tag
                    else item.get_text(" ", strip=True)[:80].strip()
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
                        "ad_promo": True,  # This is a promo
                    })

        # Debug summary
        ad_count = sum(1 for r in results if r["ad_promo"])
        print(f"Google results summary: {len(results)} total, {ad_count} ads/promos")

        return results


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

        # Debug info
        print(f"Bing search results - HTML length: {len(html_content)}")
        print(f"Found {len(soup.select('#b_results > li'))} total result items")

        # Write HTML to file for inspection
        try:
            with open("bing_results.html", "w", encoding="utf-8") as f:
                f.write(html_content[:10000])  # First 10K of HTML
            print("Wrote sample of Bing HTML to bing_results.html")
        except Exception as e:
            print(f"Failed to write HTML sample: {e}")

        # Specific Bing ad indicators
        bing_ad_indicators = [
            'b_ad', 'ad_sc', 'b_adBottom', 'ad_', 'ads_',
            'adredir.', 'adticket=', 'bat.bing', 'acb.msn',
            'sponsored', 'advertisement', 'shopping'
        ]

        # Common ad patterns in URLs and text
        ad_indicators = [
            'sponsored', 'advertisement', 'ad-', 'ads.', 'adclick',
            '/aclk', '/ads/', 'doubleclick', 'msn.com/ads', 'bing.com/aclick',
            'bat.bing.com', 'microsoft.com/advertising', 'promoted', 'shopnow'
        ]

        def is_likely_ad(url, text=None):
            """Check if a URL or text contains common ad indicators"""
            if not url:
                return False
            # Check URL for ad indicators
            url_lower = url.lower()
            for indicator in ad_indicators:
                if indicator in url_lower:
                    print(f"Ad detected via URL pattern '{indicator}' in: {url}")
                    return True

            # Check if there's "Ad" or "Sponsored" text nearby
            if text and any(x in text.lower() for x in ['ad ', 'ads ', 'sponsored ', 'advertisement']):
                print(f"Ad detected via text pattern in: {text}")
                return True

            return False

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

        # Try multiple ad selectors
        ad_selectors = [
            '#b_results > li.b_ad',
            'li.ad',
            'li[data-tag="ad"]',
            '.b_adLastChild',
            '.sb_add',
            '.ad_sc',
            'li[data-bm="5"]',  # Sometimes indicates ads
            '.b_algoPagination + li',  # Ads often appear after pagination
            '#b_context .b_ad'  # Right-side ads
        ]

        found_ad_elements = []
        for selector in ad_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} ad elements with selector '{selector}'")
                found_ad_elements.extend(elements)

        # Scan all list items in search results
        all_items = soup.select("#b_results > li, #b_context li")
        print(f"Scanning {len(all_items)} total items for ads")

        for li in all_items:
            # For Bing, we need to be even more careful about different ad structures
            cls = li.get("class", [])
            cls_str = " ".join(cls).lower()

            # Check if this is a known ad element
            is_ad = li in found_ad_elements

            # Additional checks for ad classes
            is_ad = is_ad or any(ad_ind in cls_str for ad_ind in bing_ad_indicators)
            is_promo = any("b_ans" in c for c in cls) or "b_context" in cls_str

            # Look for specific data attributes that indicate ads
            data_bm = li.get("data-bm", "")
            if data_bm in ["5", "6"]:  # These values are often used for ads
                is_ad = True

            # Look for shopping results which are often ads
            if "ProductCard" in str(li) or "Products_primaryProductCard" in str(li):
                is_ad = True
                print("Found shopping result (likely ad)")

            # Check HTML for ad indicators
            li_html = str(li).lower()
            for indicator in bing_ad_indicators:
                if indicator in li_html:
                    is_ad = True
                    print(f"Found Bing ad indicator: {indicator}")
                    break

            kind = "ad" if is_ad else "promo" if is_promo else "organic"

            # title / link / desc
            h2 = li.find("h2")
            a = h2.find("a", href=True) if h2 else li.find("a", href=True)
            para = li.find("p")

            title = (h2.get_text(strip=True) if h2 and h2.get_text(strip=True)
                     else a.get_text(strip=True) if a else None)
            link = _clean_href(a["href"]) if a else None
            desc = para.get_text(strip=True) if para else None

            # Final URL check for ad indicators
            if link and not is_ad and not is_promo:
                is_ad = is_likely_ad(link, title)

            if title:
                if title in {"Previous", "Next"} or title.startswith("Related searches"):
                    continue
                print(f"[{kind.upper()}] title: {title}  --  link: {link}")

                if title and link:  # Make description optional
                    results.append({
                        "searchEngine": "Bing",
                        "baseUrl": BASE,
                        "title": title,
                        "link": link,
                        "description": desc or "",  # Empty string if no description
                        "ad_promo": is_ad or is_promo,
                    })

        # Debug summary
        ad_count = sum(1 for r in results if r["ad_promo"])
        print(f"Bing results summary: {len(results)} total, {ad_count} ads/promos")

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

        # Debug info
        print(f"DuckDuckGo search results - HTML length: {len(html_content)}")
        print(f"Found {len(soup.select('.result'))} regular results")
        print(f"Found {len(soup.select('div[data-testid=\"ad\"]'))} explicit ads")

        # This will help detect if we have the right selectors
        print(f"Page contains 'result--ad' class: {'result--ad' in html_content}")
        print(f"Page contains 'sponsored' text: {'sponsored' in html_content.lower()}")

        # Write a sample of HTML for inspection
        try:
            with open("ddg_results.html", "w", encoding="utf-8") as f:
                f.write(html_content[:10000])  # First 10K of HTML
            print("Wrote sample of DuckDuckGo HTML to ddg_results.html")
        except Exception as e:
            print(f"Failed to write HTML sample: {e}")

        # DuckDuckGo-specific indicators
        ddg_ad_indicators = [
            'result--ad', 'result__sponsored', 'is-ad',
            'sponsored', 'js-ad-', 'module--ads',
            'adserver', 'aaxads', 'module--shopping', 'price'
        ]

        # Common ad patterns in URLs and text
        ad_indicators = [
            'sponsored', 'advertisement', 'ad-', 'ads.', 'adclick',
            '/aclk', '/ads/', 'doubleclick', 'googleadservices',
            'syndication', 'adsystem'
        ]

        def is_likely_ad(url, text=None, html=None):
            """Check if a URL or text contains common ad indicators"""
            if url:
                # Check URL for ad indicators
                url_lower = url.lower()
                for indicator in ad_indicators:
                    if indicator in url_lower:
                        print(f"Ad detected via URL pattern '{indicator}' in: {url}")
                        return True

            # Check if there's "Ad" or "Sponsored" text nearby
            if text and any(x in text.lower() for x in ['ad ', 'ads ', 'sponsored ', 'advertisement']):
                print(f"Ad detected via text pattern in: {text}")
                return True

            # Check HTML for DuckDuckGo-specific indicators
            if html:
                html_lower = html.lower()
                for indicator in ddg_ad_indicators:
                    if indicator in html_lower:
                        print(f"Ad detected via HTML pattern '{indicator}'")
                        return True

            return False

        def _clean_href(href: Optional[str]) -> Optional[str]:
            if not href:
                return None
            if href.startswith("/"):
                href = urljoin(BASE, href)
            if href.startswith("/l/?uddg="):
                return unquote(href.split("uddg=")[1].split("&")[0])
            return href

        # Scan all results
        for result in soup.select(".result, .web-result"):
            title_link = result.select_one(".result__a")
            desc_elem = result.select_one(".result__snippet")

            # Multiple ways to check if this is an ad
            result_classes = result.get("class", [])
            result_class_str = " ".join(result_classes).lower()

            is_ad = any(indicator in result_class_str for indicator in ddg_ad_indicators)

            # Check for specific HTML patterns that indicate ads
            if not is_ad:
                result_html = str(result).lower()
                is_ad = is_likely_ad(None, None, result_html)

            title = title_link.get_text(strip=True) if title_link else None
            link = _clean_href(title_link["href"]) if title_link and title_link.has_attr("href") else None
            desc = desc_elem.get_text(strip=True) if desc_elem else None

            # Check URL for ad indicators
            if not is_ad and link:
                is_ad = is_likely_ad(link, title)

            if title and link:
                if desc is None:
                    desc = ""  # Use empty string for missing description

                result_type = "AD" if is_ad else "ORG"
                print(f"{result_type}  title: {title}  --  link: {link}")
                results.append({
                    "searchEngine": "DuckDuckGo",
                    "baseUrl": BASE,
                    "title": title,
                    "link": link,
                    "description": desc,
                    "ad_promo": is_ad,
                })

        # Additional explicit ads that might use different selectors
        ad_explicit_selectors = [
            'div[data-testid="ad"]',
            '.js-ad-link',
            '.js-result-sponsored',
            '.badge--ad',
            '.sponsored',
            '.result--ad'
        ]

        for selector in ad_explicit_selectors:
            for item in soup.select(selector):
                title_tag = None
                # Different approaches to find title
                title_tag = item.find("a", attrs={"data-testid": "ad-title"})
                if not title_tag:
                    title_tag = item.find("h2") or item.find("h3") or item.find("a", class_="result__a")

                link_tag = title_tag if title_tag and title_tag.name == "a" else item.find("a", href=True)

                # Different approaches to find description
                desc_tag = item.find("div", class_="ad__desc")
                if not desc_tag:
                    desc_tag = item.find("div", class_="result__snippet") or item.find("p")

                title = title_tag.get_text(strip=True) if title_tag else None
                link = _clean_href(link_tag["href"]) if link_tag else None
                desc = desc_tag.get_text(strip=True) if desc_tag else None

                if title and link:  # Make description optional
                    if not desc:
                        desc = ""  # Use empty string for missing description
                    print(f"AD   title: {title}  --  link: {link}")
                    results.append({
                        "searchEngine": "DuckDuckGo",
                        "baseUrl": BASE,
                        "title": title,
                        "link": link,
                        "description": desc,
                        "ad_promo": True,  # This is definitely an ad
                    })

        # Promotions may be in "modules" or special sections
        promotion_selectors = [
            'div[data-testid="zci"]',
            '.module--carousel',
            '.module--tiles',
            '.module-answer',
            '.module-products',
            '.module--products',
            '.module--shopping'
        ]

        for selector in promotion_selectors:
            for item in soup.select(selector):
                # Try different patterns to extract info
                title_tag = item.find("h2") or item.find("h3") or item.find(".module__title")
                link_tag = item.find("a", href=True)
                desc_tag = item.find("div", class_="zci__content") or item.find("div", class_="module__content")

                title = title_tag.get_text(strip=True) if title_tag else None
                link = _clean_href(link_tag["href"]) if link_tag else None
                desc = desc_tag.get_text(strip=True) if desc_tag else None

                # If we have no title but have link and description
                if not title and link and desc:
                    # Use first part of description as title
                    title = desc[:60] + ("..." if len(desc) > 60 else "")

                if title and link:  # Make description optional
                    if not desc:
                        desc = ""
                    print(f"PROM title: {title}  --  link: {link}")
                    results.append({
                        "searchEngine": "DuckDuckGo",
                        "baseUrl": BASE,
                        "title": title,
                        "link": link,
                        "description": desc,
                        "ad_promo": True,  # This is a promo
                    })

        # Debug summary
        ad_count = sum(1 for r in results if r["ad_promo"])
        print(f"DuckDuckGo results summary: {len(results)} total, {ad_count} ads/promos")

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

        # Debug: Print how many elements of each type we find
        print(f"Yahoo search results - HTML length: {len(html_content)}")
        print(f"Found {len(soup.select('#web .algo'))} organic results")
        print(f"Found {len(soup.select('#web .ad'))} explicit ad results")
        print(f"Found {len(soup.select('#web .compArticleList, #web .compText'))} potential promos")

        # Write a sample of HTML for inspection
        try:
            with open("yahoo_results.html", "w", encoding="utf-8") as f:
                f.write(html_content[:10000])  # First 10K of HTML
            print("Wrote sample of Yahoo HTML to yahoo_results.html")
        except Exception as e:
            print(f"Failed to write HTML sample: {e}")

        # Yahoo-specific ad indicators
        yahoo_ad_indicators = [
            'ad_badge', 'ad-', 'adlink', 'ad-focus', 'adserver',
            'class="ad"', 'class="Ad"', 'shopping-result', 'beacon',
            'compShoppingSummary', 'AdChoices', 'label="Ad"', 'sponsored_'
        ]

        # Add fallback patterns to detect ads
        ad_indicators = [
            'sponsored', 'advertisement', 'ad-', 'ads.', 'adclick',
            '/aclk', '/ads/', 'doubleclick', 'googleadservices',
            'shopping', 'yahoo.com/commerce', 'price-section'
        ]

        def is_likely_ad(url, text=None, html=None):
            """Check if a URL or text contains common ad indicators"""
            if url:
                # Check URL for ad indicators
                url_lower = url.lower()
                for indicator in ad_indicators:
                    if indicator in url_lower:
                        print(f"Ad detected via URL pattern '{indicator}' in: {url}")
                        return True

            # Check if there's "Ad" or "Sponsored" text nearby
            if text and any(x in text.lower() for x in ['ad ', 'ads ', 'sponsored ', 'advertisement']):
                print(f"Ad detected via text pattern in: {text}")
                return True

            # Check HTML for Yahoo-specific indicators
            if html:
                html_lower = html.lower()
                for indicator in yahoo_ad_indicators:
                    if indicator in html_lower:
                        print(f"Ad detected via HTML pattern '{indicator}'")
                        return True

            return False

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

        # Scan all search results for ads - Yahoo has a complex structure
        all_items = soup.select("#web li, #web .algo, #right .algo, div[data-beacon], .dd.algo, #main li, #right li")
        print(f"Scanning {len(all_items)} total Yahoo items for ads")

        for item in all_items:
            # Check if this is an ad by class
            item_classes = item.get("class", [])
            item_class_str = " ".join(item_classes).lower() if item_classes else ""

            # Check for ad indicators in the class
            is_ad = "ad" in item_class_str
            is_promo = "comp" in item_class_str

            # Check data attributes for beacon (often used for ads)
            data_beacon = item.get("data-beacon", "")
            if "Ad" in data_beacon or "ad" in data_beacon:
                is_ad = True
                print("Found ad via data-beacon attribute")

            # Check if it contains any ad indicators in the HTML
            item_html = str(item).lower()
            if not is_ad:
                for indicator in yahoo_ad_indicators:
                    if indicator in item_html:
                        is_ad = True
                        print(f"Found Yahoo ad indicator: {indicator}")
                        break

            title_tag = item.find("h3")
            link_tag = item.find("a", href=True)

            # Updated selector for description
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

            # Check URL for ad indicators
            if link and not is_ad:
                is_ad = is_likely_ad(link, title, item_html)

            # Special case for Yahoo shopping results (which are ads)
            if not is_ad and "compShoppingSummary" in item_html:
                is_ad = True
                print("Detected Yahoo shopping result (likely ad)")

            # Special case for Yahoo product ads
            if not is_ad and "price-section" in item_html:
                is_ad = True
                print("Detected price section (likely product ad)")

            if title and link:  # Make description optional
                if desc is None:
                    desc = ""

                result_type = "AD" if is_ad else "PROMO" if is_promo else "ORG"
                print(f"{result_type}  title: {title}  --  link: {link}")

                results.append({
                    "searchEngine": "Yahoo",
                    "baseUrl": BASE,
                    "title": title,
                    "link": link,
                    "description": desc,
                    "ad_promo": is_ad or is_promo,
                })

        # Specific ad selectors - might find additional ads
        ad_selectors = [
            '#web .ad',
            '#web [data-beacon*="ad"]',
            '.AdBttm',
            '.AdTop',
            '.Ad-Composite',
            '.sw-Card-Bd[data-integration="commerce"]'  # Shopping ads
        ]

        for selector in ad_selectors:
            for item in soup.select(selector):
                # Skip if we've already processed this item
                if any(r.get("title") == item.get_text(strip=True)[:50] for r in results):
                    continue

                title_tag = item.find("h3")
                link_tag = item.find("a", href=True)
                desc_tag = item.find("p")

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
                        "ad_promo": True,  # This is definitely an ad
                    })

        # Promotions - Yahoo has many types of promotional content
        promo_selectors = [
            "#web .compArticleList",
            "#web .compText",
            "#right .compText",
            ".compFeatured",
            ".compShoppingSummary",
            ".compDlink",
            ".compCardList",
            '.sw-Card'  # Shopping widgets
        ]

        for selector in promo_selectors:
            for item in soup.select(selector):
                # Skip if we've already processed this item
                if any(r.get("title") == item.get_text(strip=True)[:50] for r in results):
                    continue

                title_tag = item.find("h3") or item.find("h4")
                link_tag = item.find("a", href=True)
                desc_tag = item.find("p")

                title = title_tag.get_text(strip=True) if title_tag else None

                # If no title tag but we have a link, use the link text
                if not title and link_tag:
                    title = link_tag.get_text(strip=True)

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
                        "ad_promo": True,  # This is a promotional item
                    })

        # Debug summary
        ad_count = sum(1 for r in results if r["ad_promo"])
        print(f"Yahoo results summary: {len(results)} total, {ad_count} ads/promos")

        return results