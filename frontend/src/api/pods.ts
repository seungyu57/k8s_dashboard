import { apiGet, queryString } from './client';
import type { PodLogResponse, PodSummary } from '../types/pod';

export function listPods(params: { namespace?: string; status?: string; nodeName?: string; gpuOnly?: boolean } = {}) {
  return apiGet<PodSummary[]>(`/api/clusters/local/pods${queryString(params)}`);
}

export function getPod(namespace: string, name: string) {
  return apiGet<PodSummary>(`/api/clusters/local/namespaces/${encodeURIComponent(namespace)}/pods/${encodeURIComponent(name)}`);
}

export function getPodLogs(namespace: string, name: string, params: { container?: string; tailLines?: number } = {}) {
  return apiGet<PodLogResponse>(`/api/clusters/local/namespaces/${encodeURIComponent(namespace)}/pods/${encodeURIComponent(name)}/logs${queryString(params)}`);
}
