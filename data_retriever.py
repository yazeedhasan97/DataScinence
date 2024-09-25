from datetime import datetime, timedelta

import numpy as np
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


# def convert_string(x):
#     return int(x.strftime('%Y%m%d'))


def process_response(response, coin):
    tmp_df = pd.DataFrame(response['entries'], columns=['epoch', 'open', 'high', 'low', 'close'])
    tmp_df['date'] = pd.to_datetime(tmp_df['epoch'] // 1000, unit='s', )

    tmp_df['date'] = tmp_df['date'].apply(lambda x: int(x.strftime('%Y%m%d')))

    print(tmp_df.info())
    tmp_df.drop('epoch', axis=1, inplace=True)  # return None
    tmp_df['iso'] = coin.iso
    tmp_df['hash'] = pd.util.hash_pandas_object(tmp_df[['iso', 'date', ]]).astype(np.int64)
    print(tmp_df)
    return tmp_df


def write_to_db(connection, df, coin):
    data = connection.select(
        query=f"SELECT * FROM scrapping.coins where iso = '{coin.iso}'",
    )
    # df = df.join(data, on='hash', )
    df = df[~df['hash'].isin(data['hash'])]
    print(df)
    print(df.info())
    df.to_sql(
        name='coins',
        schema='scrapping',
        con=connection.engine,
        if_exists='append',  # replace
        index=False,
        method='multi'
    )


def main():
    config_file = "./configs/config.json"
    config = load_json_file(config_file)
    connection, factory = get_db_hook(
        config=config.get('local', None),
        base=BASE,
        create=False,
        # logger=logger

    )

    # TODO: set the coin at namespace of config or manually
    coins = fetch_coin(factory, 'DOGE')
    print(f"Processing coins [{coins}]")
    print(f"We have total coins of {len(coins)}")

    today = datetime.today()

    df = pd.DataFrame()
    for coin in coins:
        past = int(coin.ingestion_start.strftime('%Y%m%d'))
        url = uri_generator(factory=factory, coin=coin.iso, start=past, end=int(today.strftime('%Y%m%d')))
        print(url)
        response = retrieve_data(url).get('data')

        tmp_df = process_response(
            response=response,
            coin=coin
        )
        df = pd.concat([df, tmp_df], ignore_index=True)

    df.info()
    write_to_db(connection, df, coin)

    # with open('test_data.csv', 'a') as file:
    #     df.to_csv(file, index=False,)

    # what is the hash and its use
    # groups of operations in dataframe [row, groups, total]


if __name__ == "__main__":
    main()
