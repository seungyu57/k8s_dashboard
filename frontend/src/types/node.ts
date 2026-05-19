export type NodeCondition = {
  type: string;
  status: string;
  reason?: string | null;
  message?: string | null;
};

export type NodeSummary = {
  name: string;
  status: string;
  roles: string[];
  kubeletVersion?: string | null;
  osImage?: string | null;
  containerRuntimeVersion?: string | null;
  capacity: { cpu?: string | null; memory?: string | null; gpu: number };
  allocatable: { cpu?: string | null; memory?: string | null; gpu: number };
  conditions: NodeCondition[];
  labels?: Record<string, string>;
  annotations?: Record<string, string>;
  pods?: Record<string, unknown>[];
};
