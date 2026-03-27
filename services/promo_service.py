import random
import string


def generate_promo_code(prefix: str = "PROMO", length: int = 8) -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}-{suffix}"