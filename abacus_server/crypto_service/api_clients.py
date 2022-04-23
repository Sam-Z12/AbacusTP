from .coinbase_client.cbpro_client import CBProClient
from ..config import settings


crypto_client = CBProClient(api_key=settings['CBPRO_API_KEY'], secret_key=settings['CBPRO_API_SECRET'],
                            passphrase=settings['CBPRO_PASSPHRASE'], api_url=settings['CBPRO_API_BASE_URL'])
