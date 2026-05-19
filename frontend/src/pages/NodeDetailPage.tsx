import { useEffect, useState } from 'react';
import { getNode } from '../api/nodes';
import { AsyncState } from '../components/status/AsyncState';
import { StatusBadge } from '../components/status/StatusBadge';
import type { NodeSummary } from '../types/node';

type Props = { nodeName: string | null; onBack: () => void };

export function NodeDetailPage({ nodeName, onBack }: Props) {
  const [node, setNode] = useState<NodeSummary | null>(null);
  const [loading, setLoading] = useState(Boolean(nodeName));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!nodeName) return;
    setLoading(true);
    getNode(nodeName)
      .then(setNode)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
      .finally(() => setLoading(false));
  }, [nodeName]);

  if (!nodeName) {
    return <AsyncState empty emptyText="Node 목록에서 상세 조회할 Node를 선택하세요." />;
  }

  return (
    <section className="space-y-4">
      <button className="text-sm text-sky-300 hover:text-sky-200" onClick={onBack}>← Node 목록</button>
      <h2 className="text-2xl font-semibold">Node 상세: {nodeName}</h2>
      <AsyncState loading={loading} error={error} empty={!loading && !error && !node} />
      {node && (
        <div className="space-y-4">
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
            <div className="mb-3"><StatusBadge value={node.status} /></div>
            <dl className="grid gap-3 md:grid-cols-2">
              <div><dt className="text-slate-500">Roles</dt><dd>{node.roles.join(', ')}</dd></div>
              <div><dt className="text-slate-500">Runtime</dt><dd>{node.containerRuntimeVersion ?? '-'}</dd></div>
              <div><dt className="text-slate-500">Kubelet</dt><dd>{node.kubeletVersion ?? '-'}</dd></div>
              <div><dt className="text-slate-500">OS</dt><dd>{node.osImage ?? '-'}</dd></div>
              <div><dt className="text-slate-500">Capacity</dt><dd>cpu={node.capacity.cpu ?? '-'}, memory={node.capacity.memory ?? '-'}, gpu={node.capacity.gpu}</dd></div>
              <div><dt className="text-slate-500">Allocatable</dt><dd>cpu={node.allocatable.cpu ?? '-'}, memory={node.allocatable.memory ?? '-'}, gpu={node.allocatable.gpu}</dd></div>
            </dl>
          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
            <h3 className="mb-3 font-semibold">Conditions</h3>
            <div className="space-y-2">
              {node.conditions.map((condition) => (
                <div key={condition.type} className="flex flex-wrap items-center gap-3 text-sm">
                  <StatusBadge value={`${condition.type}=${condition.status}`} />
                  <span className="text-slate-400">{condition.reason ?? ''}</span>
                  <span className="text-slate-500">{condition.message ?? ''}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
