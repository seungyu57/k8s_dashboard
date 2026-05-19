type Props = { value: string };

export function StatusBadge({ value }: Props) {
  const color = value.toLowerCase().includes('ready') || value.toLowerCase().includes('running')
    ? 'bg-emerald-500/15 text-emerald-300 ring-emerald-400/30'
    : value.toLowerCase().includes('warning') || value.toLowerCase().includes('pending')
      ? 'bg-amber-500/15 text-amber-300 ring-amber-400/30'
      : 'bg-rose-500/15 text-rose-300 ring-rose-400/30';
  return <span className={`rounded-full px-2 py-1 text-xs font-medium ring-1 ${color}`}>{value}</span>;
}
