import re
from urllib.parse import quote_plus

import requests

from .base import ManageAPI, ServerSSH


class InspurAPI(ManageAPI, ServerSSH):
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
        self.cookie = None

    def refresh_session(self):
        self.session = requests.Session()

    def __del__(self):
        self.logout()
        if self.session:
            self.session.close()

    def login(self):
        if self.check_login():
            return
        r = self.session.post(
            f"{self.url}/rpc/WEBSES/create.asp",
            data=f"WEBVAR_USERNAME={self.username}&WEBVAR_PASSWORD={self.password}",
        )
        r.raise_for_status()
        session_cookie = re.search(r"'SESSION_COOKIE'\s*:\s*'(.*?)'", r.text)
        if session_cookie:
            session_cookie = session_cookie.group(1)
            jar = r.cookies
            jar.set("SessionCookie", session_cookie)
            jar.set("SessionExpired", "false")
            self.cookie = jar

    def logout(self):
        r = self.session.get(f"{self.url}/rpc/WEBSES/logout.asp", cookies=self.cookie)
        r.raise_for_status()
        assert "HAPI_STATUS:0" in r.text or "HAPI_STATUS:-1" in r.text

    def check_login(self) -> bool:
        r = self.session.get(f"{self.url}/index.html", cookies=self.cookie)
        r.raise_for_status()
        if "forgotPwd()" in r.text and "remember-me" in r.text:
            return False
        else:
            r = self.session.get(
                f"{self.url}/rpc/hoststatus.asp",
                cookies=self.cookie,
            )
            if "Please relogin" in r.text:
                return False
            else:
                return True

    def get_power_status(self) -> int:
        self.login()
        r = self.session.get(
            f"{self.url}/rpc/hoststatus.asp",
            cookies=self.cookie,
        )
        self.logout()
        r.raise_for_status()
        state = re.search(r"'JF_STATE'\s*:\s*(\d+)", r.text)
        if state:
            return int(state.group(1))
        return -1

    def power_off(self):
        self.login()
        r = self.session.post(
            f"{self.url}/rpc/hostctl.asp",
            data="WEBVAR_POWER_CMD=5",
            cookies=self.cookie,
        )
        self.logout()
        r.raise_for_status()
        assert re.search(r"HAPI_STATUS\s*:\s*0\s*}", r.text)

    def power_off_immediate(self):
        self.login()
        r = self.session.post(
            f"{self.url}/rpc/hostctl.asp",
            data="WEBVAR_POWER_CMD=0",
            cookies=self.cookie,
        )
        self.logout()
        r.raise_for_status()
        assert re.search(r"HAPI_STATUS\s*:\s*0\s*}", r.text)

    def power_reset(self):
        self.login()
        r = self.session.post(
            f"{self.url}/rpc/hostctl.asp",
            data="WEBVAR_POWER_CMD=3",
            cookies=self.cookie,
        )
        self.logout()
        r.raise_for_status()
        assert re.search(r"HAPI_STATUS\s*:\s*0\s*}", r.text)

    def power_on(self):
        self.login()
        r = self.session.post(
            f"{self.url}/rpc/hostctl.asp",
            data="WEBVAR_POWER_CMD=1",
            cookies=self.cookie,
        )
        self.logout()
        r.raise_for_status()
        assert re.search(r"HAPI_STATUS\s*:\s*0\s*}", r.text)
