import random
import time
import uuid
from typing import TYPE_CHECKING

from locust import HttpUser, SequentialTaskSet, between, task
from locust.clients import HttpSession


class UserJourney(SequentialTaskSet):
    if TYPE_CHECKING:
        client: HttpSession

    def on_start(self):
        """사용자별 고유 데이터 초기화"""
        self.unique_id = str(uuid.uuid4())
        self.jobs_data = []
        self.selected_job = None

    @task
    def get_jobs(self):
        """1단계: 직무 목록 조회 및 저장"""
        response = self.client.get("/api/asset/v1/jobs")
        if response.status_code == 200:
            data = response.json()
            if data.get("data", {}).get("items"):
                self.jobs_data = data["data"]["items"]
                self.selected_job = random.choice(self.jobs_data)

        time.sleep(random.uniform(5, 10))

    @task
    def submit_salary(self):
        """2단계: 연봉 정보 제출 (UserSalaryPostRequest 스키마 준수)"""
        if not self.selected_job:
            return

        payload = {
            "uniqueId": self.unique_id,
            "jobId": self.selected_job["id"],  # JobItem의 id 필드 사용
            "experience": random.randint(0, 10),  # ge=0, le=10
            "salary": random.randint(1, 100000),  # gt=0, le=100_000 (단위: 만원)
        }

        response = self.client.post("/api/asset/v1/salary", json=payload)
        if response.status_code not in [200, 201]:
            print(f"❌ Salary failed: {response.status_code} - job_id: {self.selected_job['id']}")

        time.sleep(random.uniform(10, 20))

    @task
    def submit_profile(self):
        """3단계: 프로필 정보 제출 (UserProfilePostRequest 스키마 준수)"""
        payload = {
            "uniqueId": self.unique_id,
            "age": random.randint(18, 50),  # ge=18, le=50
            "saveRate": random.randint(0, 100),  # ge=0, le=100
            "hasCar": random.choice([True, False]),  # 자동차 보유 여부
            "isMonthlyRent": random.choice([True, False]),  # 월세 여부
        }

        response = self.client.post("/api/asset/v1/profile", json=payload)
        if response.status_code not in [200, 201]:
            print(f"❌ Profile failed: {response.status_code} - {response.text}")

        time.sleep(random.uniform(10, 20))

    @task
    def submit_email(self):
        """4단계: 이메일 정보 제출 (같은 uniqueId 사용해야 함)"""
        timestamp = int(time.time() * 1000000)
        unique_email = f"test_{self.unique_id}_{timestamp}@example.com"

        payload = {
            "uniqueId": self.unique_id,
            "email": unique_email,
            "agree": random.choice([True, False]),
        }

        response = self.client.post("/api/user/v1/email", json=payload)
        if response.status_code not in [200, 201]:
            print(f"❌ Email failed: {response.status_code} - {response.text}")


class BrowsingUser(HttpUser):
    wait_time = between(2, 5)
    weight = 1

    @task
    def browse_jobs(self):
        """직무 목록만 조회"""
        self.client.get("/api/asset/v1/jobs")


class SequentialUser(HttpUser):
    """순서대로 API를 호출하는 주요 사용자"""

    tasks = [UserJourney]
    wait_time = between(1, 3)
    weight = 3
