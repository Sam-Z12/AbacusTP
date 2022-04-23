import pytest
import requests
from abacus_server.config import settings
from abacus_server.crypto_service.coinbase_client.cbpro_auth import CBProAuth
from abacus_server.crypto_service.coinbase_client.cbpro_public import CBproPubicClient
from abacus_server.crypto_service.coinbase_client.cbpro_client import CBProClient


@pytest.fixture
def test_CBProAuth():
    auth = CBProAuth(api_key=settings['CBPRO_API_KEY'], secret_key=settings['CBPRO_API_SECRET'],
                     passphrase=settings['CBPRO_PASSPHRASE'])

    api_url = 'https://api.pro.coinbase.com'
    r = requests.get(api_url + '/accounts/', auth=auth)
    assert type(r.json()) == type([])
    assert len(r.json()) > 10
    assert type(r.json()[0]) == type({})


@pytest.fixture
def public_client():
    return CBproPubicClient()


@pytest.fixture
def cbpro_client():
    return CBProClient(api_key=settings['CBPRO_API_KEY'], secret_key=settings['CBPRO_API_SECRET'],
                       passphrase=settings['CBPRO_PASSPHRASE'])
