import { apiGet, queryString } from './client';
import type { EventSummary } from '../types/event';

export function listEvents(params: { namespace?: string; type?: string; reason?: string; involvedKind?: string; involvedName?: string } = {}) {
  return apiGet<EventSummary[]>(`/api/clusters/local/events${queryString(params)}`);
}

export function listPodEvents(namespace: string, podName: string) {
  return apiGet<EventSummary[]>(`/api/clusters/local/namespaces/${encodeURIComponent(namespace)}/pods/${encodeURIComponent(podName)}/events`);
}
