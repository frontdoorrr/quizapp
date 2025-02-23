#!/bin/bash
set -e

# 테스트 DB가 준비될 때까지 대기
until PGPASSWORD=postgres psql -h test-db -U postgres -d testdb -c '\q'; do
  >&2 echo "테스트 데이터베이스 준비 중..."
  sleep 1
done

# Poetry 환경에서 테스트 실행
poetry run pytest "$@"
