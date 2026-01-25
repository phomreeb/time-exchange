import secrets
import string

def generate_otp(length=6):
    digits = string.digits
    strings = string.ascii_letters
    otp = "".join(secrets.choice(digits) for _ in range(length))
    ref = "".join(secrets.choice(strings) for _ in range(length))
    return otp, ref
