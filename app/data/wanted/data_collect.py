import asyncio
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from app.data.wanted.source.constant import JOB_KEYS
from app.data.wanted.source.dto import JobData, TooltipData
from app.module.asset.model import Job, JobGroup, SalaryStat
from app.module.asset.repositories.job_group_repository import JobGroupRepository
from app.module.asset.repositories.job_repository import JobRepository
from app.module.asset.repositories.salary_stat_repository import SalaryStatRepository
from database.dependency import get_mysql_session

# [참조 링크] https://www.wanted.co.kr/salary/숫자


# [(10110, '소프트웨어 엔지니어', '개발'), (10111, '크로스플랫폼 앱 개발자', '개발'), (10112, 'VR 엔지니어', '개발'), (10113, '섬유·의류·패션', '제조·생산'), (10114, '반도체·디스플레이', '제조·생산'), (10115, '해외 사업개발·기획자', '경영·비즈니스'), (10116, '자금담당', '경영·비즈니스'), (10117, '전시 기획자', '경영·비즈니스'), (10118, '세미나/포럼 기획자', '경영·비즈니스'), (10119, '공연 기획자', '경영·비즈니스'), (10120, '애자일코치', '경영·비즈니스'), (10121, '사내 심리상담가', '경영·비즈니스'), (10122, '사무보조', '경영·비즈니스'), (10123, '미용사', '고객서비스·리테일'), (10125, '리셉션', '고객서비스·리테일'), (10126, '서비스 운영', '고객서비스·리테일'), (10127, '가구 디자이너', '디자인'), (10128, '패브릭 디자이너', '디자인'), (10129, '전시 디자이너', '디자인'), (10130, '패키지 디자이너', '디자인'), (10131, 'VMD', '디자인'), (10132, 'CAD·3D 설계자', '엔지니어링·설계'), (10134, '병원 코디네이터', '의료·제약·바이오'), (10135, '의무기록사', '의료·제약·바이오'), (10138, '퍼포먼스 마케터', '마케팅·광고'), (10139, '관세사', '물류·무역'), (10140, '원산지관리사', '물류·무역'), (10141, '푸드스타일리스트', '식·음료'), (10142, '실내건축', '건설·시설'), (10143, '건축시공·감리', '건설·시설'), (10144, '건설 안전·품질·검사', '건설·시설'), (10145, '로봇·자동화', '엔지니어링·설계'), (10147, '임상심리사', '의료·제약·바이오'), (10148, '입·출고 관리자', '물류·무역'), (10149, '유통 관리자', '물류·무역'), (10150, '바이어관리·상담·개발', '물류·무역'), (10151, '수출입사무', '물류·무역'), (10152, '소믈리에', '식·음료'), (10153, '식품가공·개발', '식·음료'), (10154, '바리스타', '식·음료'), (10230, 'ERP전문가', '개발'), (10231, 'DBA', '개발'), (10232, '상품기획자(BM)', '경영·비즈니스'), (10235, '연예,엔터테인먼트', '미디어'), (10236, '항해사', '물류·무역'), (10237, '기관사', '물류·무역'), (1030, '디지털 마케터', '마케팅·광고'), (1031, 'Sports 전문가', '마케팅·광고'), (1032, '마케팅 디렉터', '마케팅·광고'), (1033, '모바일마케팅', '마케팅·광고'), (1034, '회계·경리', '경영·비즈니스'), (1035, '솔루션 컨설턴트', '영업'), (1036, '기업영업', '영업'), (1037, '고객성공매니저', '영업'), (10375, '캐디', '고객서비스·리테일'), (1040, '한의사', '의료·제약·바이오'), (1041, '헤드헌터', 'HR'), (1042, '교수', 'HR'), (1043, 'HRBP', 'HR'), (1044, '사내 강사', 'HR'), (1045, '큐레이터', '미디어'), (1046, '콘텐츠 크리에이터', '미디어'), (10527, 'CRM 마케터', '마케팅·광고'), (10530, 'UX 리서처', '디자인'), (10531, 'RPA 엔지니어', '개발'), (10532, '콘텐츠 디자이너', '디자인'), (10533, '사운드 디자이너', '미디어'), (10534, '조명 엔지니어', '미디어'), (10535, '콘텐츠 에디터', '미디어'), (10536, '테크니컬 라이터', '개발'), (1633, '미디어 세일즈', '영업'), (1634, '머신러닝 엔지니어', '개발'), (1635, '콘텐츠 마케터', '마케팅·광고'), (1636, '라이센스 관리자', '미디어'), (1637, '헬스케어매니저', '고객서비스·리테일'), (3351, '비디오 제작', '미디어')]


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
    async with get_mysql_session() as session:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1200,800")
        chrome_options.add_argument("--enable-automation")

        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/89.0.4389.90 Safari/537.36"
        )
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        job_group_repo = JobGroupRepository(session)
        job_repo = JobRepository(session)
        salary_stat_repo = SalaryStatRepository(session)

        for job_num in JOB_KEYS:
            preset_data: JobData | None = await get_wanted_job_num_preset(job_num, driver)

            if not preset_data:
                print(job_num)
                continue

            job_group_name = preset_data.job_group
            job_name = preset_data.job
            tooltip_data_list: list[TooltipData] = preset_data.tooltip_data

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

            assert job.id is not None
            for tooltip_data in tooltip_data_list:
                tooltip_data: TooltipData

                avg = int(tooltip_data.salary) * 10_000_000
                salary_stat = await salary_stat_repo.get(job.id)
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
