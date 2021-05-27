from datetime import datetime
import requests
from jproperties import Properties

from module.appointment import Appointment
from module.captcha import Captcha
from constant.constant import ACTION, SECRET, URL_GET_BENEFICIARY, HEADER, TOKEN_FILE, TIME_FILE, CONFIG_FILE
from module.mail import Mail
from module.otp import Otp


class CowinApp:
    def __init__(self):
        #  Default Config
        self.age = 0
        self.num_days = 0
        self.district_code = []
        self.mobile = ""
        self.dose = ""
        self.beneficiary = ""
        self.start_date = datetime.today().strftime("%d-%m-%Y")
        self.vaccine = []
        self.email = ""
        self.password = ""
        self.token = ""
        self.fee_type = ""
        self.book_type = ""
        self.app_id = ""

        #  Read Config File
        self.read_properties()

        self.otp = Otp(self.mobile, SECRET)
        self.mail = Mail(self.email, self.password, self.mobile)

    def read_properties(self):
        configs = Properties()
        with open(CONFIG_FILE, 'rb') as read_prop:
            configs.load(read_prop)

        self.age = configs["AGE"].data
        self.num_days = int(configs["TOTAL_DAYS"].data)
        code = str(configs["DISTRICT_CODE"].data)
        self.district_code = code.split(",")
        self.mobile = configs["MOBILE"].data
        self.email = configs["EMAIL"].data
        self.password = configs["PASSWORD"].data
        self.dose = configs["DOSE"].data
        ref_id = str(configs["REF_ID"].data)
        self.beneficiary = ref_id.split(",")
        self.start_date = configs["START_DATE"].data
        vac = configs["VACCINE"].data
        self.vaccine = vac.split(",")
        fee = str(configs["FEE"].data)
        self.fee_type = fee.split(",")
        self.book_type = configs["TYPE"].data

    def get_existing_token(self):
        with open(TOKEN_FILE, "r") as text_file:
            token = text_file.read()
        return token

    def validate_token(self, token):
        url = URL_GET_BENEFICIARY
        header = HEADER
        header["Authorization"] = "Bearer " + token

        result = requests.get(url, headers=header)
        if result.ok:
            return True
        else:
            print("Token Auth Failed due to : " + str(result.status_code))
        return False

    def get_token(self):
        last_token = self.get_existing_token()

        if self.validate_token(last_token):
            return last_token

        print("STRANGE... You should not see this log.. Token refresh not working!!!!!")

        self.mail.login()
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
        self.mail.logout()
        token = self.otp.get_auth_token(txn_id, new_otp)

        with open(TOKEN_FILE, "w") as text_file:
            text_file.write(token)

        with open(TIME_FILE, "w") as text_file:
            text_file.write(str(datetime.now().strftime("%b %d %Y %H:%M:%S")))

        return token

    def start(self):
        print(datetime.now())

        token = self.get_token()

        if token is None:
            print("OTP Failed")
            return ACTION.RESTART

        self.token = token
        appointment = Appointment(self)

        if self.book_type == "RESCHEDULE":
            self.app_id = appointment.get_appointment_id()
            if self.app_id is None:
                return ACTION.RESTART

        while True:
            slot = appointment.get_slots()

            if slot is ACTION.RESTART:
                return ACTION.RESTART

            if slot is None:
                print("Will retry")
            else:
                self.token = self.get_existing_token()
                captcha = Captcha(self.token)
                captcha_string = captcha.decode_captcha()
                if captcha_string is None:
                    return ACTION.RESTART

                if self.book_type == "RESCHEDULE":
                    booking_res = appointment.reschedule_slot(app_id=self.app_id,
                                                              session_id=slot['session_id'],
                                                              slot_time=slot['slot_time'],
                                                              captcha=captcha_string)
                else:
                    booking_res = appointment.schedule_slot(dose=self.dose,
                                                            session_id=slot['session_id'],
                                                            center_id=slot['center_id'],
                                                            slot_time=slot['slot_time'],
                                                            beneficiary_id=self.beneficiary,
                                                            captcha=captcha_string)
                print(booking_res)
                if booking_res is None or booking_res["appointment_confirmation_no"] is None:
                    print("Booking failed")
                else:
                    exit()



if __name__ == '__main__':

    cowin = CowinApp()

    res = cowin.start()
    while res is ACTION.RESTART:
        cowin = CowinApp()
        res = cowin.start()

    print("Thank you")
