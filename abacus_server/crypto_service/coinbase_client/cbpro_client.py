
import requests

from ...config import settings
from .cbpro_auth import CBProAuth
from .cbpro_public import CBproPubicClient


class CBProClient(CBproPubicClient):

    def __init__(self, api_key, secret_key, passphrase, api_url: str = 'https://api.pro.coinbase.com'):
        """Used for private endpoints for specific user accounts.
        Args:
            key (str): Your coinbase pro api key
            secret_key (str): Secret key given by coinbase when api key is generated
            passphase (str): passphrase given when creating api key
            api_url (str): Url to coinbase 
        """
        super().__init__()
        self.auth = CBProAuth(api_key, secret_key, passphrase)
        self.session = requests.Session()

    def get_account(self, account_id):
        """ Get information for a single account.
        Use this endpoint when you know the account_id.
        Args:
            account_id (str): Account id for account you want to get.
        Returns:
            dict: Account information. Example::
                {
                    "id": "a1b2c3d4",
                    "balance": "1.100",
                    "holds": "0.100",
                    "available": "1.00",
                    "currency": "USD"
                }
        """
        return self._send_http_request('get', '/accounts/' + account_id)

    def get_accounts(self):
        """
        Gets a list of all accounts

        When an order is place those funds 
        are put on hold until the order is 
        filled or canceled and can be seen in the hold field.

        Returns:
            list: Info about all accounts. Example::
                [
                    {
                        "id": "71452118-efc7-4cc4-8780-a5e22d4baa53",
                        "currency": "BTC",
                        "balance": "0.0000000000000000",
                        "available": "0.0000000000000000",
                        "hold": "0.0000000000000000",
                        "profile_id": "75da88c5-05bf-4f54-bc85-5c775bd68254"
                    },
                    {
                        ...
                    }
                ]
        """
        return self._send_http_request('get', '/accounts/')

    def find_account_id(self, currency_name: str):
        """
        Find the account id for a currency
        Args:
            currency_name (str): currency name such as 'BTC' 

        Returns:
            string: an account id
        """
        accounts = self.get_accounts()
        for a in accounts:
            if a['currency'] == currency_name:
                return a['id']

        raise IndexError(f'currency_name {currency_name} does not exist')

    def find_all_positions(self):
        accounts = self.get_accounts()
        positions = []
        for a in accounts:
            if a['balance'] != '0.0000000000000000':
                positions.append(a)
        return positions
