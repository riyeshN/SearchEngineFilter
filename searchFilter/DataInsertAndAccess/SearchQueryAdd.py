from searchFilter.models import SearchEngine, SearchTermMapping, SearchUrls
from django.db import transaction
class SearchQueryAdd:

    @staticmethod
    @transaction.atomic
    def add_search_results(search_term: str, data: list[list]):

        for curr in data:
            for engine in curr:
                search_engine_obj = SearchQueryAdd.add_to_search_engine(
                    engine["searchEngine"], engine["baseUrl"]
                )
                search_term_mapping_obj = SearchQueryAdd.add_search_term_mapping(
                    search_term, search_engine_obj
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
    def add_search_term_mapping(search_term: str, search_engine_obj: SearchEngine):
        search_term_mapping_obj, _ = SearchTermMapping.objects.get_or_create(
            searchEngineId=search_engine_obj,
            searchTerm=search_term
        )
        return search_term_mapping_obj

    @staticmethod
    def add_search_urls(engine, search_term_mapping_obj: SearchTermMapping):
        search_url_obj, _ = SearchUrls.objects.get_or_create(
            url = engine["link"],
            desc= engine["description"],
            title= engine["title"],
            ad= engine["is_ad"] or engine["is_promo"],
            searchTermId=search_term_mapping_obj
        )
        return search_url_obj
