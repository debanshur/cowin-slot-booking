import datetime
import json
import time

import requests

from constant.constant import URL_SLOT_SCHEDULE, HEADER, URL_SLOT_DISTRICT, ACTION, URL_GET_BENEFICIARY, \
    URL_SLOT_RESCHEDULE, TOKEN_FILE, TIME_FILE


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
        with open(TIME_FILE, "r") as text_file:
            last_time = text_file.read()
            lt = datetime.datetime.strptime(last_time, "%b %d %Y %H:%M:%S")

        while True:
            for curr_date in actual_dates:
                time.sleep(1)
                curr = datetime.datetime.strptime(datetime.datetime.now().strftime("%b %d %Y %H:%M:%S"), "%b %d %Y %H:%M:%S")

                diff = curr - lt
                if diff.seconds > 850:
                    print("Token Expiry")
                    with open(TOKEN_FILE, "w") as text_file:
                        text_file.write("abc")
                    return ACTION.RESTART



                for code in self.cowin_app.district_code:
                    url = URL_SLOT_DISTRICT.format(code, curr_date)
                    header = HEADER
                    header["Authorization"] = "Bearer " + self.cowin_app.token
                    result = requests.get(url, headers=header)

                    if int(result.status_code) == 401:
                        print("OTP expired")
                        return ACTION.RESTART

                    if int(result.status_code) == 403:
                        print("Timeout by server")
                        with open(TOKEN_FILE, "w") as text_file:
                            text_file.write("abc")
                        return ACTION.RESTART

                    if result.ok:
                        check = 0
                        response_json = result.json()
                        print(url)
                        print(response_json)
                        slot = self.parse_availability(response_json)
                        if slot is None:
                            continue
                        return slot
                    else:
                        print("Get Slot Req failed!" + str(result.status_code))
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

                if self.cowin_app.dose == "1":
                    av = res['available_capacity_dose1']
                else:
                    av = res['available_capacity_dose2']

                if int(av) < len(self.cowin_app.beneficiary):
                    continue
                ag = res['min_age_limit']
                vc = res['vaccine']
                fe = res['fee_type']

                if res['center_id'] == 557647 or res['center_id'] == 711001:

                    if int(ag) <= int(self.cowin_app.age) and \
                        vc in self.cowin_app.vaccine and \
                        fe.upper() in self.cowin_app.fee_type:
                            print("Booking Slot \n" + str(res))
                            slot = {
                                'session_id': res['session_id'],
                                'center_id': res['center_id'],
                                'slot_time': res['slots'][0]
                            }
                            return slot
        return None

    def schedule_slot(self, dose, session_id, center_id, slot_time, beneficiary_id,  captcha):
        print("Booking slot... ")
        url = URL_SLOT_SCHEDULE
        header = HEADER
        header["Authorization"] = "Bearer " + self.cowin_app.token

        data = {
            "dose": dose,
            "session_id": session_id,
            "slot": slot_time,
            "beneficiaries": beneficiary_id,
            "center_id" : center_id,
            "captcha": captcha
        }

        result = requests.post(url, data=json.dumps(data), headers=header)
        if result.ok:
            response_json = result.json()
            return response_json
        else:
            print("Booking slot Schedule Failed due to : " + str(result.status_code))
            return None

    def reschedule_slot(self, app_id, session_id, slot_time,  captcha):
        print("Booking slot Reschedule... ")
        url = URL_SLOT_RESCHEDULE
        header = HEADER
        header["Authorization"] = "Bearer " + self.cowin_app.token

        data = {
            "appointment_id": app_id,
            "session_id": session_id,
            "slot": slot_time,
            "captcha": captcha
        }

        result = requests.post(url, data=json.dumps(data), headers=header)
        if result.ok:
            response_json = result.json()
            return response_json
        else:
            print("Booking slot Reschedule Failed due to : " + str(result.status_code))
            return None

    def get_appointment_id(self):
        print("Getting Appointment ID..")
        url = URL_GET_BENEFICIARY
        header = HEADER
        header["Authorization"] = "Bearer " + self.cowin_app.token

        result = requests.get(url, headers=header)
        if result.ok:
            response_json = result.json()
            beneficiary = response_json['beneficiaries']
            for b in beneficiary:
                if b['beneficiary_reference_id'] in self.cowin_app.beneficiary:
                    appointment_id = b['appointments'][0]['appointment_id']
                    return appointment_id
        else:
            print("Get Beneficiary Failed due to : " + str(result.status_code))
            return None
