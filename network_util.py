import requests
from log_util import LogUtil

class NetworkUtil(object):
    def test_access_url(url):
        # url = "http://www.kite.com"
        # url = "http://rt.ugr.es:8920/"
        url = "https://cajal.ugr.es/"
        timeout = 5
        try:
            request = requests.get(url, timeout=timeout)
            LogUtil.write_log(url, "Access successfully!")
            return True
        except (requests.ConnectionError, requests.Timeout) as exception:
            LogUtil.write_log(url, "Cannot access.")
            return False
