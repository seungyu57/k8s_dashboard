# Kubernetes ReadOnly Dashboard

Kubernetes 클러스터의 Overview, Node, Pod, Event, Log, GPU request/limit 상태를 웹에서 확인하는 사내 ReadOnly 관제 Dashboard MVP입니다.

## 1차 MVP 범위

- Cluster Overview
- Node 목록/상세
- Pod 목록/상세
- Pod Event 조회
- Pod Log 조회
- `nvidia.com/gpu` request/limit 표시

이번 단계는 **실행 가능한 프로젝트 기본 뼈대**를 만드는 단계이며, 대부분의 화면과 API는 mock 데이터를 사용합니다.

## 제외 기능

- 로그인/인증
- 데이터베이스
- Pod 삭제/수정
- Deployment scale 변경
- YAML 편집
- Secret 값 조회
- 실시간 터미널 접속

## Backend 로컬 실행

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

확인:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/clusters/local/overview
```


### kubeconfig 없이 Mock 모드로 실행

현재 계정이 kubeconfig에 접근하지 못하거나 실제 클러스터 연결 전에 UI를 확인하려면 mock 모드를 사용합니다.

```bash
cd backend
source .venv/bin/activate
export K8S_MOCK_MODE=true
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

확인:

```bash
curl http://localhost:8000/api/clusters/local/overview
curl http://localhost:8000/api/clusters/local/nodes
curl http://localhost:8000/api/clusters/local/pods
```

Mock 모드는 Kubernetes API에 접속하지 않고 내장 fixture 데이터를 반환합니다. 실제 클러스터를 조회하려면 `K8S_MOCK_MODE=false`로 두고 `KUBECONFIG` 또는 InClusterConfig를 사용해야 합니다.

### 로컬 kubeconfig 사용

Backend는 Kubernetes Python Client를 사용합니다. 로컬 개발 환경에서는 kubeconfig fallback을 사용합니다.

```bash
cd backend
export KUBECONFIG=$HOME/.kube/config
# 필요하면 context 지정
export K8S_CONTEXT=my-context
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 클러스터 내부 실행

Kubernetes 내부에 배포하면 `InClusterConfig`를 우선 사용합니다. 이때 Pod의 ServiceAccount에 `deploy/k8s/rbac-readonly.yaml` 수준의 ReadOnly 권한이 필요합니다.

필요 권한 요약:

- `nodes`, `namespaces`, `pods`, `services`, `events`: `get`, `list`, `watch`
- `pods/log`: `get`
- `apps/deployments`: `get`, `list`, `watch`
- `secrets`: 권한 없음

## Frontend 로컬 실행

```bash
cd frontend
npm install
npm run dev
```

기본 주소:

```text
http://localhost:5173
```

Frontend는 기본적으로 같은 origin의 `/api`를 호출합니다. 로컬 Vite 개발 서버는 `/api`와 `/health`를 `http://localhost:8000`으로 proxy합니다. 다른 Backend 주소를 직접 호출해야 할 때만 `VITE_API_BASE_URL`을 설정합니다.

## Kubernetes 배포

`deploy/k8s` 디렉터리에 Kubernetes 배포용 YAML이 있습니다. 이미지 빌드/푸시 후 `backend-deployment.yaml`, `frontend-deployment.yaml`의 `image:` 값을 실제 registry/tag로 맞춥니다. 자세한 절차는 `docs/deploy-checklist.md`를 봅니다.

### Docker image build

Repository root에서 실행합니다.

```bash
docker build -f backend/Dockerfile -t ghcr.io/seungyu57/k8s-dashboard-backend:latest .
docker build -f frontend/Dockerfile -t ghcr.io/seungyu57/k8s-dashboard-frontend:latest .
```

### Frontend API 연결 방식

배포 환경에서는 Frontend가 같은 origin의 `/api`를 호출합니다. Ingress는 `/api`와 `/health`를 backend Service로 라우팅하고, frontend nginx도 `/api`와 `/health`를 `k8s-dashboard-backend:8000`으로 proxy합니다. 이 방식을 선택한 이유는 브라우저 CORS 설정을 단순화하고, 빌드된 정적 파일에 클러스터별 API URL을 하드코딩하지 않기 위해서입니다.

## 보안 원칙

- Kubernetes 접근은 ServiceAccount + 최소 ReadOnly RBAC를 우선합니다.
- write/delete/patch/update API는 만들지 않습니다.
- Secret 값은 API와 UI에 노출하지 않습니다.
- Pod logs 조회는 MVP에서도 tail 제한을 적용합니다.
