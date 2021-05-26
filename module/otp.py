import hashlib
import json
import requests

from constant.constant import URL_GENERATE_OTP, HEADER, URL_VALIDATE_OTP


class Otp:
    def __init__(self, mobile, secret):
        self.mobile = mobile
        self.secret = secret

    def generate_otp(self):
        print("Generating OTP..")
        url = URL_GENERATE_OTP
        data = {'mobile': self.mobile,
                'secret': self.secret
                }

        result = requests.post(url, data=json.dumps(data), headers=HEADER)
        if result.ok:
            response_json = result.json()
            if 'txnId' in response_json:
                return response_json['txnId']

        return None

    def validate_otp(self, txn_id, otp_hash):
        print("Validating OTP..")
        url = URL_VALIDATE_OTP
        data = {'txnId': txn_id,
                'otp': otp_hash
                }

        result = requests.post(url, data=json.dumps(data), headers=HEADER)
        if result.ok:
            response_json = result.json()
            if 'token' in response_json:
                return response_json['token']
        return None

    def get_auth_token(self, txn_id, user_otp):
        otp_hash = hashlib.sha256(user_otp.encode()).hexdigest()
        token = self.validate_otp(txn_id=txn_id, otp_hash=otp_hash)
        return token
