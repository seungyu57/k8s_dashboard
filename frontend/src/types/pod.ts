export type ContainerResource = {
  name: string;
  requests: Record<string, string>;
  limits: Record<string, string>;
  gpuRequests: number;
  gpuLimits: number;
  restartCount: number;
  ready: boolean;
  state?: string | null;
  reason?: string | null;
};

export type PodSummary = {
  namespace: string;
  name: string;
  phase: string;
  nodeName?: string | null;
  podIP?: string | null;
  hostIP?: string | null;
  restartCount: number;
  createdAt?: string | null;
  labels: Record<string, string>;
  containers: ContainerResource[];
  waitingReason?: string | null;
  resourceRequests: Record<string, string>;
  resourceLimits: Record<string, string>;
  gpuRequests: number;
  gpuLimits: number;
  annotations?: Record<string, string>;
  conditions?: Record<string, unknown>[];
  events?: Record<string, unknown>[];
};

export type PodLogResponse = {
  namespace: string;
  pod: string;
  container?: string | null;
  tailLines: number;
  logs: string;
  truncated: boolean;
};
