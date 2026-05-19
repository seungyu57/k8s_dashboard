from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Kubernetes ReadOnly Dashboard"
    app_env: str = "local"
    api_prefix: str = "/api"
    cors_origins: str = "http://localhost:5173"
    kubeconfig: Optional[str] = None
    k8s_context: Optional[str] = None
    log_tail_lines_default: int = 500
    log_tail_lines_max: int = 2000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
