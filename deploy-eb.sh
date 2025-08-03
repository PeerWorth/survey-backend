#!/bin/bash

# Elastic Beanstalk 배포 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 환경 변수 확인
if [ -z "$1" ]; then
    echo -e "${RED}Error: 환경을 지정해주세요 (dev 또는 prod)${NC}"
    echo "Usage: ./deploy-eb.sh [dev|prod]"
    exit 1
fi

ENV=$1
TIMESTAMP=$(date +%Y%m%d%H%M%S)
APP_NAME="olass-${ENV}"
ZIP_FILE="deploy-${ENV}-${TIMESTAMP}.zip"

echo -e "${GREEN}Starting Elastic Beanstalk deployment for ${ENV} environment...${NC}"

# 1. 배포 파일 준비
echo -e "${YELLOW}1. Preparing deployment files...${NC}"
mkdir -p .ebdeploy

# 필요한 파일들을 복사
cp Dockerfile .ebdeploy/
cp docker-compose.${ENV}.yml .ebdeploy/docker-compose.yml
# Dockerrun.aws.json은 제외 - docker-compose.yml 사용
cp -r app .ebdeploy/
cp pyproject.toml .ebdeploy/
cp poetry.lock .ebdeploy/
cp alembic.ini .ebdeploy/
cp -r alembic .ebdeploy/
cp main.py .ebdeploy/

# 선택적 파일들 (있으면 복사)
[ -f dependencies.py ] && cp dependencies.py .ebdeploy/
[ -f main_config.py ] && cp main_config.py .ebdeploy/
[ -d database ] && cp -r database .ebdeploy/

# .env 파일은 제외 (Elastic Beanstalk 환경 변수 사용)

# 2. ZIP 파일 생성
echo -e "${YELLOW}2. Creating deployment package...${NC}"
cd .ebdeploy
zip -r ../${ZIP_FILE} . -x "*.pyc" -x "*__pycache__*" -x "*.pytest_cache*" -x "*.mypy_cache*"
cd ..

# 3. S3에 업로드
echo -e "${YELLOW}3. Uploading to S3...${NC}"
S3_BUCKET=$(cd infra/infrastructure && terraform output -raw eb_deployment_bucket 2>/dev/null || echo "")

if [ -z "$S3_BUCKET" ]; then
    echo -e "${RED}Error: S3 bucket not found. Make sure infrastructure is deployed.${NC}"
    rm -rf .ebdeploy ${ZIP_FILE}
    exit 1
fi

aws s3 cp ${ZIP_FILE} s3://${S3_BUCKET}/

# 4. 새 애플리케이션 버전 생성
echo -e "${YELLOW}4. Creating application version...${NC}"
EB_APP_NAME=$(cd infra/infrastructure && terraform output -raw eb_application_name 2>/dev/null)
VERSION_LABEL="${ENV}-${TIMESTAMP}"

aws elasticbeanstalk create-application-version \
    --application-name ${EB_APP_NAME} \
    --version-label ${VERSION_LABEL} \
    --source-bundle S3Bucket=${S3_BUCKET},S3Key=${ZIP_FILE} \
    --description "Deployment at ${TIMESTAMP}"

# 5. 환경 업데이트
echo -e "${YELLOW}5. Updating environment...${NC}"
EB_ENV_NAME=$(cd infra/infrastructure && terraform output -raw eb_environment_name 2>/dev/null)

aws elasticbeanstalk update-environment \
    --environment-name ${EB_ENV_NAME} \
    --version-label ${VERSION_LABEL}

# 6. 정리
echo -e "${YELLOW}6. Cleaning up...${NC}"
rm -rf .ebdeploy ${ZIP_FILE}

echo -e "${GREEN}Deployment initiated successfully!${NC}"
echo -e "${YELLOW}Monitor deployment status:${NC}"
echo "aws elasticbeanstalk describe-environments --environment-names ${EB_ENV_NAME}"
echo ""
echo -e "${YELLOW}Or check logs:${NC}"
echo "cd infra/infrastructure && make eb-status"
