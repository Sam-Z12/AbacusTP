from td.client import TDClient
from ...config import settings

CREDENTIALS_PATH = './credPath.json'

td_session = TDClient(client_id=settings['TD_CONSUMER_KEY'],
                      redirect_uri=settings['TD_REDIRECT_URI'],
                      credentials_path=CREDENTIALS_PATH,
                      account_number=settings['TD_ACCOUNT_NUMBER'])

td_session.login()
