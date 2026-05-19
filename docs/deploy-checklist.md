# Kubernetes 배포 체크리스트

## 1. 이미지 빌드

Repository root에서 실행합니다.

```bash
docker build -f backend/Dockerfile -t ghcr.io/seungyu57/k8s-dashboard-backend:latest .
docker build -f frontend/Dockerfile -t ghcr.io/seungyu57/k8s-dashboard-frontend:latest .
```

필요하면 tag를 버전으로 바꿉니다.

```bash
docker tag ghcr.io/seungyu57/k8s-dashboard-backend:latest ghcr.io/seungyu57/k8s-dashboard-backend:v0.1.0
docker tag ghcr.io/seungyu57/k8s-dashboard-frontend:latest ghcr.io/seungyu57/k8s-dashboard-frontend:v0.1.0
```

## 2. 이미지 푸시

```bash
docker push ghcr.io/seungyu57/k8s-dashboard-backend:latest
docker push ghcr.io/seungyu57/k8s-dashboard-frontend:latest
```

사내 registry를 쓴다면 `deploy/k8s/*-deployment.yaml`의 `image:` 값을 해당 registry 주소로 변경합니다.

## 3. 배포 전 YAML 확인

```bash
kubectl apply --dry-run=client -f deploy/k8s/namespace.yaml
kubectl apply --dry-run=client -f deploy/k8s/serviceaccount.yaml
kubectl apply --dry-run=client -f deploy/k8s/rbac-readonly.yaml
kubectl apply --dry-run=client -f deploy/k8s/service.yaml
kubectl apply --dry-run=client -f deploy/k8s/backend-deployment.yaml
kubectl apply --dry-run=client -f deploy/k8s/frontend-deployment.yaml
kubectl apply --dry-run=client -f deploy/k8s/ingress.yaml
```

## 4. kubectl apply 순서

```bash
kubectl apply -f deploy/k8s/namespace.yaml
kubectl apply -f deploy/k8s/serviceaccount.yaml
kubectl apply -f deploy/k8s/rbac-readonly.yaml
kubectl apply -f deploy/k8s/service.yaml
kubectl apply -f deploy/k8s/backend-deployment.yaml
kubectl apply -f deploy/k8s/frontend-deployment.yaml
kubectl apply -f deploy/k8s/ingress.yaml
```

## 5. 배포 상태 확인

```bash
kubectl -n k8s-readonly-dashboard get deploy,po,svc,ingress
kubectl -n k8s-readonly-dashboard rollout status deploy/k8s-dashboard-backend
kubectl -n k8s-readonly-dashboard rollout status deploy/k8s-dashboard-frontend
```

## 6. Backend health check

클러스터 내부 Service를 port-forward해서 확인합니다.

```bash
kubectl -n k8s-readonly-dashboard port-forward svc/k8s-dashboard-backend 8000:8000
curl http://localhost:8000/health
curl http://localhost:8000/api/clusters/local/overview
```

`overview`가 Node/Pod 수를 반환하면 backend Pod가 InClusterConfig와 ServiceAccount RBAC로 Kubernetes API를 조회하는 것입니다.

## 7. Frontend 확인

```bash
kubectl -n k8s-readonly-dashboard port-forward svc/k8s-dashboard-frontend 8080:80
```

브라우저에서 접속합니다.

```text
http://localhost:8080
```

Ingress가 준비되어 있으면 `deploy/k8s/ingress.yaml`의 host로 접속합니다.

```text
http://k8s-dashboard.internal.example.com
```

## 8. Pod logs 확인

```bash
kubectl -n k8s-readonly-dashboard logs deploy/k8s-dashboard-backend
kubectl -n k8s-readonly-dashboard logs deploy/k8s-dashboard-frontend
```

Backend에서 RBAC 오류가 나면 `deploy/k8s/rbac-readonly.yaml`을 확인합니다. Secret 권한이나 write/delete/patch/update 권한은 추가하지 않습니다.

## 9. Rollback

직전 ReplicaSet으로 되돌립니다.

```bash
kubectl -n k8s-readonly-dashboard rollout undo deploy/k8s-dashboard-backend
kubectl -n k8s-readonly-dashboard rollout undo deploy/k8s-dashboard-frontend
```

특정 revision으로 되돌리려면 다음을 사용합니다.

```bash
kubectl -n k8s-readonly-dashboard rollout history deploy/k8s-dashboard-backend
kubectl -n k8s-readonly-dashboard rollout undo deploy/k8s-dashboard-backend --to-revision=<REVISION>
```

## 10. 삭제

```bash
kubectl delete -f deploy/k8s/ingress.yaml
kubectl delete -f deploy/k8s/frontend-deployment.yaml
kubectl delete -f deploy/k8s/backend-deployment.yaml
kubectl delete -f deploy/k8s/service.yaml
kubectl delete -f deploy/k8s/rbac-readonly.yaml
kubectl delete -f deploy/k8s/serviceaccount.yaml
kubectl delete -f deploy/k8s/namespace.yaml
```
