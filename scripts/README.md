# Quiz App Scripts 사용 가이드

이 디렉토리에는 Quiz App 관리에 필요한 유틸리티 스크립트들이 포함되어 있습니다.
모든 스크립트는 도커 컨테이너 내에서 실행되어야 합니다.

## 스크립트 실행 방법

### 1. 데이터베이스 설정 (db_setup.py)
데이터베이스 테이블을 생성하고 초기 설정을 수행합니다.

```bash
# 컨테이너 내부에서 실행
docker exec -it quizapp python scripts/db_setup.py

# 또는 docker compose를 사용하는 경우
docker compose exec app python scripts/db_setup.py
```

### 2. 관리자 계정 생성 (create_admin.py)
새로운 관리자 계정을 생성합니다.

```bash
# 컨테이너 내부에서 실행
docker exec -it quizapp python scripts/create_admin.py --email admin@example.com --password your_secure_password

# 또는 docker compose를 사용하는 경우
docker compose exec app python scripts/create_admin.py --email admin@example.com --password your_secure_password
```

### 3. 테스트 데이터 생성 (generate_test_data.py)
개발 및 테스트 목적으로 샘플 데이터를 생성합니다.

```bash
# 기본 설정으로 실행 (10명의 사용자, 5개의 게임)
docker exec -it quizapp python scripts/generate_test_data.py

# 사용자 및 게임 수 지정
docker exec -it quizapp python scripts/generate_test_data.py --users 20 --games 10

# 또는 docker compose를 사용하는 경우
docker compose exec app python scripts/generate_test_data.py --users 20 --games 10
```

### 4. 데이터베이스 백업 (backup_db.py)
데이터베이스의 백업을 생성합니다.

```bash
# 기본 백업 디렉토리(backups/)에 백업 생성
docker exec -it quizapp python scripts/backup_db.py

# 사용자 지정 디렉토리에 백업 생성
docker exec -it quizapp python scripts/backup_db.py --backup-dir /app/custom_backups

# 또는 docker compose를 사용하는 경우
docker compose exec app python scripts/backup_db.py --backup-dir /app/custom_backups
```

## 주의사항

1. 모든 스크립트는 애플리케이션의 루트 디렉토리(`/app`)에서 실행됩니다.
2. 스크립트 실행 전 환경 변수가 올바르게 설정되어 있는지 확인하세요.
3. 백업 파일은 컨테이너 내부의 지정된 디렉토리에 생성됩니다. 필요한 경우 호스트 시스템으로 복사하세요.
4. 프로덕션 환경에서 `generate_test_data.py`를 실행하지 마세요.

## 백업 파일 호스트로 복사하기

백업 파일을 호스트 시스템으로 복사하려면 다음 명령어를 사용하세요:

```bash
# 단일 컨테이너 사용 시
docker cp quizapp:/app/backups ./host_backups

# docker compose 사용 시
docker compose cp app:/app/backups ./host_backups
```

## 문제 해결

1. 스크립트 실행 권한 오류 발생 시:
```bash
# 컨테이너 내부에서 스크립트에 실행 권한 부여
docker exec -it quizapp chmod +x scripts/*.py
```

2. 데이터베이스 연결 오류 발생 시:
   - 환경 변수가 올바르게 설정되어 있는지 확인
   - 데이터베이스 서비스가 실행 중인지 확인
   - 네트워크 설정 확인
