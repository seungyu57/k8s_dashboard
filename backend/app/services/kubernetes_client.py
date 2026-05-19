from typing import Any

from app.core.config import get_settings


class KubernetesClientError(RuntimeError):
    pass


class KubernetesClients:
    def __init__(self, core_v1: Any, apps_v1: Any):
        self.core_v1 = core_v1
        self.apps_v1 = apps_v1


class KubernetesClientFactory:
    """Create Kubernetes API clients for ReadOnly access.

    Intended behavior for the next implementation step:
    1. Try config.load_incluster_config() first when this backend runs inside Kubernetes.
    2. Fall back to config.load_kube_config(config_file=settings.kubeconfig,
       context=settings.k8s_context) for local development.
    3. Expose only read clients such as CoreV1Api and AppsV1Api.

    Important security rule:
    - Do not add write/delete/patch/update helper methods here.
    - Route/service layers must call only get/list/read_namespaced_pod_log style APIs.
    """

    def __init__(self):
        self.settings = get_settings()

    def create(self):
        try:
            from kubernetes import client, config
        except ImportError as exc:
            raise KubernetesClientError("python kubernetes package is not installed") from exc

        try:
            try:
                config.load_incluster_config()
            except config.ConfigException:
                config.load_kube_config(
                    config_file=self.settings.kubeconfig,
                    context=self.settings.k8s_context,
                )
            return KubernetesClients(core_v1=client.CoreV1Api(), apps_v1=client.AppsV1Api())
        except Exception as exc:  # pragma: no cover - concrete client setup is integration-tested later.
            raise KubernetesClientError("failed to initialize Kubernetes client: {0}".format(exc)) from exc
