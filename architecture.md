# 시스템 아키텍처 설계

## 1. 전체 아키텍처 개요

이 시스템은 사용자 관리, 인증, 포인트/코인 관리 기능을 제공하는 마이크로서비스 아키텍처입니다.

## 2. AWS 컴포넌트 구성

### 2.1 컴퓨팅 레이어
- **ECS (Elastic Container Service)**
  - FastAPI 애플리케이션 컨테이너 실행
  - Auto Scaling 구성으로 트래픽 대응
  - Application Load Balancer와 연동

- **AWS Lambda**
  - 이메일 인증 처리
  - 비동기 작업 처리

### 2.2 데이터베이스 레이어
- **Amazon RDS (PostgreSQL)**
  - 사용자 정보 저장
  - 트랜잭션 처리
  - Multi-AZ 구성으로 고가용성 확보

- **Amazon ElastiCache (Redis)**
  - 세션 관리
  - 이메일 인증 토큰 저장
  - 캐시 레이어

### 2.3 메시징 & 이벤트
- **Amazon SQS**
  - 이메일 발송 큐
  - 비동기 작업 처리

- **Amazon SNS**
  - 이벤트 알림
  - 시스템 모니터링 알림

### 2.4 스토리지
- **Amazon S3**
  - 정적 파일 저장
  - 로그 저장
  - 백업 저장

### 2.5 보안
- **AWS WAF**
  - 웹 애플리케이션 보안
  - DDoS 방어

- **AWS KMS**
  - 암호화 키 관리
  - 민감 정보 보호

### 2.6 모니터링 & 로깅
- **Amazon CloudWatch**
  - 시스템 모니터링
  - 로그 수집
  - 알람 설정

- **AWS X-Ray**
  - 분산 추적
  - 성능 모니터링

## 3. 네트워크 구성

### 3.1 VPC 구성
- **퍼블릭 서브넷**
  - ALB
  - NAT Gateway
  - Bastion Host

- **프라이빗 서브넷**
  - ECS Tasks
  - RDS
  - ElastiCache

### 3.2 보안 그룹
- **ALB 보안 그룹**: 80/443 포트 인바운드
- **ECS 보안 그룹**: ALB로부터의 트래픽만 허용
- **RDS 보안 그룹**: ECS로부터의 데이터베이스 포트만 허용
- **ElastiCache 보안 그룹**: ECS로부터의 Redis 포트만 허용

## 4. 확장성 & 가용성

### 4.1 확장성
- ECS Auto Scaling을 통한 수평적 확장
- RDS Read Replica를 통한 읽기 성능 확장
- ElastiCache 클러스터 확장

### 4.2 가용성
- 다중 가용영역(Multi-AZ) 구성
- RDS Multi-AZ 배포
- ElastiCache 복제 그룹
- ALB를 통한 로드 밸런싱

## 5. 배포 전략

### 5.1 CI/CD 파이프라인
- **AWS CodePipeline**
  - GitHub 소스 연동
  - 자동 빌드 및 테스트
  - Blue/Green 배포

### 5.2 컨테이너 관리
- **Amazon ECR**
  - 도커 이미지 저장
  - 버전 관리

## 6. 비용 최적화
- Auto Scaling을 통한 리소스 최적화
- S3 수명 주기 정책 적용
- Reserved Instance 활용
- 개발/스테이징 환경의 자동 중지/시작

## 7. 장애 복구 전략
- 다중 가용영역 구성
- 자동 백업 및 복구
- 장애 탐지 및 알림
- Failover 자동화
