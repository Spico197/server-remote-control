import re
from urllib.parse import quote_plus, urlencode

import requests

from .base import ManageAPI, ServerSSH


class InspurPlainAPI(ManageAPI, ServerSSH):
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
        self.username = quote_plus(manage_username)
        self.password = quote_plus(manage_password)
        self.url = manage_url

        self.session = requests.Session()

    def refresh_session(self):
        self.session = requests.Session()

    def __del__(self):
        if self.session:
            self.session.close()

    def login(self):
        r = self.session.post(
            f"{self.url}/cgi/login.cgi",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=f"name={self.username}&pwd={self.password}",
        )
        r.raise_for_status()

    def get_power_status(self) -> int:
        r = self.session.post(
            f"{self.url}/cgi/ipmi.cgi",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=urlencode({
                "POWER_INFO.XML": "(0,0)",
            }),
        )
        r.raise_for_status()
        # POWER_INFO.XML=(0%2C0)&time_stamp=Sun%20Feb%2005%202023%2019%3A10%3A51%20GMT%2B0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&_=
        state = re.search(r"<POWER STATUS=\"(.*?)\"/>", r.text)
        if state:
            return 1 if state.group(1) == "ON" else 0
        return -1

    def power_off(self):
        r = self.session.post(
            f"{self.url}/cgi/ipmi.cgi",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=urlencode({
                "POWER_INFO.XML": "(1,5)",
            }),
        )
        r.raise_for_status()
        state = re.search(r"<POWER STATUS=\"(.*?)\"/>", r.text)
        if state:
            return 1 if state.group(1) == "ON" else 0
        return -1

    def power_reset(self):
        r = self.session.post(
            f"{self.url}/cgi/ipmi.cgi",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=urlencode({
                "POWER_INFO.XML": "(1,3)",
            }),
        )
        r.raise_for_status()
        state = re.search(r"<POWER STATUS=\"(.*?)\"/>", r.text)
        if state:
            return 1 if state.group(1) == "ON" else 0
        return -1

    def power_on(self) -> int:
        r = self.session.post(
            f"{self.url}/cgi/ipmi.cgi",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=urlencode({
                "POWER_INFO.XML": "(1,1)",
            }),
        )
        r.raise_for_status()
        state = re.search(r"<POWER STATUS=\"(.*?)\"/>", r.text)
        if state:
            return 1 if state.group(1) == "ON" else 0
        return -1
