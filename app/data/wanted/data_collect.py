import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# [참조 링크] https://www.wanted.co.kr/salary/숫자


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
driver.get("https://www.wanted.co.kr/salary/10110")

wait = WebDriverWait(driver, 10)


rectangles = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "path.recharts-rectangle")))
actions = ActionChains(driver)
tooltip_data = {}  # {경력: 연봉} 형태의 데이터 저장

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
            print(f"Tooltip {idx + 1}: {years} -> {salary_num}")
        else:
            print(f"Tooltip {idx + 1} 텍스트 형식 오류: {text}")
    except Exception as e:
        print(f"Tooltip {idx + 1}를 찾지 못했습니다. 에러: {e}")

    time.sleep(0.5)

# 2. select 요소 값 추출 (title: "직군", "직무", "경력")
try:
    job_group_select = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'select[title="직군"]')))
    job_group = Select(job_group_select).first_selected_option.text.strip()
except Exception as e:
    print(f'"직군" select 요소를 찾지 못했습니다: {e}')
    job_group = None

try:
    job_select = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'select[title="직무"]')))
    job = Select(job_select).first_selected_option.text.strip()
except Exception as e:
    print(f'"직무" select 요소를 찾지 못했습니다: {e}')
    job = None

try:
    year_select = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'select[title="경력"]')))
    selected_year = Select(year_select).first_selected_option.text.strip()
    selected_year = 0 if selected_year == "신입" else selected_year
except Exception as e:
    print(f'"경력" select 요소를 찾지 못했습니다: {e}')
    selected_year = None

# 3. 최종 결과 객체 생성 및 출력
result = {"job_group": job_group, "job": job, "year": selected_year, "tooltip_data": tooltip_data}

driver.quit()

print("최종 결과:", result)
