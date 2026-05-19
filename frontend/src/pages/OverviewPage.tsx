import { useEffect, useState } from 'react';
import { getLocalOverview } from '../api/clusters';
import { AsyncState } from '../components/status/AsyncState';
import type { ClusterOverview } from '../types/cluster';

export function OverviewPage() {
  const [data, setData] = useState<ClusterOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getLocalOverview()
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
      .finally(() => setLoading(false));
  }, []);

  const cards = data ? [
    ['Nodes', `${data.nodes.total} total / ${data.nodes.running} ready`],
    ['Pods', `${data.pods.total} total / ${data.pods.running} running`],
    ['Namespaces', String(data.namespaces)],
    ['Warning Events', String(data.warning_events)],
    ['GPU', `${data.gpu.total_gpu} total / ${data.gpu.requested_gpu} requested`],
  ] : [];

  return (
    <section className="space-y-6">
      <h2 className="text-2xl font-semibold">Cluster Overview</h2>
      <AsyncState loading={loading} error={error} empty={!loading && !error && !data} />
      {data && (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            {cards.map(([label, value]) => (
              <div key={label} className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                <div className="text-sm text-slate-400">{label}</div>
                <div className="mt-2 text-2xl font-bold">{value}</div>
              </div>
            ))}
          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5 text-slate-300">
            Backend API <code className="text-sky-300">/api/clusters/local/overview</code> 응답을 표시합니다.
          </div>
        </>
      )}
    </section>
  );
}
