from datetime import datetime
from zoneinfo import ZoneInfo


def current_time_kst():
    KST = ZoneInfo("Asia/Seoul")
    return datetime.now(KST)
