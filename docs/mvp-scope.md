# 1차 MVP 범위

## 포함 기능

1. Cluster Overview
2. Node 목록
3. Node 상세
4. Pod 목록
5. Pod 상세
6. Pod Event 조회
7. Pod Log 조회
8. `nvidia.com/gpu` request/limit 표시

## 이번 단계의 목표

- FastAPI backend가 실행된다.
- React + Vite frontend가 실행된다.
- 기본 Layout, Sidebar, Header가 있다.
- API와 화면은 mock 데이터 기반으로 동작한다.
- Kubernetes Client 연결 구조는 준비하되 실제 조회 구현은 다음 단계로 미룬다.

## 제외 기능

- 인증/로그인
- Database
- Secret 값 조회
- Pod 삭제/수정
- Deployment scale 변경
- YAML 직접 편집
- 실시간 터미널 접속
- 멀티 클러스터 고급 관리
- Prometheus/DCGM 실사용률 연동
- 알림 기능
