FROM python:3.11-slim

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
ENV POETRY_VERSION=1.7.1
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry --version

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 설정
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0

# 프로젝트 의존성 파일 복사
COPY pyproject.toml ./

# poetry.lock 파일 생성 및 의존성 설치
RUN poetry config virtualenvs.create false && \
    poetry lock && \
    poetry install --no-root

# 스크립트 파일 복사 및 권한 설정
COPY scripts/entrypoint.sh /app/scripts/
RUN chmod +x /app/scripts/entrypoint.sh

# 나머지 프로젝트 파일 복사
COPY . .
RUN poetry install

# 실행
ENTRYPOINT ["/bin/sh", "/app/scripts/entrypoint.sh"]
