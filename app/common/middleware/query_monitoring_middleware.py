"""API별 쿼리 모니터링 미들웨어"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.common.monitoring.query_monitor import query_monitor


class QueryMonitoringMiddleware(BaseHTTPMiddleware):
    """API 요청별 쿼리 모니터링 미들웨어"""

    def __init__(self, app: ASGIApp, enable_detailed_logging: bool = False):
        super().__init__(app)
        self.enable_detailed_logging = enable_detailed_logging

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # API 요청 시작 시점의 쿼리 수
        start_query_count = len(query_monitor.query_stats)
        start_time = time.time()

        # API 실행
        response = await call_next(request)

        # API 완료 후 통계 수집
        end_time = time.time()
        api_duration = end_time - start_time

        # 이 API에서 실행된 쿼리들
        api_queries = query_monitor.query_stats[start_query_count:]
        query_count = len(api_queries)

        # 슬로우 쿼리 개수
        slow_queries = [q for q in api_queries if q["is_slow"]]
        slow_query_count = len(slow_queries)

        # 총 쿼리 실행 시간
        total_query_time = sum(q["execution_time"] for q in api_queries)

        # 로깅
        log_data = {
            "method": request.method,
            "path": str(request.url.path),
            "status_code": response.status_code,
            "api_duration": f"{api_duration:.3f}s",
            "query_count": query_count,
            "slow_query_count": slow_query_count,
            "total_query_time": f"{total_query_time:.3f}s",
            "query_ratio": f"{(total_query_time / api_duration * 100):.1f}%" if api_duration > 0 else "0%",
        }

        # 응답 헤더에 쿼리 정보 추가
        response.headers["X-Query-Count"] = str(query_count)
        response.headers["X-Query-Time"] = f"{total_query_time:.3f}"
        response.headers["X-Slow-Query-Count"] = str(slow_query_count)

        # 상세 로깅 (개발환경)
        if self.enable_detailed_logging and (slow_query_count > 0 or query_count > 5):
            import logging

            logger = logging.getLogger(__name__)

            logger.warning(
                f"API Query Analysis: {log_data['method']} {log_data['path']} | "
                f"Queries: {query_count} | Slow: {slow_query_count} | "
                f"Query Time: {log_data['total_query_time']} ({log_data['query_ratio']})"
            )

            # 슬로우 쿼리 상세 정보
            for query in slow_queries:
                logger.warning(f"Slow Query: {query['execution_time']:.3f}s - {query['sql'][:100]}...")

        return response
