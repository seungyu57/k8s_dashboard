export type ClusterOverview = {
  cluster_id: string;
  nodes: { total: number; running: number; pending: number; failed: number; succeeded: number; unknown: number };
  namespaces: number;
  pods: { total: number; running: number; pending: number; failed: number; succeeded: number; unknown: number };
  deployments: number;
  services: number;
  warning_events: number;
  gpu: { gpu_nodes: number; total_gpu: number; requested_gpu: number; gpu_pods: number };
};
