# 보안 원칙

## ReadOnly 원칙

이 Dashboard의 1차 MVP는 조회 전용입니다. Kubernetes 리소스에 대해 create, update, patch, delete 기능을 제공하지 않습니다.

## Secret 미노출

- Secret 값은 API 응답에 포함하지 않습니다.
- MVP에서는 Secret 목록/상세 기능 자체를 만들지 않습니다.
- 향후 Secret 메타데이터를 표시하더라도 name, namespace, type, createdAt 같은 메타데이터만 허용합니다.

## RBAC 최소 권한

- ServiceAccount는 cluster-admin을 사용하지 않습니다.
- 필요한 리소스에 대해 get/list/watch 중심 권한만 부여합니다.
- Pod 로그 조회를 위해 `pods/log`에는 get 권한만 부여합니다.
- secrets 리소스 권한은 부여하지 않습니다.

## 로그 조회 주의

Pod 로그에는 토큰, 비밀번호, 개인정보가 포함될 수 있습니다. MVP에서도 tailLines 제한을 적용하고, 향후 권한/감사 로그를 추가해야 합니다.
