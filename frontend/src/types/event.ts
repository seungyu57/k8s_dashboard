export type EventSummary = {
  namespace?: string | null;
  type?: string | null;
  reason?: string | null;
  message?: string | null;
  involvedKind?: string | null;
  involvedName?: string | null;
  count?: number | null;
  firstTimestamp?: string | null;
  lastTimestamp?: string | null;
};
