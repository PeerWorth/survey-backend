import asyncio
import time
from os import getenv

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from app.common.enums import EnvironmentType
from app.data.excel import load_excel
from app.data.wanted.source.dto import JobData, TooltipData
from app.module.asset.model import Job, JobGroup, SalaryStat
from app.module.asset.repositories.job_group_repository import JobGroupRepository
from app.module.asset.repositories.job_repository import JobRepository
from app.module.asset.repositories.salary_stat_repository import SalaryStatRepository
from database.dependency import get_mysql_session_router

load_dotenv()

ENVIRONMENT = getenv("ENVIRONMENT", None)

# [참조 링크] https://www.wanted.co.kr/salary/숫자


async def get_wanted_job_num_preset(number: int, driver: webdriver.Chrome) -> JobData | None:
    try:
        driver.get(f"https://www.wanted.co.kr/salary/{number}")

        wait = WebDriverWait(driver, 10)

        rectangles = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "path.recharts-rectangle")))
        actions = ActionChains(driver)
    except Exception:
        return None

    tooltip_data = {}
    for idx, rect in enumerate(rectangles):
        actions.move_to_element(rect).perform()

        try:
            tooltip = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".recharts-tooltip-wrapper"))
            )
            text = tooltip.text.strip()
            lines = text.splitlines()
            if len(lines) >= 2:
                exp_str = lines[0].strip()
                salary_str = lines[1].strip()

                years = 0 if exp_str == "신입" else int(exp_str.replace("년", "").strip())
                salary_num = int(salary_str.replace(",", "").replace("만원", "").strip())
                tooltip_data[years] = salary_num
        except Exception:
            return None

        time.sleep(0.5)

    try:
        job_group_select = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'select[title="직군"]')))
        job_group = Select(job_group_select).first_selected_option.text.strip()
    except Exception:
        return None

    try:
        job_select = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'select[title="직무"]')))
        job = Select(job_select).first_selected_option.text.strip()
    except Exception:
        return None

    tooltip_data_list = [TooltipData(experience=year, salary=salary) for year, salary in tooltip_data.items()]

    return JobData(job_group=job_group, job=job, tooltip_data=tooltip_data_list)


async def main():
    wanted_job_rows = load_excel("./etc/wanted_job.xlsx")
    session = get_mysql_session_router()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--window-size=1200,800")

    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
    )
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    if ENVIRONMENT == EnvironmentType.LOCAL.value or ENVIRONMENT == EnvironmentType.TEST.value:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    elif ENVIRONMENT == EnvironmentType.PROD.value:
        # TODO: 일회성 chrome driver 설치하여 저장함. 별도 자동화 필요
        driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=chrome_options)

    job_group_repo = JobGroupRepository(session)
    job_repo = JobRepository(session)
    salary_stat_repo = SalaryStatRepository(session)

    for wanted_job_row in wanted_job_rows:
        preset_data: JobData | None = await get_wanted_job_num_preset(wanted_job_row[0], driver)

        if not preset_data:
            print(wanted_job_row[0])
            continue

        job_group_name = preset_data.job_group
        job_name = preset_data.job
        tooltip_data_list: list[TooltipData] = preset_data.tooltip_data

        print(f"{job_group_name=}, {job_name=}")

        job_group: JobGroup | None = await job_group_repo.get_by_name(job_group_name)
        if not job_group:
            cur_job_group = JobGroup(name=job_group_name)
            job_group = await job_group_repo.save(cur_job_group)
            if not job_group:
                continue

        assert job_group.id is not None
        job = await job_repo.find_by_group_and_name(job_group.id, job_name)
        if not job:
            if job_name == "전체":
                job_name = f"{job_group_name} 전체"

            new_job = Job(group_id=job_group.id, name=job_name)
            job = await job_repo.save(new_job)
            if not job:
                continue

        assert job.id  # SQLModel 특성상, 데이터 타입 존재 확인 필요
        for tooltip_data in tooltip_data_list:
            tooltip_data: TooltipData

            avg = int(tooltip_data.salary) * 10_000  # 천만원 단위 곱
            salary_stat = await salary_stat_repo.get_by_job_id_experience(job.id, tooltip_data.experience)
            if not salary_stat:
                salary_stat = SalaryStat(
                    job_id=job.id,
                    experience=tooltip_data.experience,
                    avg=avg,
                )
                await salary_stat_repo.save(salary_stat)

    driver.quit()


if __name__ == "__main__":
    asyncio.run(main())
