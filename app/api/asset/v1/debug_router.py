"""Asset API 쿼리 분석용 디버그 라우터"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.monitoring.query_monitor import query_analysis_context, query_monitor
from app.module.asset.services.asset_service import AssetService
from database.dependency import get_mysql_session_router

debug_router = APIRouter(prefix="/debug", tags=["debug"])


@debug_router.get("/query-stats", summary="쿼리 실행 통계")
async def get_query_stats() -> Dict[str, Any]:
    """전체 쿼리 실행 통계 조회"""
    return query_monitor.get_query_summary()


@debug_router.get("/slow-queries", summary="슬로우 쿼리 목록")
async def get_slow_queries(limit: int = 10) -> List[Dict[str, Any]]:
    """슬로우 쿼리 목록 조회"""
    return query_monitor.get_slow_queries(limit)


@debug_router.post("/clear-stats", summary="통계 초기화")
async def clear_query_stats():
    """쿼리 통계 초기화"""
    query_monitor.clear_stats()
    return {"message": "Query statistics cleared"}


@debug_router.get("/analyze-jobs", summary="Jobs API 쿼리 분석")
async def analyze_jobs_queries(
    asset_service: AssetService = Depends(), session: AsyncSession = Depends(get_mysql_session_router)
):
    """Jobs API의 쿼리 분석"""

    with query_analysis_context(session, enable_explain=True) as monitor:
        # Jobs API 실행
        jobs = await asset_service.get_jobs()

        # 실행된 쿼리 분석
        recent_queries = monitor.query_stats[-10:] if monitor.query_stats else []

        return {
            "api": "get_jobs",
            "result_count": len(jobs) if jobs else 0,
            "queries_executed": len(recent_queries),
            "query_details": [
                {
                    "sql": q["sql"][:200] + "..." if len(q["sql"]) > 200 else q["sql"],
                    "execution_time": f"{q['execution_time']:.3f}s",
                    "is_slow": q["is_slow"],
                }
                for q in recent_queries
            ],
        }


@debug_router.get("/analyze-profile/{unique_id}", summary="Profile API 쿼리 분석")
async def analyze_profile_queries(
    unique_id: str,
    save_rate: int,
    asset_service: AssetService = Depends(),
    session: AsyncSession = Depends(get_mysql_session_router),
):
    """Profile API의 쿼리 분석"""

    with query_analysis_context(session, enable_explain=True) as monitor:
        start_count = len(monitor.query_stats)

        try:
            # Profile API 실행
            import uuid

            user_uuid = uuid.UUID(unique_id)

            car = await asset_service.get_user_car(user_uuid, save_rate)
            percentage = await asset_service.get_user_percentage(user_uuid, save_rate)

            # 실행된 쿼리 분석
            new_queries = monitor.query_stats[start_count:]

            return {
                "api": "user_profile",
                "unique_id": unique_id,
                "save_rate": save_rate,
                "result": {"car": car, "percentage": percentage},
                "queries_executed": len(new_queries),
                "query_details": [
                    {
                        "sql": q["sql"][:200] + "..." if len(q["sql"]) > 200 else q["sql"],
                        "execution_time": f"{q['execution_time']:.3f}s",
                        "is_slow": q["is_slow"],
                        "parameters": str(q["parameters"])[:100] if q["parameters"] else None,
                    }
                    for q in new_queries
                ],
            }

        except Exception as e:
            new_queries = monitor.query_stats[start_count:]
            return {
                "api": "user_profile",
                "error": str(e),
                "queries_executed": len(new_queries),
                "query_details": [
                    {
                        "sql": q["sql"][:200] + "..." if len(q["sql"]) > 200 else q["sql"],
                        "execution_time": f"{q['execution_time']:.3f}s",
                        "is_slow": q["is_slow"],
                    }
                    for q in new_queries
                ],
            }


@debug_router.post("/explain-query", summary="쿼리 실행계획 분석")
async def explain_query(
    sql: str, params: Dict[str, Any] | None = None, session: AsyncSession = Depends(get_mysql_session_router)
):
    """특정 쿼리의 실행계획 분석"""

    explain_result = await query_monitor.explain_query(session, sql, params or {})

    if "error" not in explain_result:
        # 실행계획 분석
        analysis = query_monitor.analyze_explain_plan(explain_result.get("explain", {}))
        explain_result["analysis"] = analysis

    return explain_result
