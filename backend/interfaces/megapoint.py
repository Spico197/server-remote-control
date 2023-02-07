import re
from urllib.parse import urlencode

import requests

# In case of SSL: DH_KEY_TOO_SMALL] dh key too small error
# Ref: https://stackoverflow.com/questions/38015537/python-requests-exceptions-sslerror-dh-key-too-small
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ":HIGH:!DH:!aNULL"


from .base import ManageAPI, ServerSSH


class MegapointAPI(ManageAPI, ServerSSH):
    def __init__(
        self,
        manage_url,
        manage_username,
        manage_password,
        ssh_ip,
        ssh_username,
        ssh_password,
        ssh_port=22,
        ssh_timeout=5.0,
    ) -> None:
        super().__init__(
            ssh_ip, ssh_username, ssh_password, ssh_port, ssh_timeout=ssh_timeout
        )
        self.username = manage_username
        self.password = manage_password
        self.url = manage_url

        self.session = requests.Session()
        self.st1 = ""
        self.st2 = ""

    def refresh_session(self):
        self.session = requests.Session()

    def __del__(self):
        if self.session:
            self.session.close()

    def check_login(self) -> bool:
        ...

    def login(self):
        if self.check_login():
            return
        r = self.session.post(
            f"{self.url}/data/login",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=urlencode(
                {
                    "user": self.username,
                    "password": self.password,
                    "killduplicatedsession": "true",
                }
            ),
            verify=False,
        )
        r.raise_for_status()
        assert "<status>ok</status>" in r.text
        assert "<authResult>0</authResult>" in r.text
        index_r = self.session.get(f"{self.url}/index.html", verify=False)
        index_r.raise_for_status()
        self.st1 = re.search(r"\"ST1\",\s*\"(.*?)\"", index_r.text).group(1)
        self.st2 = re.search(r"\"ST2\",\s*\"(.*?)\"", index_r.text).group(1)

    def logout(self):
        r = self.session.post(
            f"{self.url}/data/logout",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "GUIAutoRefresh": "false",
                "ST2": self.st2,
                "Referer": f"{self.url}/powercontrol.html?ST1={self.st1}",
            },
            verify=False,
        )
        assert r.status_code in [401, 200]

    def get_power_status(self) -> int:
        self.login()
        r = self.session.post(
            f"{self.url}/data",
            params={
                "get": "pwState",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "GUIAutoRefresh": "false",
                "ST2": self.st2,
                "Referer": f"{self.url}/powercontrol.html?ST1={self.st1}",
            },
            verify=False,
        )
        self.logout()
        r.raise_for_status()
        text = re.sub(r"[\s\n]+", "", r.text, flags=re.MULTILINE)
        state = re.search(r"<pwState>(.*?)</pwState>", text)
        if state:
            return int(state.group(1))
        return -1

    def power_off(self):
        self.login()
        r = self.session.post(
            f"{self.url}/data",
            params={
                "set": "pwState:0",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "GUIAutoRefresh": "false",
                "ST2": self.st2,
                "Referer": f"{self.url}/powercontrol.html?ST1={self.st1}",
            },
            verify=False,
        )
        self.logout()
        r.raise_for_status()
        assert "<status>ok</status>" in r.text

    def power_reset(self):
        self.login()
        r = self.session.post(
            f"{self.url}/data",
            params={
                "set": "pwState:3",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "GUIAutoRefresh": "false",
                "ST2": self.st2,
                "Referer": f"{self.url}/powercontrol.html?ST1={self.st1}",
            },
            verify=False,
        )
        self.logout()
        r.raise_for_status()
        assert "<status>ok</status>" in r.text

    def power_on(self):
        self.login()
        r = self.session.post(
            f"{self.url}/gbtdata",
            params={
                "set": "PowerOn",
                "ST1": self.st1,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "GUIAutoRefresh": "false",
                "ST2": self.st2,
                "Referer": f"{self.url}/powercontrol.html?ST1={self.st1}",
            },
            verify=False,
        )
        self.logout()
        r.raise_for_status()
        assert "<status>ok</status>" in r.text
        assert "<compcode>0x00</compcode>" in r.text
