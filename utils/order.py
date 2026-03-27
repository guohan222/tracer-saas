import string,secrets
from datetime import datetime  # 正确导入datetime类

def generate_order():
    # %Y%m%d%H%M%S 包含：年、月、日、时、分、秒
    date_str = datetime.now().strftime("%Y%m%d%H%M%S")
    chars = string.ascii_letters + string.digits
    secrets_str = "".join(secrets.choice(chars) for _ in range(6))
    order = date_str + secrets_str
    return order