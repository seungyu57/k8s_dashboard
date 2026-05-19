from fastapi import HTTPException

from app.core.config import get_settings
from app.schemas.log import PodLogResponse
from app.services.kubernetes_client import KubernetesClientError, KubernetesClientFactory


class LogService:
    """ReadOnly Pod log service backed by read_namespaced_pod_log."""

    def __init__(self, client_factory=None, core_v1=None):
        self.client_factory = client_factory or KubernetesClientFactory()
        self._core_v1 = core_v1

    def _core(self):
        if self._core_v1 is not None:
            return self._core_v1
        return self.client_factory.create().core_v1

    def get_pod_logs(self, cluster_id, namespace, pod_name, container, tail_lines):
        settings = get_settings()
        safe_tail = self._safe_tail_lines(tail_lines, settings.log_tail_lines_default, settings.log_tail_lines_max)
        try:
            logs = self._core().read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                container=container,
                tail_lines=safe_tail,
                timestamps=True,
            )
            return PodLogResponse(
                namespace=namespace,
                pod=pod_name,
                container=container,
                tail_lines=safe_tail,
                logs=logs or "",
                truncated=False,
            )
        except KubernetesClientError as exc:
            raise HTTPException(status_code=503, detail=str(exc))
        except Exception as exc:
            raise self._http_error(exc, "failed to read Kubernetes pod logs '{0}/{1}'".format(namespace, pod_name))

    def _safe_tail_lines(self, tail_lines, default, maximum):
        try:
            parsed = int(tail_lines) if tail_lines is not None else int(default)
        except (TypeError, ValueError):
            parsed = int(default)
        if parsed < 1:
            parsed = int(default)
        return min(parsed, int(maximum))

    def _http_error(self, exc, message):
        status = getattr(exc, "status", None)
        reason = getattr(exc, "reason", None) or str(exc)
        if status == 404:
            return HTTPException(status_code=404, detail="{0}: pod or container not found".format(message))
        if status in (401, 403):
            return HTTPException(status_code=403, detail="{0}: Kubernetes RBAC denied access to pods/log".format(message))
        if status == 400:
            return HTTPException(status_code=400, detail="{0}: container must be specified for multi-container pods".format(message))
        return HTTPException(status_code=502, detail="{0}: {1}".format(message, reason))
