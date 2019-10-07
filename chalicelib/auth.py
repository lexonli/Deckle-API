import hashlib
import hmac
import datetime
from uuid import uuid4

import jwt
from chalice import UnauthorizedError

import logging


# TODO: Figure out what we want to do with this.
# We can either move this out to env vars in config.json,
# use KMS to encrypt/decrypt this value, or store this in SSM.
# Until we figure it out I'll store it here.
_SECRET = b'\xf7\xb6k\xabP\xce\xc1\xaf\xad\x86\xcf\x84\x02\x80\xa0\xe0'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_jwt_token(username, password, record):
    actual = hashlib.pbkdf2_hmac(
        record['hash'],
        password.encode(),
        record['salt'].value,
        record['rounds']
    )
    logger.info(actual)
    expected = record['hashed'].value
    logger.info(expected)
    if hmac.compare_digest(actual, expected):
        now = datetime.datetime.utcnow()
        unique_id = str(uuid4())
        payload = {
            'sub': username,
            'iat': now,
            'nbf': now,
            'jti': unique_id,
            # NOTE: We can also add 'exp' if we want tokens to expire.
        }
        return jwt.encode(payload, _SECRET, algorithm='HS256')
    raise UnauthorizedError('Invalid password')


def decode_jwt_token(token):
    return jwt.decode(token, _SECRET, algorithms=['HS256'])
