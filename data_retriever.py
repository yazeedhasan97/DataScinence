from datetime import datetime, timedelta

import pandas as pd

from controllers.apis import get_list_of_coins_at_source, uri_generator, retrieve_data

from models.db import get_db_hook
from models.models import BASE
from models.models import DimCoin
from utilities.utils import load_json_file


def fetch_coin(factory, coin='all'):
    # filters = []
    query = factory.session.query(DimCoin)
    if coin.lower() != 'all':
        data = query.filter(DimCoin.iso == coin).all()
    else:
        data = query.all()

    if not data:
        return []
    return data


def main():
    config_file = "./configs/config.json"
    config = load_json_file(config_file)
    connection, factory = get_db_hook(
        config=config.get('local', None),
        base=BASE,
        # logger=logger

    )

    # TODO: set the coin at namespace of config or manually
    coins = fetch_coin(factory, 'BTC')
    print(f"Processing coins [{coins}]")
    print(f"We have total coins of {len(coins)}")

    today = datetime.today()

    df = pd.DataFrame()
    for coin in coins:
        past = int(coin.ingestion_start.strftime('%Y%m%d'))
        url = uri_generator(factory=factory, coin=coin.iso, start=past, end=int(today.strftime('%Y%m%d')))
        response = retrieve_data(url).get('data')
        tmp_df = pd.DataFrame(response['entries'], columns=['epoch', 'open', 'high', 'low', 'close'])
        tmp_df['date'] = pd.to_datetime(tmp_df['epoch'] // 1000, unit='s', )
        tmp_df.drop('epoch', axis=1, inplace=True)  # return None
        tmp_df['iso'] = coin.iso
        tmp_df['hash'] = pd.util.hash_pandas_object(tmp_df[['iso', 'date', ]])
        df = pd.concat([df, tmp_df], ignore_index=True)

    df.to_csv('test_data.csv', index=False)

    # what is the hash and its use
    # groups of operations in dataframe [row, groups, total]

if __name__ == "__main__":
    main()
