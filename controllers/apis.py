# constants
from datetime import datetime

import requests

URL = 'https://production.api.coindesk.com/v2/price/values/{coin}?start_date={start}&end_date={end}&ohlc=true'


def uri_generator(factory, coin: str, start: int, end: int):  # make him send on day level

    completion = 'T00:00'
    try:
        start = datetime.strptime(str(start), '%Y%m%d').strftime(f'%Y-%m-%d{completion}')
        end = datetime.strptime(str(end), '%Y%m%d').strftime(f'%Y-%m-%d{completion}')
    except Exception as e:
        raise e

    return URL.format(
        coin=coin,
        start=start,
        end=end
    )


def retrieve_data(uri, expect_to_be_bad=False):
    result = requests.get(uri)
    try:
        if not expect_to_be_bad:
            result.raise_for_status()
    except Exception as e:
        raise e

    return result.json()

def get_list_of_coins_at_source(expect_to_be_bad=True):
    investigation_hit = retrieve_data(URL, expect_to_be_bad=expect_to_be_bad)
    list_of_coin = investigation_hit['message'].split('[')[-1].strip(']').split(', ')