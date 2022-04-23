
from abacus_server.config import settings
from tests.td_cbpro_api.test_cbpro_login import public_client


def test_get_all_trading_pairs(public_client):
    currencies = public_client.get_all_trading_pairs()
    assert type(currencies) == type([])
    assert len(currencies) > 10
    assert type(currencies[0]) == type({})


def test_get_all_trading_pair_ids(public_client):
    ids = public_client.get_all_trading_pair_ids()
    assert len(ids) > 10


def test_get_pruduct_order_book(public_client):
    order_book = public_client.get_product_order_book('BTC-USD')
    assert 'bids' in order_book
    assert 'asks' in order_book


def test_get_product_stats(public_client):
    stats = public_client.get_product_stats('BTC-USD')
    assert 'volume_30day' in stats


def test_get_product_candles(public_client):
    candles = public_client.get_product_candles(
        'BTC-USD', '2022-01-19', '2022-01-20', 3600)
    print(candles)

    assert len(candles) == 25
