import time
from datetime import datetime

import requests
from jproperties import Properties

from constant.constant import TOKEN_FILE, TIME_FILE, SECRET, CONFIG_FILE, URL_GET_BENEFICIARY, HEADER
from module.mail import Mail
from module.otp import Otp


class TokenRefresh:
    def __init__(self):
        #  Default Config
        self.mobile = ""
        self.email = ""
        self.password = ""

        #  Read Config File
        self.read_properties()

        self.otp = Otp(self.mobile, SECRET)
        self.mail = Mail(self.email, self.password, self.mobile)

    def read_properties(self):
        configs = Properties()
        with open(CONFIG_FILE, 'rb') as read_prop:
            configs.load(read_prop)

        self.mobile = configs["MOBILE"].data
        self.email = configs["EMAIL"].data
        self.password = configs["PASSWORD"].data

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
        with open(TIME_FILE, "r") as text_file:
            last_time = text_file.read()
            lt = datetime.strptime(last_time, "%b %d %Y %H:%M:%S")

        valid = False
        if self.validate_token():
            valid = True

        self.mail.login()

        # TODO : Add Exception handling. Loop should never break

        while True:
            time.sleep(10)
            curr = datetime.strptime(datetime.now().strftime("%b %d %Y %H:%M:%S"), "%b %d %Y %H:%M:%S")
            print("Waiting..... " + str(curr))

            diff = curr - lt
            if diff.seconds > 700 or valid is False:
                print("Token Soon to Expire, Getting new")
                self.mail.re_login()

                last_otp = self.mail.read_otp()
                txn_id = self.otp.generate_otp()
                new_otp = self.mail.read_otp()

                count = 0
                while last_otp == new_otp:
                    print("Old OTP found : " + last_otp)
                    # time.sleep(1)
                    new_otp = self.mail.read_otp()
                    count = count + 1
                    if count == 10:
                        self.otp.generate_otp()
                        self.mail.re_login()
                        count = 0

                print("New OTP received : " + new_otp)

                token = self.otp.get_auth_token(txn_id, new_otp)

                with open(TOKEN_FILE, "w") as text_file:
                    text_file.write(token)

                with open(TIME_FILE, "w") as text_file:
                    text_file.write(str(datetime.now().strftime("%b %d %Y %H:%M:%S")))

                lt = datetime.strptime(datetime.now().strftime("%b %d %Y %H:%M:%S"), "%b %d %Y %H:%M:%S")
                valid = True


token_refresh = TokenRefresh()
token_refresh.refresh()
