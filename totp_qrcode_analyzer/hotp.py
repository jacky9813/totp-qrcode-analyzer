"""
    Implementation of RFC 4226 HOTP: An HMAC-Based One-Time Password Algorithm
"""

import urllib.parse
import hmac
import base64
import typing
from qrcode.main import QRCode


T = typing.TypeVar("T")


class HOTP:
    otp_type: str = "hotp"


    def __init__(
        self,
        secret: typing.Union[bytes, str],
        *,
        counter: typing.Optional[int] = None,
        digits: typing.Literal[6, 8] = 6,
        algorithm: str = "sha1",
        **additional_info
    ):
        if not secret:
            raise ValueError("secret cannot be empty")
        if not isinstance(secret, (bytes, str)):
            raise TypeError("secret must be a str or bytes")
        if isinstance(secret, str):
            padding_length = 8 - (len(secret) % 8) if len(secret) % 8 else 0
            secret = base64.b32decode(f'{secret}{"=" * padding_length}')
        self._shared_secret = secret
        self._counter = int(counter or 0)
        self._digest = algorithm.lower()
        self._digits = int(digits)
        self._byteorder: typing.Literal["little", "big"] = "big"
        for v in additional_info.values():
            if not isinstance(v, str):
                raise TypeError("All additional info must be a string")
        self.additional_info: typing.Dict[str, str] = additional_info


    @property
    def secret(self) -> str:
        "Base-32 encoded secret."
        return base64.b32encode(self._shared_secret).decode().strip("=")


    @property
    def C(self) -> bytes:
        "Get and advance the HOTP counter."
        c = self._counter
        if not c:
            c = 0
        self._counter = c + 1
        return c.to_bytes(8, self._byteorder, signed=False)


    @property
    def K(self) -> bytes:
        "The shared secret."
        return self._shared_secret


    @property
    def digits(self) -> int:
        return self._digits


    def dynamic_truncation(self, value: bytes) -> int:
        offset_bits = value[-1] & 0x0F
        s_num = int.from_bytes(
            value[offset_bits:offset_bits+4], 
            self._byteorder,
            signed=False
        )
        return s_num & 0x7FFFFFFF


    def get_code(self, counter: typing.Optional[int] = None) -> str:
        hs = hmac.new(
            self.K,
            counter.to_bytes(8, self._byteorder, signed=False)
                if counter else self.C,
            self._digest
        ).digest()
        s_num = self.dynamic_truncation(hs)
        return "".join([
            "0" * self.digits,
            str(s_num % (10 ** self.digits))
        ])[-self.digits:]
    

    def __getitem__(self, key: str) -> str:
        return self.additional_info[key]
    

    def get(self, key: str, default: T) -> typing.Union[str, T]:
        return self.additional_info.get(key, default)


    def __setitem__(self, key: str, value: str) -> None:
        if not isinstance(key, str):
            raise TypeError("key must be str")
        if not isinstance(value, str):
            raise TypeError("value must be string")
        self.additional_info[key] = value


    def to_dict(self) -> typing.Dict[str, typing.Union[str, int]]:
        return {
            k: v
            for k, v in {
                "secret": self.secret,
                "algorithm": self._digest.upper(),
                "digits": self.digits,
                "counter": self._counter,
                **self.additional_info
            }.items()
            if v
        }


    def to_uri(self) -> str:
        uri = urllib.parse.ParseResult(
            "otpauth",
            self.otp_type,
            f'/{self.get("label", "")}',
            "",
            urllib.parse.urlencode({
                k: str(v)
                for k, v in self.to_dict().items()
                if k != "label"
            }),
            ""
        )
        return urllib.parse.urlunparse(uri)


    def print_qrcode(self) -> None:
        uri = self.to_uri()
        qr = QRCode()
        qr.add_data(uri)
        qr.print_ascii(invert=True)
