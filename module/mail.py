import imaplib

from constant.constant import IMAP_URL


class Mail:
    def __init__(self, user, password, mobile):
        self.key_tag = "OTP-" + str(mobile)
        self.user = user
        self.password = password
        self.con = imaplib.IMAP4_SSL(IMAP_URL)

    # Function to get email content part i.e its body part
    def get_body(self, msg):
        if msg.is_multipart():
            return self.get_body(msg.get_payload(0))
        else:
            return msg.get_payload(None, True)

    # Function to search for a key value pair
    def search(self, key, value, con):
        result, data = con.search(None, key, '"{}"'.format(value))

        return data

    # Function to get the list of emails under this label
    def get_emails(self, result_bytes):
        msgs = []
        for num in result_bytes[0].split():
            typ, data = self.con.fetch(num, '(RFC822)')
            msgs.append(data)

        return msgs

    def read_otp(self):
        # calling function to check for email under this label
        self.con.select('INBOX', readonly=True)

        msgs = self.get_emails(self.search('SUBJECT', self.key_tag, self.con))
        for msg in msgs[::-1]:
            for sent in msg:
                if type(sent) is tuple:
                    content = str(sent[1], 'utf-8')
                    data = str(content)
                    msg_body = data.split('$D$')
                    otp = msg_body[1].split(".")[0].split()[-1]
                    print("OTP Received from mail : " + otp)
                    return otp

    def logout(self):
        self.con.logout()

    def login(self):
        self.con.login(self.user, self.password)

    def re_login(self):
        self.con.logout()
        self.con = imaplib.IMAP4_SSL(IMAP_URL)
        self.con.login(self.user, self.password)

    def re_con(self):
        self.con = imaplib.IMAP4_SSL(IMAP_URL)
        self.con.login(self.user, self.password)
