import time
from datetime import datetime

import requests
from jproperties import Properties

from constant.constant import CONFIG_FILE, SECRET, TOKEN_FILE, URL_GET_BENEFICIARY, HEADER, TIME_FILE, KVDB_BUCKET
from module.kvdb import KVDB
from module.otp import Otp


class TokenRefresh:
    def __init__(self):
        self.mobile = ""
        #  Read Config File
        self.read_properties()

        self.otp = Otp(self.mobile, SECRET)

    def read_properties(self):
        configs = Properties()
        with open(CONFIG_FILE, 'rb') as read_prop:
            configs.load(read_prop)

        self.mobile = configs["MOBILE"].data

    def validate_token(self):
        with open(TOKEN_FILE, "r") as text_file:
            token = text_file.read()

        url = URL_GET_BENEFICIARY
        header = HEADER
        header["Authorization"] = "Bearer " + token

        result = requests.get(url, headers=header)
        if result.ok:
            return True
        else:
            print("Invalid Token : " + str(result.status_code))
        return False

    def refresh(self):
        kvdb = KVDB(self.mobile)
        with open(TIME_FILE, "r") as text_file:
            last_time = text_file.read()
            lt = datetime.strptime(last_time, "%b %d %Y %H:%M:%S")

        valid = False
        if self.validate_token():
            print("Re-Using Existing Valid token...")
            valid = True

        # TODO : Add Exception handling. Loop should never break

        while True:
            time.sleep(10)
            curr = datetime.strptime(datetime.now().strftime("%b %d %Y %H:%M:%S"), "%b %d %Y %H:%M:%S")
            print("Waiting..... " + str(curr))

            diff = curr - lt
            if diff.seconds > 800 or valid is False:
                print("Token Soon to Expire, Getting new")

                last_otp = kvdb.get_otp()
                txn_id = self.otp.generate_otp()
                new_otp = kvdb.get_otp()

                count = 0
                while last_otp == new_otp:
                    print("Old OTP found : " + last_otp)
                    # time.sleep(1)
                    new_otp = kvdb.get_otp()
                    count = count + 1
                    if count == 10:
                        self.otp.generate_otp()
                        count = 0

                print("New OTP received : " + new_otp)

                print("Waiting..... " + str(datetime.now().strftime("%b %d %Y %H:%M:%S")))
                token = self.otp.get_auth_token(txn_id, new_otp)

                if token is None:
                    valid = False
                    continue

                with open(TOKEN_FILE, "w") as text_file:
                    text_file.write(token)

                with open(TIME_FILE, "w") as text_file:
                    text_file.write(str(datetime.now().strftime("%b %d %Y %H:%M:%S")))

                lt = datetime.strptime(datetime.now().strftime("%b %d %Y %H:%M:%S"), "%b %d %Y %H:%M:%S")
                valid = True


token_refresh = TokenRefresh()
token_refresh.refresh()
