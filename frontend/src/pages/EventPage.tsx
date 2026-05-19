import { useEffect, useState } from 'react';
import { listEvents } from '../api/events';
import { AsyncState } from '../components/status/AsyncState';
import { StatusBadge } from '../components/status/StatusBadge';
import { SimpleTable } from '../components/table/SimpleTable';
import type { EventSummary } from '../types/event';

export function EventPage() {
  const [events, setEvents] = useState<EventSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [warningOnly, setWarningOnly] = useState(false);

  useEffect(() => {
    setLoading(true);
    listEvents({ type: warningOnly ? 'Warning' : undefined })
      .then(setEvents)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
      .finally(() => setLoading(false));
  }, [warningOnly]);

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-2xl font-semibold">Events</h2>
        <label className="flex items-center gap-2 text-sm text-slate-300">
          <input type="checkbox" checked={warningOnly} onChange={(event) => setWarningOnly(event.target.checked)} />
          Warning만 보기
        </label>
      </div>
      <AsyncState loading={loading} error={error} empty={!loading && !error && events.length === 0} />
      {!loading && !error && events.length > 0 && (
        <SimpleTable rows={events} columns={[
          { key: 'namespace', label: 'Namespace', render: (row) => row.namespace ?? '-' },
          { key: 'type', label: 'Type', render: (row) => <StatusBadge value={row.type ?? '-'} /> },
          { key: 'reason', label: 'Reason', render: (row) => row.reason ?? '-' },
          { key: 'object', label: 'Object', render: (row) => `${row.involvedKind ?? '-'}/${row.involvedName ?? '-'}` },
          { key: 'message', label: 'Message', render: (row) => row.message ?? '-' },
          { key: 'lastTimestamp', label: 'Last Seen', render: (row) => row.lastTimestamp ?? '-' },
        ]} />
      )}
    </section>
  );
}
