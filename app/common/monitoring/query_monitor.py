"""SQLAlchemy 쿼리 모니터링 시스템"""

import logging
import time
from contextlib import contextmanager
from typing import Any, Dict, List

from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


class QueryMonitor:
    """쿼리 실행계획 및 성능 모니터링"""

    def __init__(self, slow_query_threshold: float = 0.2):
        """
        Args:
            slow_query_threshold: 슬로우 쿼리 임계값 (초)
        """
        self.slow_query_threshold = slow_query_threshold
        self.query_stats: List[Dict[str, Any]] = []

    def setup_query_monitoring(self, engine: Engine | AsyncEngine):
        """쿼리 모니터링 이벤트 리스너 설정"""

        @event.listens_for(engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
            context._statement = statement
            context._parameters = parameters

        @event.listens_for(engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total_time = time.time() - context._query_start_time

            query_info = {
                "sql": statement,
                "parameters": parameters,
                "execution_time": total_time,
                "is_slow": total_time > self.slow_query_threshold,
                "timestamp": time.time(),
            }

            self.query_stats.append(query_info)

            if query_info["is_slow"]:
                logger.warning(
                    f"Slow Query Detected: {total_time:.3f}s\n" f"SQL: {statement}\n" f"Params: {parameters}"
                )

    async def explain_query(self, session, sql: str, params: dict | None = None) -> dict:
        """쿼리 실행계획 조회"""
        try:
            # MySQL EXPLAIN 실행
            explain_sql = f"EXPLAIN FORMAT=JSON {sql}"
            result = await session.execute(text(explain_sql), params or {})
            explain_data = result.scalar()

            return {"sql": sql, "params": params, "explain": explain_data}
        except Exception as e:
            logger.error(f"Failed to explain query: {e}")
            return {"error": str(e)}

    def analyze_explain_plan(self, explain_data: dict) -> Dict[str, Any]:
        """실행계획 분석"""
        analysis: Dict[str, Any] = {"issues": [], "recommendations": [], "index_usage": [], "table_scans": []}

        try:
            query_block = explain_data.get("query_block", {})
            table = query_block.get("table", {})

            # 인덱스 사용 여부 확인
            access_type = table.get("access_type", "")
            if access_type in ["ALL", "index"]:
                analysis["issues"].append(f"Full table scan detected: {access_type}")
                analysis["recommendations"].append("Consider adding appropriate indexes")

            # 사용된 인덱스 정보
            if "key" in table:
                analysis["index_usage"].append(
                    {
                        "table": table.get("table_name", ""),
                        "index": table.get("key", ""),
                        "key_length": table.get("key_length", ""),
                    }
                )

            # 검사된 행 수
            rows_examined = table.get("rows_examined_per_scan", 0)
            if rows_examined > 1000:
                analysis["issues"].append(f"High row examination: {rows_examined}")
                analysis["recommendations"].append("Consider optimizing WHERE conditions")

        except Exception as e:
            logger.error(f"Failed to analyze explain plan: {e}")
            analysis["error"] = str(e)

        return analysis

    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """슬로우 쿼리 목록 조회"""
        slow_queries = [q for q in self.query_stats if q["is_slow"]]
        return sorted(slow_queries, key=lambda x: x["execution_time"], reverse=True)[:limit]

    def get_query_summary(self) -> Dict[str, Any]:
        """쿼리 실행 통계 요약"""
        if not self.query_stats:
            return {"total_queries": 0}

        total_queries = len(self.query_stats)
        slow_queries = len([q for q in self.query_stats if q["is_slow"]])
        avg_time = sum(q["execution_time"] for q in self.query_stats) / total_queries
        max_time = max(q["execution_time"] for q in self.query_stats)

        return {
            "total_queries": total_queries,
            "slow_queries": slow_queries,
            "slow_query_rate": slow_queries / total_queries * 100,
            "avg_execution_time": avg_time,
            "max_execution_time": max_time,
            "threshold": self.slow_query_threshold,
        }

    def clear_stats(self):
        """통계 초기화"""
        self.query_stats.clear()


# 전역 쿼리 모니터 인스턴스
query_monitor = QueryMonitor()


@contextmanager
def query_analysis_context(session, enable_explain: bool = False):
    """쿼리 분석 컨텍스트 매니저"""
    start_queries = len(query_monitor.query_stats)

    try:
        yield query_monitor
    finally:
        new_queries = query_monitor.query_stats[start_queries:]

        if new_queries:
            logger.info(f"Executed {len(new_queries)} queries in this context")

            if enable_explain:
                # 슬로우 쿼리에 대해 실행계획 출력
                for query in new_queries:
                    if query["is_slow"]:
                        logger.warning(
                            f"Slow query analysis needed:\n"
                            f"SQL: {query['sql']}\n"
                            f"Time: {query['execution_time']:.3f}s"
                        )
