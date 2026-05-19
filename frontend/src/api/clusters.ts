import { apiGet } from './client';
import type { ClusterOverview } from '../types/cluster';

export function getLocalOverview() {
  return apiGet<ClusterOverview>('/api/clusters/local/overview');
}
