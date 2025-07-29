"""데이터베이스 모니터링 설정"""

from app.common.monitoring.query_monitor import query_monitor
from database.config import mysql_engine


def setup_database_monitoring():
    """데이터베이스 쿼리 모니터링 설정"""
    # AsyncEngine의 sync_engine 속성을 사용해야 함
    query_monitor.setup_query_monitoring(mysql_engine.sync_engine)
