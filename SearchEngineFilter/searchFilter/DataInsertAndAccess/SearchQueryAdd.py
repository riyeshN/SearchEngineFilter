import re
from datetime import datetime
from django.utils import timezone
from searchFilter.models import SearchEngine, SearchTermMapping, SearchUrls, UrlData
from django.db import transaction


class SearchQueryAdd:

    @staticmethod
    @transaction.atomic
    def add_url_html_data(html: str, row: SearchUrls) -> UrlData:

        date = timezone.now()
        row.data_scrape_time = date
        row.save(update_fields=["data_scrape_time"])

        search_term = row.searchTermId.searchTerm
        print(f"getting data for {row.url} - id: {row.id}")
        count = SearchQueryAdd.get_count(html=html, keyword=search_term)

        url_data_obj, _ = UrlData.objects.get_or_create(
            searchUrls=row,
            count_of_appearance=count,
            html_data=html
        )
        return url_data_obj

    @staticmethod
    def get_count(html: str, keyword: str):
        if not html or not keyword:
            return 0
            # \b matches word boundaries (start or end of a word)
        pattern = rf'\b{re.escape(keyword)}\b'
        return len(re.findall(pattern, html, flags=re.IGNORECASE))

    @staticmethod
    @transaction.atomic
    def add_search_results(search_term: str, data: list[list]):
        date = timezone.now()

        # Debug: Count how many ads we're finding
        total_ads = 0
        total_results = 0

        print("\n**** PROCESSING SEARCH RESULTS ****")
        print(f"Search term: {search_term}")
        obj_added = []
        for curr in data:
            for engine in curr:
                is_ad = engine.get("ad_promo", False)
                total_results += 1
                if is_ad:
                    total_ads += 1

                search_engine_obj = SearchQueryAdd.add_to_search_engine(
                    engine["searchEngine"], engine["baseUrl"]
                )
                search_term_mapping_obj = SearchQueryAdd.add_search_term_mapping(
                    search_term, search_engine_obj, date
                )
                search_url_obj = SearchQueryAdd.add_search_urls(engine=engine,
                                                                search_term_mapping_obj=search_term_mapping_obj)

                obj_added.append(search_url_obj)

        print(f"\n**** SEARCH SUMMARY: {total_results} total results, {total_ads} ads/promos ****\n")

    @staticmethod
    def add_to_search_engine(search_engine: str, base_url: str):
        search_engine_obj, _ = SearchEngine.objects.get_or_create(
            name=search_engine,
            defaults={"baseUrl": base_url}
        )
        return search_engine_obj

    @staticmethod
    def add_search_term_mapping(search_term: str, search_engine_obj: SearchEngine, date: datetime):
        search_term_mapping_obj, _ = SearchTermMapping.objects.get_or_create(
            searchEngineName=search_engine_obj,
            searchTerm=search_term,
            time_searched=date
        )
        return search_term_mapping_obj

    @staticmethod
    def add_search_urls(engine, search_term_mapping_obj: SearchTermMapping):
        # Make sure we're preserving the ad_promo flag from the engine results
        ad_promo = engine.get("ad_promo", False)

        # More detailed debug info
        search_engine = engine.get("searchEngine", "Unknown")
        title = engine.get("title", "Unknown")
        ad_text = "AD/PROMO" if ad_promo else "ORGANIC"

        print(f"[{search_engine}] {ad_text}: {title}")

        ##TODO: this needs to create new entry 
        search_url_obj, _ = SearchUrls.objects.get_or_create(
            url=engine["link"],
            desc=engine["description"],
            title=engine["title"],
            ad_promo=engine["ad_promo"],  # Use the flag from the engine results
            searchTermId=search_term_mapping_obj
        )
        return search_url_obj