import enum

URL_GENERATE_OTP = "https://api.CoWIN.gov.in/api/v2/auth/generateMobileOTP"
URL_VALIDATE_OTP = "https://api.CoWIN.gov.in/api/v2/auth/validateMobileOtp"
URL_GET_CAPTCHA = "https://api.CoWIN.gov.in/api/v2/auth/getRecaptcha"
URL_GET_BENEFICIARY = "https://api.CoWIN.gov.in/api/v2/appointment/beneficiaries"
URL_SLOT_SCHEDULE = "https://api.CoWIN.gov.in/api/v2/appointment/schedule"
URL_SLOT_DISTRICT = "https://api.CoWIN.gov.in/api/v2/appointment/sessions/findByDistrict?district_id={}&date={}"

HEADER = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36",
          "Content-Type" : "application/json",
          "Accept" : "application/json",
          "cache-control": "no-cache",
          "pragma": "no-cache"
          }

IMAP_URL = 'imap.gmail.com'

SECRET = "SECRET"
MODEL = "SECRET_KEY_FOR_CAPTCHA"


class ACTION(enum.Enum):
    RESTART = 0
