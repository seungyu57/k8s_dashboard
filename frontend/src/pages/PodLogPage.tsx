import { useEffect, useState } from 'react';
import { getPodLogs } from '../api/pods';
import { AsyncState } from '../components/status/AsyncState';

type Props = {
  namespace: string | null;
  podName: string | null;
  container?: string | null;
  onBack: () => void;
};

export function PodLogPage({ namespace, podName, container, onBack }: Props) {
  const [logs, setLogs] = useState('');
  const [tailLines, setTailLines] = useState(500);
  const [loading, setLoading] = useState(Boolean(namespace && podName));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!namespace || !podName) return;
    setLoading(true);
    getPodLogs(namespace, podName, { container: container ?? undefined, tailLines })
      .then((data) => setLogs(data.logs))
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
      .finally(() => setLoading(false));
  }, [namespace, podName, container, tailLines]);

  if (!namespace || !podName) {
    return <AsyncState empty emptyText="Pod 상세 화면에서 로그를 조회할 Container를 선택하세요." />;
  }

  return (
    <section className="space-y-4">
      <button className="text-sm text-sky-300 hover:text-sky-200" onClick={onBack}>← Pod 상세</button>
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-2xl font-semibold">Pod Log: {namespace}/{podName}</h2>
        <select className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm" value={tailLines} onChange={(event) => setTailLines(Number(event.target.value))}>
          <option value={100}>tail 100</option>
          <option value={500}>tail 500</option>
          <option value={1000}>tail 1000</option>
          <option value={2000}>tail 2000</option>
        </select>
      </div>
      {container && <p className="text-sm text-slate-400">Container: {container}</p>}
      <AsyncState loading={loading} error={error} />
      {!loading && !error && (
        <pre className="max-h-[70vh] overflow-auto whitespace-pre-wrap rounded-xl border border-slate-800 bg-black p-4 font-mono text-sm text-emerald-200">
          {logs || '로그가 비어 있습니다.'}
        </pre>
      )}
    </section>
  );
}
