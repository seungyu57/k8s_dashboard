import { useEffect, useState } from 'react';
import { getPod } from '../api/pods';
import { listPodEvents } from '../api/events';
import { AsyncState } from '../components/status/AsyncState';
import { StatusBadge } from '../components/status/StatusBadge';
import { SimpleTable } from '../components/table/SimpleTable';
import type { EventSummary } from '../types/event';
import type { PodSummary } from '../types/pod';

type Props = {
  namespace: string | null;
  podName: string | null;
  onBack: () => void;
  onLogs: (namespace: string, podName: string, container?: string) => void;
};

export function PodDetailPage({ namespace, podName, onBack, onLogs }: Props) {
  const [pod, setPod] = useState<PodSummary | null>(null);
  const [events, setEvents] = useState<EventSummary[]>([]);
  const [loading, setLoading] = useState(Boolean(namespace && podName));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!namespace || !podName) return;
    setLoading(true);
    Promise.all([getPod(namespace, podName), listPodEvents(namespace, podName)])
      .then(([podData, eventData]) => {
        setPod(podData);
        setEvents(eventData);
      })
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
      .finally(() => setLoading(false));
  }, [namespace, podName]);

  if (!namespace || !podName) {
    return <AsyncState empty emptyText="Pod 목록에서 상세 조회할 Pod를 선택하세요." />;
  }

  return (
    <section className="space-y-4">
      <button className="text-sm text-sky-300 hover:text-sky-200" onClick={onBack}>← Pod 목록</button>
      <h2 className="text-2xl font-semibold">Pod 상세: {namespace}/{podName}</h2>
      <AsyncState loading={loading} error={error} empty={!loading && !error && !pod} />
      {pod && (
        <div className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
              <div className="mb-3"><StatusBadge value={pod.phase} /></div>
              <p>Node: {pod.nodeName ?? '-'}</p>
              <p>Pod IP: {pod.podIP ?? '-'}</p>
              <p>Host IP: {pod.hostIP ?? '-'}</p>
              <p>Restarts: {pod.restartCount}</p>
              {pod.waitingReason && <p>Waiting: {pod.waitingReason}</p>}
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
              <h3 className="mb-2 font-semibold">Resources</h3>
              <p>Requests: {formatResources(pod.resourceRequests)}</p>
              <p>Limits: {formatResources(pod.resourceLimits)}</p>
              <p>GPU: request={pod.gpuRequests}, limit={pod.gpuLimits}</p>
            </div>
          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
            <h3 className="mb-3 font-semibold">Containers</h3>
            <SimpleTable rows={pod.containers} columns={[
              { key: 'name', label: 'Name' },
              { key: 'ready', label: 'Ready', render: (row) => String(row.ready) },
              { key: 'state', label: 'State', render: (row) => row.state ?? '-' },
              { key: 'reason', label: 'Reason', render: (row) => row.reason ?? '-' },
              { key: 'gpuRequests', label: 'GPU Req', render: (row) => row.gpuRequests },
              { key: 'logs', label: 'Logs', render: (row) => <button className="text-sky-300 hover:text-sky-200" onClick={(event) => { event.stopPropagation(); onLogs(namespace, podName, row.name); }}>로그 보기</button> },
            ]} />
          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
            <h3 className="mb-3 font-semibold">Pod Events</h3>
            <AsyncState empty={events.length === 0} emptyText="관련 Event가 없습니다." />
            {events.length > 0 && <SimpleTable rows={events} columns={[
              { key: 'type', label: 'Type', render: (row) => <StatusBadge value={row.type ?? '-'} /> },
              { key: 'reason', label: 'Reason', render: (row) => row.reason ?? '-' },
              { key: 'message', label: 'Message', render: (row) => row.message ?? '-' },
              { key: 'lastTimestamp', label: 'Last Seen', render: (row) => row.lastTimestamp ?? '-' },
            ]} />}
          </div>
        </div>
      )}
    </section>
  );
}

function formatResources(resources: Record<string, string>) {
  const entries = Object.entries(resources);
  return entries.length ? entries.map(([key, value]) => `${key}=${value}`).join(', ') : '-';
}
