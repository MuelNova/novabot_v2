import time

from sqlitedict import SqliteDict
from nonebot import get_driver
from requests import Session
from requests.cookies import create_cookie
from typing import Dict, Union, Any, List

from .config import Config
from .crypto import *
from .model import *
from .exception import NoLoginException
from .parser import report_parser, xisu_report_parser

plugin_config = Config.parse_obj(get_driver().config)

if not Path.exists(plugin_config.data_path):
    Path.mkdir(plugin_config.data_path, parents=True)
if not Path.exists(plugin_config.secret_path):
    Path.mkdir(plugin_config.secret_path, parents=True)

salt = initialize(plugin_config.salt_path)
API_TIMEOUT = plugin_config.api_timeout


class DBUser:
    qq: str
    path: Path
    username: str
    password: str
    _password: str
    cookies: List
    _cookie_eaisess: str
    _cookie_uukey: str
    _secret: bytes
    _iv: bytes
    checkin_time: str
    xisu_checkin_time: str
    is_stopped: bool
    is_xisu_stopped: bool

    def __init__(self, conf: Dict = None, path: Path = None):
        self.path = path and path or plugin_config.secret_path
        if conf is not None:
            for i in conf.values():
                self.qq = i.get('qq')
                self.username = i.get('username')
                self._password = i.get('password')
                self._cookie_eaisess = i.get('cookie_eaisess')
                self._cookie_uukey = i.get('cookie_uukey')
                self._secret, self._iv = get_passwd_secret_iv(self.path, self.qq)
                self.checkin_time = i.get('checkin_time', '08:00')
                self.xisu_checkin_time = i.get('xisu_checkin_time', '08:01|12:01|18:01')
                self.is_stopped = i.get('is_stopped', False)
                self.is_xisu_stopped = i.get('is_xisu_stopped', False)
                break
        else:
            self.checkin_time = '08:00'
            self.xisu_checkin_time = '08:01|12:01|18:01'
            self._cookie_eaisess = ''
            self._cookie_uukey = ''
            self.is_stopped = False
            self.is_xisu_stopped = False

    def set_password(self, password: str):
        self._secret, self._iv = get_passwd_secret_iv(self.path, self.qq, password, salt)
        self._password = msg_encrypt(password, self._secret, self._iv)

    def set_cookie(self, cookie_eaisess: str, cookie_uukey: str):
        assert self._secret and self._iv
        self._cookie_eaisess = msg_encrypt(cookie_eaisess, self._secret, self._iv)
        self._cookie_uukey = msg_encrypt(cookie_uukey, self._secret, self._iv)

    def __getattr__(self, item) -> Any:
        if item == 'password':
            assert self._secret and self._iv
            return msg_decrypt(self._password, self._secret, self._iv)
        if item == 'cookies':
            assert self._secret and self._iv
            return [msg_decrypt(self._cookie_eaisess, self._secret, self._iv),
                    msg_decrypt(self._cookie_uukey, self._secret, self._iv)]
        return None

    def dict(self) -> dict:
        return {
            self.qq: {
                "qq": self.qq,
                "username": self.username,
                "password": self._password,
                "cookie_eaisess": self._cookie_eaisess,
                "cookie_uukey": self._cookie_uukey,
                "checkin_time": self.checkin_time,
                "xisu_checkin_time": self.xisu_checkin_time,
                "is_stopped": self.is_stopped,
                "is_xisu_stopped": self.is_xisu_stopped
            }
        }


class BUPTUser(SqliteDict):
    qq: str
    session: Session
    is_login: bool
    _username: str
    _passwd: str
    db: DBUser

    def __init__(self, qq: Union[str, int]):
        if isinstance(qq, int):
            qq = str(qq)
        super().__init__(plugin_config.database_path, autocommit=True)
        self.qq = qq
        self.is_login = False
        self.session = Session()

    def get_or_create(self,
                      username: str = None,
                      password: str = None,
                      force: bool = False
                      ):
        if self.get(self.qq) and not force:
            self.db = DBUser(self.get(self.qq))
            self._username = self.db.username
            self._passwd = self.db.password
            cookies = self.db.cookies
            self.session.cookies.set_cookie(create_cookie("eai-sess", cookies[0], domain=BASIC_DOMAIN))
            self.session.cookies.set_cookie(create_cookie("UUkey", cookies[1], domain=BASIC_DOMAIN))
            self.is_login = True
        else:
            assert username and password
            self._username = username
            self._passwd = password
            self.db = DBUser()
            self.db.username = self._username
            self.db.qq = self.qq
            self.db.set_password(self._passwd)
            self.do_login()
        return self

    def do_login(self):
        login_resp = self.session.post(LOGIN_API, data={
            'username': self._username,
            'password': self._passwd,
        }, timeout=API_TIMEOUT)
        if login_resp.status_code != 200:
            raise ConnectionError(f"Failed to Login!\nError Code: {login_resp.status_code}")
        elif (resp := login_resp.json()).get('e'):
            raise ConnectionError(f"Failed to Login!\nError Message: {resp.get('m')}")
        self.db.set_cookie(login_resp.cookies['eai-sess'], login_resp.cookies['UUkey'])
        self.is_login = True
        self.save()

    def save(self):
        self[self.qq] = self.db.dict()

    def read(self) -> Dict:
        # print(self.db.cookies, self.db.password)
        return self.get(self.qq)

    def ncov_checkin(self) -> str:
        report_page_resp = self.session.get(REPORT_PAGE, allow_redirects=False,
                                            timeout=API_TIMEOUT)
        if report_page_resp.status_code != 200:
            raise ConnectionError(f"Failed to Checkin\nError Code: {report_page_resp.status_code}")
        if "realname" not in report_page_resp.text:
            raise NoLoginException("Failed to Checkin\nNo Login")
        post_data = report_parser(report_page_resp.text)
        final_resp = self.session.post(REPORT_API, post_data,
                                       headers={'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest'},
                                       timeout=API_TIMEOUT)
        if final_resp.status_code != 200:
            raise ConnectionError(f"Failed to Checkin\nError Code: {report_page_resp.status_code}")
        if (resp := final_resp.json()).get('e'):
            raise ConnectionError(f"Failed to Checkin!\nError Message: {resp.get('m')}")
        return resp.get('m')

    def xisu_ncov_checkin(self) -> str:
        report_page_resp = self.session.get(XISU_HISTORY_DATA, allow_redirects=False,
                                            timeout=API_TIMEOUT)
        if report_page_resp.status_code != 200:
            raise ConnectionError(f"Failed to Xisu Checkin\nError Code: {report_page_resp.status_code}")
        data = report_page_resp.json()
        report_page_resp = self.session.get(REPORT_PAGE, allow_redirects=False,
                                            timeout=API_TIMEOUT)
        if report_page_resp.status_code != 200:
            raise ConnectionError(f"Failed to Xisu Checkin\nError Code: {report_page_resp.status_code}")
        if "realname" not in report_page_resp.text:
            raise NoLoginException("Failed to Xisu Checkin\nNo Login")

        post_data = xisu_report_parser(report_page_resp.text, data)
        final_resp = self.session.post(XISU_REPORT_API, post_data,
                                       headers={'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest'},
                                       timeout=API_TIMEOUT)
        if final_resp.status_code != 200:
            raise ConnectionError(f"Failed to Xisu Checkin\nError Code: {report_page_resp.status_code}")
        if (resp := final_resp.json()).get('e'):
            raise ConnectionError(f"Failed to Xisu Checkin!\nError Message: {resp.get('m')}")
        return resp.get('m')
