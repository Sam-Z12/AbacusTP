
import requests
from ...config import settings


class CBproPubicClient(object):
    """Used to access pubic endpoints from coinbase"""

    def __init__(self, api_url: str = 'https://api.pro.coinbase.com') -> object:
        self.url = api_url
        self.auth = None
        self.session = requests.Session()

    def get_all_trading_pairs(self):
        """Grabs a list of currency comparisons.

        Returns:
           list: Info about all currency pairs. Example::
               [
                   {
                       "id": "BTC-USD",
                       "display_name": "BTC/USD",
                       "base_currency": "BTC",
                       "quote_currency": "USD",
                       "base_min_size": "0.01",
                       "base_max_size": "10000.00",
                       "quote_increment": "0.01"
                   }
               ]
            """

        return self._send_http_request('get', '/products')

    def get_all_trading_pair_ids(self):
        currencies = self.get_all_trading_pairs()
        return [c['id'] for c in currencies]

    def get_product_candles(self, product_id, start=None, end=None,
                            granularity=None):
        """Historic rates for a product.
        Rates are returned in grouped buckets based on requested
        `granularity`. {60, 300, 900, 3600, 21600, 86400}. These values 
        correspond to timeslices representing one minute, five minutes, 
        fifteen minutes, one hour, six hours, and one day, respectively. 
        If start, end, and granularity aren't provided,
        the exchange will assume some (currently unknown) default values.
        Historical rate data may be incomplete. No data is published for
        intervals where there are no ticks.
        **Caution**: Historical rates should not be polled frequently.
        If you need real-time information, use the trade and book
        endpoints along with the websocket feed.
        The maximum number of data points for a single request is 200
        candles. If your selection of start/end time and granularity
        will result in more than 200 data points, your request will be
        rejected. If you wish to retrieve fine granularity data over a
        larger time range, you will need to make multiple requests with
        new start/end ranges.
        Args:
            product_id (str): Product
            start (Optional[str]): Start time in ISO 8601
            end (Optional[str]): End time in ISO 8601
            granularity (Optional[int]): Desired time slice in seconds
        Returns:
            list: Historic candle data. Example:
                [
                    [ time, low, high, open, close, volume ],
                    [ 1415398768, 0.32, 4.2, 0.35, 4.2, 12.3 ],
                    ...
                ]
        """
        # if kwargs:
        #     product_id = kwargs['product_id']
        #     start = kwargs['start']
        #     end = kwargs['end']
        #     granularity = kwargs['granularity']

        print("retrieving cbpro candles")
        params = {}
        if start is not None:
            params['start'] = start
        if end is not None:
            params['end'] = end
        if granularity is not None:
            acceptedGrans = [60, 300, 900, 3600, 21600, 86400]
            if granularity not in acceptedGrans:
                raise ValueError(
                    f'Specified granularity is {granularity}, must be in approved values: {acceptedGrans}')

            params['granularity'] = granularity
        return self._send_http_request('get',
                                       f'/products/{product_id}/candles',
                                       params=params)

    def get_product_stats(self, product_id):
        """Gets 30day and 24hour stats for a product.

        Args:
            product_id(str): product
        Returns:
            dict: Product stats
            {
                "open": "5414.18000000",
                "high": "6441.37000000",
                "low": "5261.69000000",
                "volume": "53687.76764233",
                "last": "6250.02000000",
                "volume_30day": "786763.72930864}
            }

        """

        return self._send_http_request('get', f'/products/{product_id}/stats')

    def get_product_order_book(self, product_id: str, level: int = 1):
        """Get a list of open orders for a product.
        The amount of detail shown can be customized with the `level`
        parameter:
        * 1: Only the best bid and ask
        * 2: Top 50 bids and asks (aggregated)
        * 3: Full order book (non aggregated)
        Level 1 and Level 2 are recommended for polling. For the most
        up-to-date data, consider using the websocket stream.
        **Caution**: Level 3 is only recommended for users wishing to
        maintain a full real-time order book using the websocket
        stream. Abuse of Level 3 via polling will cause your access to
        be limited or blocked.
        Args:
            product_id (str): Product
            level (Optional[int]): Order book level (1, 2, or 3).
                Default is 1.
        Returns:
            dict: Order book. Example for level 1::
                {
                    "sequence": "3",
                    "bids": [
                        [ price, size, num-orders ],
                    ],
                    "asks": [
                        [ price, size, num-orders ],
                    ]
                }
        """
        params = {'level': level}
        return self._send_http_request('get', f'/products/{product_id}/book', params=params)

    def _send_http_request(self, method: str, endpoint: str, params: dict = None, data: str = None):
        """Send http request.
        Args:
            method (str): HTTP method (get, post, delete, etc.)
            endpoint (str): Endpoint (to be added to base URL)
            params (Optional[dict]): HTTP request parameters
            data (Optional[str]): JSON-encoded string payload for POST
        Returns:
            dict/list: JSON response
        """
        url = self.url + endpoint
        r = self.session.request(method, url, params=params, data=data,
                                 auth=self.auth, timeout=30)
        return r.json()
