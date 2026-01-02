import jwt
from django.conf import settings
from datetime import datetime, timedelta

JWT_SECRET = settings.SECRET_KEY
JWT_ALGO = 'HS256'
JWT_EXP_MINUTES = 60


def generate_jwt(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    return token


def decode_jwt(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def is_employer(user):
    return user.is_authenticated and user.role == 'employer'

def is_jobseeker(user):
    return user.is_authenticated and user.role == 'jobseeker'
