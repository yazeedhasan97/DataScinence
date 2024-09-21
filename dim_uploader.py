from datetime import datetime, timedelta

from controllers.apis import get_list_of_coins_at_source, uri_generator, retrieve_data

from models.db import get_db_hook
from models.models import BASE
from models.models import DimCoin
from utilities.utils import load_json_file


def is_coin_exists(factory, coin):
    exists = factory.session.query(DimCoin).filter(DimCoin.iso == coin).all()
    if not exists:
        return False
    return True


def main():
    config_file = "./configs/config.json"
    config = load_json_file(config_file)
    connection, factory = get_db_hook(
        config=config.get('local', None),
        base=BASE,
        # logger=logger

    )

    factory.create_tables()

    list_of_coin = get_list_of_coins_at_source()
    # message = "['" + "', '".join(message) + "']"
    print(f"We have total coins of {len(list_of_coin)}")
    print(type(list_of_coin))
    # lst = eval(message)
    # print(lst)
    # print(type(lst))

    today = datetime.today()
    yesterday = int((today - timedelta(days=1)).strftime('%Y%m%d'))

    for idx, coin in enumerate(list_of_coin):
        if is_coin_exists(factory, coin):
            # print(f"The coin [{coin}] exists... skipping insertion")
            continue
        print(f"Inserting coin [{coin}] to DB.")
        url = uri_generator(factory=factory, coin=coin, start=yesterday, end=int(today.strftime('%Y%m%d')))
        dummy_hit = retrieve_data(url).get('data')
        con = DimCoin(
            iso=dummy_hit.get('iso'),
            name=dummy_hit.get('name'),
            slug=dummy_hit.get('slug'),
            ingestion_start=datetime.strptime(dummy_hit.get('ingestionStart'), '%Y-%m-%d'),
            # interval = Column(Interval, nullable=False, default=timedelta(days=1)),

            active=True,
            collected=False,
        )
        factory.session.add(con)
        if idx % 10 == 0:  # batch
            factory.session.commit()
    factory.session.commit()


if __name__ == "__main__":
    main()
