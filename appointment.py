import datetime
import json
import time

import requests

from constant import URL_SLOT_SCHEDULE, HEADER, URL_SLOT_DISTRICT, ACTION


class Appointment:
    def __init__(self, cowin_app):
        self.cowin_app = cowin_app
        pass

    def get_slots(self):
        print("Starting search for Covid vaccine slots!")

        start_date = datetime.datetime.strptime(self.cowin_app.start_date, '%d-%m-%Y')
        date_format = [start_date + datetime.timedelta(days=i) for i in range(self.cowin_app.num_days)]
        actual_dates = [i.strftime("%d-%m-%Y") for i in date_format]

        check = 0
        while True:
            for curr_date in actual_dates:
                time.sleep(1)
                for code in self.cowin_app.district_code:
                    url = URL_SLOT_DISTRICT.format(code, curr_date)
                    header = HEADER
                    header["Authorization"] = "Bearer " + self.cowin_app.token
                    result = requests.get(url, headers=header)

                    if int(result.status_code) == 401:
                        print("OTP expired")
                        return ACTION.RESTART

                    if result.ok:
                        check = 0
                        response_json = result.json()
                        print(response_json)
                        slot = self.parse_availability(response_json)
                        if slot is None:
                            continue
                        return slot
                    else:
                        print("Get Slot Req failed!")
                        if check == 10:
                            return ACTION.RESTART
                        check = check + 1

    def parse_availability(self, response):
        if len(response['sessions']) == 0:
            print("No Slots available!!")
            return None
        else:
            for res in response['sessions']:
                if int(res['available_capacity']) < len(self.cowin_app.beneficiary):
                    continue

                if self.cowin_app.dose is "1":
                    av = res['available_capacity_dose1']
                else:
                    av = res['available_capacity_dose2']

                if int(av) < len(self.cowin_app.beneficiary):
                    continue
                ag = res['min_age_limit']
                vc = res['vaccine']
                fe = res['fee_type']

                if int(ag) <= int(self.cowin_app.age) and \
                    vc in self.cowin_app.vaccine and \
                    fe.upper() in self.cowin_app.fee_type:
                        print("Booking Slot \n" + str(res))
                        slot = {
                            'session_id': res['session_id'],
                            'slot_time': res['slots'][0]
                        }
                        return slot
        return None

    def book_slot(self, dose, session_id, slot_time, beneficiary_id,  captcha):
        print("Booking slot... ")
        url = URL_SLOT_SCHEDULE
        header = HEADER
        header["Authorization"] = "Bearer " + self.cowin_app.token

        data = {
            "dose": dose,
            "session_id": session_id,
            "slot": slot_time,
            "beneficiaries": beneficiary_id,
            "captcha": captcha
        }

        result = requests.post(url, data=json.dumps(data), headers=header)
        if result.ok:
            response_json = result.json()
            return response_json
        else:
            print("Booking slot Failed due to : " + str(result.status_code))
            return None
