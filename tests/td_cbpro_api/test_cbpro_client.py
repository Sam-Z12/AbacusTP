from .test_cbpro_login import cbpro_client


def test_get_accounts(cbpro_client):
    accounts = cbpro_client.get_accounts()


def test_find_account_id(cbpro_client):
    id = cbpro_client.find_account_id('BTC')
    assert type(id) == type('')


def test_find_all_positions(cbpro_client):
    positions = cbpro_client.find_all_positions()
    print(positions)
