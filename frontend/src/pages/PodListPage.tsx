import { useEffect, useState } from 'react';
import { listPods } from '../api/pods';
import { AsyncState } from '../components/status/AsyncState';
import { StatusBadge } from '../components/status/StatusBadge';
import { SimpleTable } from '../components/table/SimpleTable';
import type { PodSummary } from '../types/pod';

type Props = { onSelectPod: (namespace: string, name: string) => void };

export function PodListPage({ onSelectPod }: Props) {
  const [pods, setPods] = useState<PodSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [gpuOnly, setGpuOnly] = useState(false);

  useEffect(() => {
    setLoading(true);
    listPods({ gpuOnly })
      .then(setPods)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
      .finally(() => setLoading(false));
  }, [gpuOnly]);

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-2xl font-semibold">Pod 목록</h2>
        <label className="flex items-center gap-2 text-sm text-slate-300">
          <input type="checkbox" checked={gpuOnly} onChange={(event) => setGpuOnly(event.target.checked)} />
          GPU Pod만 보기
        </label>
      </div>
      <AsyncState loading={loading} error={error} empty={!loading && !error && pods.length === 0} />
      {!loading && !error && pods.length > 0 && (
        <SimpleTable rows={pods} onRowClick={(pod) => onSelectPod(pod.namespace, pod.name)} columns={[
          { key: 'namespace', label: 'Namespace' },
          { key: 'name', label: 'Name' },
          { key: 'phase', label: 'Phase', render: (row) => <StatusBadge value={row.phase} /> },
          { key: 'nodeName', label: 'Node', render: (row) => row.nodeName ?? '-' },
          { key: 'podIP', label: 'Pod IP', render: (row) => row.podIP ?? '-' },
          { key: 'gpuRequests', label: 'GPU Req', render: (row) => row.gpuRequests },
          { key: 'restartCount', label: 'Restarts', render: (row) => row.restartCount },
        ]} />
      )}
    </section>
  );
}
