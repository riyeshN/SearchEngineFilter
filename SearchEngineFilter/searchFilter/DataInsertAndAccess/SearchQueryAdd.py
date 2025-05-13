import re
from datetime import datetime
from django.utils import timezone
from searchFilter.models import SearchEngine, SearchTermMapping, SearchUrls, UrlData
from django.db import transaction
class SearchQueryAdd:

    @staticmethod
    @transaction.atomic
    def add_url_html_data(html : str, row : SearchUrls) -> UrlData:

        date = timezone.now()
        row.data_scrape_time = date
        row.save(update_fields=["data_scrape_time"])

        search_term = row.searchTermId.searchTerm
        print(f"getting data for {row.url} - id: {row.id}")
        count = SearchQueryAdd.get_count(html=html, keyword=search_term)

        url_data_obj, _  = UrlData.objects.get_or_create(
            searchUrls = row,
            count_of_appearance = count,
            html_data = html
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
        for curr in data:
            for engine in curr:
                search_engine_obj = SearchQueryAdd.add_to_search_engine(
                    engine["searchEngine"], engine["baseUrl"]
                )
                search_term_mapping_obj = SearchQueryAdd.add_search_term_mapping(
                    search_term, search_engine_obj, date
                )
                search_url_obj = SearchQueryAdd.add_search_urls(engine = engine, search_term_mapping_obj = search_term_mapping_obj)


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
        search_url_obj, _ = SearchUrls.objects.get_or_create(
            url = engine["link"],
            desc= engine["description"],
            title= engine["title"],
            ad_promo=engine["is_ad_promo"],
            searchTermId=search_term_mapping_obj
        )
        return search_url_obj
