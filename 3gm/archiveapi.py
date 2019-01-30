# -*- coding: utf-8 -*-

from internetarchive import get_session
from datetime import date , datetime , timedelta
import isodate


class ArchiveStats:
    """Internet Archive stats class"""

    @staticmethod
    def getStats():
        today = date.today()
        back30_days = (datetime.now() - timedelta(days=30)).date()
        back7_days = (datetime.now() - timedelta(days=7)).date()

        collection = 'greekgovernmentgazette'
        query_all = f'collection:({collection})'
        res = {}

        try:
            s = get_session()
            s.mount_http_adapter()


            search_results = s.search_items(query_all,fields=['identifier','addeddate'])
            lst_res = list(search_results)
            docs_last30days = [ i for i in lst_res if isodate.parse_date(i['addeddate']) >= back30_days]
            docs_last7days = [ i for i in lst_res if isodate.parse_date(i['addeddate']) >= back7_days]
            docs_today = [ i for i in lst_res if isodate.parse_date(i['addeddate']) == today]

            res['count_all'] = len(lst_res)
            res['count_last30days'] = len(docs_last30days)
            res['count_last7days'] = len(docs_last7days)
            res['count_today'] = len(docs_today)
        finally:
            return res
        