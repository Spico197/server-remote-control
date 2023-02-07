import re
from urllib.parse import urlencode

import requests

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

    def refresh_session(self):
        self.session = requests.Session()

    def __del__(self):
        if self.session:
            self.session.close()

    def login(self):
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

    def get_power_status(self) -> int:
        index_r = self.session.get(f"{self.url}/index.html")
        st1 = re.search(r"\"ST1\",\s*\"(.*?)\"", index_r.text).group(1)
        st2 = re.search(r"\"ST2\",\s*\"(.*?)\"", index_r.text).group(1)
        r = self.session.post(
            f"{self.url}/data",
            params={
                "get": "pwState",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "GUIAutoRefresh": "false",
                "ST2": st2,
                "Referer": f"{self.url}/powercontrol.html?ST1={st1}",
            },
            verify=False,
        )
        r.raise_for_status()
        text = re.sub(r"[\s\n]+", "", r.text, flags=re.MULTILINE)
        state = re.search(r"<pwState>(.*?)</pwState>", text)
        if state:
            return int(state.group(1))
        return -1

    def power_off(self):
        index_r = self.session.get(f"{self.url}/index.html")
        st1 = re.search(r"\"ST1\",\s*\"(.*?)\"", index_r.text).group(1)
        st2 = re.search(r"\"ST2\",\s*\"(.*?)\"", index_r.text).group(1)
        r = self.session.post(
            f"{self.url}/data",
            params={
                "set": "pwState:0",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "GUIAutoRefresh": "false",
                "ST2": st2,
                "Referer": f"{self.url}/powercontrol.html?ST1={st1}",
            },
            verify=False,
        )
        r.raise_for_status()
        assert "<status>ok</status>" in r.text

    def power_reset(self):
        index_r = self.session.get(f"{self.url}/index.html")
        st1 = re.search(r"\"ST1\",\s*\"(.*?)\"", index_r.text).group(1)
        st2 = re.search(r"\"ST2\",\s*\"(.*?)\"", index_r.text).group(1)
        r = self.session.post(
            f"{self.url}/data",
            params={
                "set": "pwState:3",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "GUIAutoRefresh": "false",
                "ST2": st2,
                "Referer": f"{self.url}/powercontrol.html?ST1={st1}",
            },
            verify=False,
        )
        r.raise_for_status()
        assert "<status>ok</status>" in r.text

    def power_on(self):
        index_r = self.session.get(f"{self.url}/index.html")
        st1 = re.search(r"\"ST1\",\s*\"(.*?)\"", index_r.text).group(1)
        st2 = re.search(r"\"ST2\",\s*\"(.*?)\"", index_r.text).group(1)
        r = self.session.post(
            f"{self.url}/gbtdata",
            params={
                "set": "PowerOn",
                "ST1": st1,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "GUIAutoRefresh": "false",
                "ST2": st2,
                "Referer": f"{self.url}/powercontrol.html?ST1={st1}",
            },
            verify=False,
        )
        r.raise_for_status()
        assert "<status>ok</status>" in r.text
        assert "<compcode>0x00</compcode>" in r.text
