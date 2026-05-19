import { apiGet } from './client';
import type { NodeSummary } from '../types/node';

export function listNodes() {
  return apiGet<NodeSummary[]>('/api/clusters/local/nodes');
}

export function getNode(name: string) {
  return apiGet<NodeSummary>(`/api/clusters/local/nodes/${encodeURIComponent(name)}`);
}
