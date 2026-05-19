import { useEffect, useState } from 'react';
import { listNodes } from '../api/nodes';
import { AsyncState } from '../components/status/AsyncState';
import { StatusBadge } from '../components/status/StatusBadge';
import { SimpleTable } from '../components/table/SimpleTable';
import type { NodeSummary } from '../types/node';

type Props = { onSelectNode: (name: string) => void };

export function NodeListPage({ onSelectNode }: Props) {
  const [nodes, setNodes] = useState<NodeSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    listNodes()
      .then(setNodes)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-semibold">Node 목록</h2>
      <AsyncState loading={loading} error={error} empty={!loading && !error && nodes.length === 0} />
      {!loading && !error && nodes.length > 0 && (
        <SimpleTable rows={nodes} onRowClick={(node) => onSelectNode(node.name)} columns={[
          { key: 'name', label: 'Name' },
          { key: 'status', label: 'Status', render: (row) => <StatusBadge value={row.status} /> },
          { key: 'roles', label: 'Roles', render: (row) => row.roles.join(', ') },
          { key: 'cpu', label: 'CPU', render: (row) => row.allocatable.cpu ?? '-' },
          { key: 'memory', label: 'Memory', render: (row) => row.allocatable.memory ?? '-' },
          { key: 'gpu', label: 'GPU', render: (row) => row.allocatable.gpu },
        ]} />
      )}
    </section>
  );
}
