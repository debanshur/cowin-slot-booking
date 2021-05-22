import base64
import json
import re
import xml.etree.ElementTree as ET

from constant import MODEL


class AutoCaptcha:
    def __init__(self):
        self.my_dict = {}
        self._lookup = [False] * 4096
        self.loc_dict = {}
        self.decode_str = self.decode()
        pass

    def process_captcha(self, captcha_file):
        self.build_lookup()
        self.my_dict = json.loads(self.decode_str)

        return self.parse_xml(captcha_file)

    def build_lookup(self):
        for c in range(65, 91):
            self._lookup[c] = True

    def parse_xml(self, file):
        tree = ET.parse(file)
        root = tree.getroot()

        # TODO : Use list(root) in place of getChindren
        for item in root.getchildren():
            self.compute_captcha(item)

        sorted_dict = dict(sorted(self.loc_dict.items()))
        captcha_decoded = ''.join(str(sorted_dict[x]) for x in sorted(sorted_dict))
        print(captcha_decoded)
        return captcha_decoded

    def compute_captcha(self, item):
        path_raw_data = item.attrib["d"].upper()
        position = float(path_raw_data[1: path_raw_data.find(' ')])

        encoded_data = re.sub('[^A-Z]+', '', path_raw_data)
        mapped_character = self.my_dict[encoded_data]
        self.loc_dict[position] = mapped_character

    def decode(self):
        string_bytes = base64.b64decode(MODEL)
        str_decode = string_bytes.decode()
        return str_decode
