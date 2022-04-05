from typing import AnyStr, Optional

from Crypto.Cipher import AES


def AES_encrypt(msg: AnyStr,
                key: AnyStr,
                IV: Optional[AnyStr] = None,
                mode: Optional[int] = AES.MODE_ECB,
                encode_mode: Optional[str] = 'UTF-8',
                **kwargs) -> bytes:
    if isinstance(msg, str):
        msg = msg.encode(encode_mode)
    if isinstance(key, str):
        key = key.encode(encode_mode)
    if IV is not None:
        if isinstance(IV, str):
            IV = IV.encode(encode_mode)
        aes = AES.new(key, mode, IV, **kwargs)
    else:
        aes = AES.new(key, mode, **kwargs)
        IV = aes.IV
    return aes.encrypt(msg)
