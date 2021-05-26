import re
import requests

from src.module.auto_captcha import AutoCaptcha
from src.constant.constant import URL_GET_CAPTCHA, HEADER


class Captcha:
    def __init__(self, token):
        self.auto = AutoCaptcha()
        self.token = token
        pass

    def get_captcha(self):
        print("Generating Captcha..")
        url = URL_GET_CAPTCHA

        header = HEADER
        header["Authorization"] = "Bearer " + self.token

        result = requests.post(url, headers=header)
        if result.ok:
            response_json = result.json()
            if 'captcha' in response_json:
                return response_json['captcha']

        return None

    def decode_captcha(self):

        svg = self.get_captcha()
        if svg is None:
            return None
        svg = re.sub(r'<path d=.*?fill=\"none\"/>', '', svg)

        with open("C:\\Users\\debanshu.r\\PycharmProjects\\CoWin-Slot\\src\\data\\captcha.svg", "w") as text_file:
            text_file.write(svg)  # No use. Just for fun. Will remove if performance decreases

        with open("C:\\Users\\debanshu.r\\PycharmProjects\\CoWin-Slot\\src\\data\\captcha.xml", "w") as text_file:
            text_file.write(svg)

        # cap = input("Enter Captcha : ")
        cap = self.auto.process_captcha("C:\\Users\\debanshu.r\\PycharmProjects\\CoWin-Slot\\src\\data\\captcha.xml")
        print("Captcha : " + cap)
        return cap
