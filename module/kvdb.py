import requests

from constant.constant import KVDB_BUCKET, KVDB_URL


class KVDB:
    def __init__(self, mobile):
        self.mobile = mobile

    def get_otp(self):
        url = KVDB_URL.format(KVDB_BUCKET, self.mobile)

        result = requests.get(url)

        if result.ok:
            return result.text
        else:
            return "000000"
