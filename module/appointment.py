import datetime
import json
import time

import requests

from constant.constant import URL_SLOT_SCHEDULE, HEADER, URL_SLOT_DISTRICT, ACTION, URL_GET_BENEFICIARY, \
    URL_SLOT_RESCHEDULE, TOKEN_FILE, TIME_FILE, URL_SLOT_PINCODE


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

        if self.cowin_app.search_type == "DISTRICT":
            search_codes = self.cowin_app.district_code
            search_url = URL_SLOT_DISTRICT
        else:
            search_codes = self.cowin_app.pincode
            search_url = URL_SLOT_PINCODE

        while True:
            for curr_date in actual_dates:
                time.sleep(0.5)

                # TODO : Token Validity check. May be refactored
                # url = URL_GET_BENEFICIARY
                # header = HEADER
                # header["Authorization"] = "Bearer " + self.cowin_app.token
                #
                # result = requests.get(url, headers=header)
                # if not result.ok:
                #     print("Token Auth Failed due to : " + str(result.status_code))
                #     return ACTION.RESTART

                for code in search_codes:
                    url = search_url.format(code, curr_date)
                    header = HEADER
                    # Not Required for public api
                    #header["Authorization"] = "Bearer " + self.cowin_app.token
                    result = requests.get(url, headers=header)

                    if result.status_code == 401 or result.status_code == 403:
                        print("OTP expired / Timeout by Server : " + str(result.status_code))
                        return ACTION.RESTART

                    if result.ok:
                        check = 0
                        response_json = result.json()
                        print(datetime.datetime.now().strftime("%b %d %Y %H:%M:%S"))
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

                age_criteria = True
                if int(self.cowin_app.age) >= 45:
                    if int(ag) >= 45:
                        age_criteria = True
                    else :
                        age_criteria = False
                else:
                    if int(ag) >= 18 and int(ag) < 45:
                        age_criteria = True
                    else :
                        age_criteria = False

                if age_criteria and \
                    vc in self.cowin_app.vaccine and \
                    fe.upper() in self.cowin_app.fee_type:
                        print("Booking Slot \n" + str(res))
                        slot = {
                            'session_id': res['session_id'],
                            'center_id': res['center_id'],
                            'slot_time': res['slots'][0]
                        }
                        #print("\n--------------------------------------")
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
            if result.status_code != 200:
                return result
            response_json = result.json()
            return response_json
        else:
            print("Booking slot Reschedule Failed due to : " + str(result.status_code))
            return result

    def get_appointment_id(self):
        print("Getting Appointment ID..")
        url = URL_GET_BENEFICIARY
        header = HEADER
        header["Authorization"] = "Bearer " + self.cowin_app.token

        result = requests.get(url, headers=header)
        appointment_id_list = set([])
        if result.ok:
            response_json = result.json()
            beneficiary = response_json['beneficiaries']
            for b in beneficiary:
                if b['beneficiary_reference_id'] in self.cowin_app.beneficiary:
                    appointment_id_list.add(b['appointments'][0]['appointment_id'])
            return appointment_id_list
        else:
            print("Get Beneficiary Failed due to : " + str(result.status_code))
            return None
