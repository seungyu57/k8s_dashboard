import { useEffect, useMemo, useState } from 'react';
import { listPods } from '../api/pods';
import { AsyncState } from '../components/status/AsyncState';
import { StatusBadge } from '../components/status/StatusBadge';
import { SimpleTable } from '../components/table/SimpleTable';
import type { PodSummary } from '../types/pod';

type Props = { onSelectPod: (namespace: string, name: string) => void };

const PHASES = ['', 'Running', 'Pending', 'Failed', 'Succeeded', 'Unknown'];

export function PodListPage({ onSelectPod }: Props) {
  const [pods, setPods] = useState<PodSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [namespace, setNamespace] = useState('');
  const [status, setStatus] = useState('');
  const [nodeName, setNodeName] = useState('');
  const [search, setSearch] = useState('');
  const [gpuOnly, setGpuOnly] = useState(false);
  const [dataikuOnly, setDataikuOnly] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(null);
    listPods({ namespace, status, nodeName, search, gpuOnly, dataikuOnly })
      .then(setPods)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
      .finally(() => setLoading(false));
  }, [namespace, status, nodeName, search, gpuOnly, dataikuOnly]);

  const namespaceOptions = useMemo(() => unique(pods.map((pod) => pod.namespace)), [pods]);
  const nodeOptions = useMemo(() => unique(pods.map((pod) => pod.nodeName).filter(Boolean) as string[]), [pods]);

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold">Pod 목록</h2>
          <p className="text-sm text-slate-400">{pods.length}개 Pod 표시 중</p>
        </div>
        <div className="flex flex-wrap items-center gap-3 text-sm text-slate-300">
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={gpuOnly} onChange={(event) => setGpuOnly(event.target.checked)} />
            GPU Pod만
          </label>
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={dataikuOnly} onChange={(event) => setDataikuOnly(event.target.checked)} />
            Dataiku Pod만
          </label>
          <button className="rounded border border-slate-700 px-3 py-2 hover:bg-slate-800" onClick={() => setStatus('Failed')}>Failed만</button>
          <button className="rounded border border-slate-700 px-3 py-2 hover:bg-slate-800" onClick={clearFilters}>초기화</button>
        </div>
      </div>

      <div className="grid gap-3 rounded-xl border border-slate-800 bg-slate-900 p-4 md:grid-cols-2 xl:grid-cols-4">
        <label className="space-y-1 text-sm">
          <span className="text-slate-400">검색</span>
          <input className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2" placeholder="pod, project, submitter..." value={search} onChange={(event) => setSearch(event.target.value)} />
        </label>
        <label className="space-y-1 text-sm">
          <span className="text-slate-400">Namespace</span>
          <input className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2" list="namespace-options" placeholder="예: dataiku-dss" value={namespace} onChange={(event) => setNamespace(event.target.value)} />
          <datalist id="namespace-options">{namespaceOptions.map((value) => <option key={value} value={value} />)}</datalist>
        </label>
        <label className="space-y-1 text-sm">
          <span className="text-slate-400">Status</span>
          <select className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2" value={status} onChange={(event) => setStatus(event.target.value)}>
            {PHASES.map((phase) => <option key={phase || 'all'} value={phase}>{phase || 'All'}</option>)}
          </select>
        </label>
        <label className="space-y-1 text-sm">
          <span className="text-slate-400">Node</span>
          <input className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2" list="node-options" placeholder="예: h100-server" value={nodeName} onChange={(event) => setNodeName(event.target.value)} />
          <datalist id="node-options">{nodeOptions.map((value) => <option key={value} value={value} />)}</datalist>
        </label>
      </div>

      <AsyncState loading={loading} error={error} empty={!loading && !error && pods.length === 0} />
      {!loading && !error && pods.length > 0 && (
        <SimpleTable rows={pods} onRowClick={(pod) => onSelectPod(pod.namespace, pod.name)} columns={[
          { key: 'namespace', label: 'Namespace' },
          { key: 'name', label: 'Name' },
          { key: 'phase', label: 'Phase', render: (row) => <StatusBadge value={row.phase} /> },
          { key: 'nodeName', label: 'Node', render: (row) => row.nodeName ?? '-' },
          { key: 'dataikuProject', label: 'Dataiku Project', render: (row) => dataikuLabel(row, 'dataiku.com/dku-project-key') },
          { key: 'dataikuSubmitter', label: 'Submitter', render: (row) => dataikuLabel(row, 'dataiku.com/dku-exec-submitter') },
          { key: 'dataikuConf', label: 'Conf', render: (row) => dataikuLabel(row, 'dataiku.com/dku-container-conf') },
          { key: 'gpuRequests', label: 'GPU Req', render: (row) => row.gpuRequests },
          { key: 'restartCount', label: 'Restarts', render: (row) => row.restartCount },
          { key: 'waitingReason', label: 'Reason', render: (row) => row.waitingReason ?? '-' },
        ]} />
      )}
    </section>
  );

  function clearFilters() {
    setNamespace('');
    setStatus('');
    setNodeName('');
    setSearch('');
    setGpuOnly(false);
    setDataikuOnly(false);
  }
}

function unique(values: string[]) {
  return Array.from(new Set(values)).sort();
}

function dataikuLabel(pod: PodSummary, key: string) {
  return pod.labels?.[key] ?? '-';
}
