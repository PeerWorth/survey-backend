import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

source_db_url = os.getenv("DEV_MYSQL_URL")
target_db_url = os.getenv("PROD_MYSQL_URL")

TABLES_TO_COPY = ["job", "job_group", "salary_stat"]


async def copy_tables():
    source_engine = create_async_engine(source_db_url)
    target_engine = create_async_engine(target_db_url)

    source_session = sessionmaker(source_engine, class_=AsyncSession, expire_on_commit=False)
    target_session = sessionmaker(target_engine, class_=AsyncSession, expire_on_commit=False)

    async with source_session() as source_db:
        async with target_session() as target_db:
            # 외래 키 체크 비활성화
            await target_db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

            for table_name in TABLES_TO_COPY:
                print(f"Copying table: {table_name}")

                # 타겟 테이블 비우기
                await target_db.execute(text(f"TRUNCATE TABLE {table_name}"))
                await target_db.commit()

                # 소스에서 데이터 가져오기
                result = await source_db.execute(text(f"SELECT * FROM {table_name}"))
                rows = result.fetchall()

                if rows:
                    # 컬럼 이름 가져오기
                    columns = result.keys()
                    column_names = ", ".join(columns)
                    placeholders = ", ".join([f":{col}" for col in columns])

                    # 타겟에 데이터 삽입
                    insert_query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

                    # 각 행을 딕셔너리로 변환
                    data = [dict(zip(columns, row)) for row in rows]

                    # 배치 삽입
                    await target_db.execute(text(insert_query), data)
                    await target_db.commit()

                    print(f"{len(rows)}개의 행을 복사합니다. {table_name=}")
                else:
                    print(f"데이터가 존재하지 않습니다. {table_name=}")

            # 외래 키 체크 다시 활성화
            await target_db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            await target_db.commit()

    await source_engine.dispose()
    await target_engine.dispose()
    print("복사 완료 되었습니다!")


if __name__ == "__main__":
    asyncio.run(copy_tables())
