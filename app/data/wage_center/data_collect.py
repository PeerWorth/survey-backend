import asyncio

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.wage_center.constant import AGE_GROUP_WAGE_PATH
from app.module.asset.enum import AgeGroup
from app.module.asset.model import SalaryStat
from app.module.asset.repository.salary_stat_repository import SalaryStatRepository
from database.dependency import get_mysql_session

# 링크 => https://www.wage.go.kr/whome/wage/wagesearch2.do?menuNo=102010100


async def save_age_group_wage(session: AsyncSession):
    """
    엑셀에서 나이대별 통계(하위/중위/평균/상위)를 읽어
    AgeGroup enum 순서대로 SalaryStat 객체를 생성하고 저장합니다.
    """

    df = pd.read_excel(AGE_GROUP_WAGE_PATH)

    enum_list = list(AgeGroup)

    for idx, record in enumerate(df.to_dict(orient="records")):
        if idx < len(enum_list):
            age_group_enum = enum_list[idx]
        else:
            print(f"⚠️  AgeGroup enum이 부족합니다: row {idx + 1} 건너뜀")
            continue

        lower = int(record.get("하위", record.get("lower")))
        avg = int(record.get("평균", record.get("avg")))
        upper = int(record.get("상위", record.get("upper")))

        stat = SalaryStat(
            job_id=None, experience=None, age_group=age_group_enum.value, lower=lower, avg=avg, upper=upper
        )

        saved = await SalaryStatRepository.upsert_by_age_group(session, stat)
        if saved:
            print(f">>> 저장 완료: id={saved.id}, age_group={saved.age_group}")
        else:
            print(f">>> 저장 실패: age_group={age_group_enum.value}")

    return df


async def main():
    async with get_mysql_session() as session:
        await save_age_group_wage(session)


if __name__ == "__main__":
    asyncio.run(main())
