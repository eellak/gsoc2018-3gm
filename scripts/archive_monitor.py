# -*- coding: utf-8 -*-

from internetarchive import get_session
from datetime import date , datetime , timedelta
import isodate
import argparse 

def get_stats(days=30):
        back_days = (datetime.now() - timedelta(days=days)).date()
        query_all = 'collection:(greekgovernmentgazette) AND date:[{1} TO {0}]' \
                        .format(datetime.now().strftime('%Y-%m-%d'), back_days.strftime('%Y-%m-%d'))
        s = get_session()
        s.mount_http_adapter()

        search_results = s.search_items(query_all,fields=['identifier','addeddate'])

        return '{}\t{}'.format(query_all, len(search_results))

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(usage='Display IA collection stats')
    argparser.add_argument('-d', type=int, default=30)
    args = argparser.parse_args()
    print(get_stats(days=args.d))

