# cowin-slot-booking
Fully Automated Vaccine Slot Booking App on CoWIN.

## Setup
```
pip install -r requirements.txt
```

Edit the `data.properties` file for custom settings

|Property | Value | Remark |
|--- | --- | --- |
|`AGE` | 50 | Minimum Age |
|`DISTRICT_CODE` | 100,301,505 | List of District Code |
|`START_DATE` | 23-05-2021 | Starting Date for Search |
|`TOTAL_DAYS` | 10 | Total days to search from `START_DATE` |
|`MOBILE` | 7001978442 | Mobile number for OTP |
|`REF_ID` | 54443186578770,35256313660930 | List of Beneficiary ID |
|`DOSE` | 1 | Dose Number. 1 or 2 |
|`VACCINE` | COVISHIELD,COVAXIN,SPUTNIK | Vaccine Type Preference |
|`FEE` | FREE,PAID | Cost of Vaccine |
|`TYPE` | SCHEDULE | Can be SCHEDULE or RESCHEDULE based on your booking status |
|`EMAIL` | "Any mail address" | Any email address to send OTP |
|`PASSWORD` | "Email Password" | Email Password |

## Run
```
python main.py
```
