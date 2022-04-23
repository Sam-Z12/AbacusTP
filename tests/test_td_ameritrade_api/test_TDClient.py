from abacus_server.equities_service.td_python_api.td_python_api import td_session
import pprint

def test_get_accounts():
    account_info = td_session.get_accounts(account='all', fields=['orders', 'positions'])
    pprint.pprint(account_info)
