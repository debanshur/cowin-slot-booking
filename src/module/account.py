import requests

from src.constant.constant import URL_GET_BENEFICIARY, HEADER


class Account:
    def __init__(self, token):
        self.token = token
        pass

    def get_acc_details(self):
        print("Getting beneficiary..")
        url = URL_GET_BENEFICIARY
        header = HEADER
        header["Authorization"] = "Bearer " + self.token

        result = requests.get(url, headers=header)
        if result.ok:
            response_json = result.json()
            return response_json
        else:
            print("Get Beneficiary Failed due to : " + str(result.status_code))
            return None
