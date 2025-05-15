from django.db import connection


class GetSQLData:

    @staticmethod
    def get_list_of_links_for_keyword(keyword: str = None):
        results = []

        if not keyword:
            return results

        query = """
            WITH ID_TO_SEARCH AS (
                SELECT a.* from searchFilter_searchtermmapping a JOIN (
                    SELECT searchTerm, searchEngineName_id, MAX(time_searched) AS max_time
                    FROM searchFilter_searchtermmapping
                    WHERE Lower(searchTerm) = %s
                    GROUP BY searchTerm, searchEngineName_id
                ) b ON LOWER(a.searchTerm) = LOWER(b.searchTerm)and a.searchEngineName_id =b.searchEngineName_id 
                    AND a.time_searched = b.max_time 
                ), URL_FROM_ID AS (
                    select * from searchFilter_searchurls where searchTermId_id  in (select id from ID_TO_SEARCH)
                ), URL_AND_KEYWORD AS (
                    SELECT a.*, b.searchTerm, b.time_searched, b.searchEngineName_id  from URL_FROM_ID a JOIN ID_TO_SEARCH b on a.searchTermId_id  = b.id 
                ), FINAL_RESULTS AS (
                    SELECT a.*, b.count_of_appearance , b.searchUrls_id  FROM URL_AND_KEYWORD a JOIN searchFilter_urldata b on a.id = b.searchUrls_id 
                ) SELECT id, url, desc, title, ad_promo, data_scrape_time, time_searched, count_of_appearance, searchEngineName_id AS searchEngine 
                FROM FINAL_RESULTS ORDER BY searchEngineName_id , count_of_appearance  DESC
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [keyword.lower()])
            columns = [col[0] for col in cursor.description]
            results = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        return results


    @staticmethod
    def get_list_of_ads_none_ads(keyword: str = None):
        results = []

        if not keyword:
            return results

        query = """
            	WITH ID_TO_SEARCH AS (
                    SELECT a.* from searchFilter_searchtermmapping a JOIN (
                    SELECT searchTerm, searchEngineName_id, MAX(time_searched) AS max_time
                    FROM searchFilter_searchtermmapping
                    WHERE Lower(searchTerm) = %s
                    GROUP BY searchTerm, searchEngineName_id
                ) b ON LOWER(a.searchTerm) = LOWER(b.searchTerm)and a.searchEngineName_id =b.searchEngineName_id 
                    AND a.time_searched = b.max_time 
                ), ALL_VALUES AS (
                    SELECT a.id, a.searchTerm , a.time_searched, a.searchEngineName_id,b.ad_promo 
                    FROM ID_TO_SEARCH a join searchFilter_searchurls b on a.id  = b.searchTermId_id 
                ) SELECT searchTerm, searchEngineName_id, ad_promo, COUNT(*)  FROM ALL_VALUES 
                GROUP BY searchTerm, searchEngineName_id, ad_promo 
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [keyword.lower()])
            columns = [col[0] for col in cursor.description]
            results = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        return results

