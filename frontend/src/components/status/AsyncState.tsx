type Props = {
  loading?: boolean;
  error?: string | null;
  empty?: boolean;
  emptyText?: string;
};

export function AsyncState({ loading, error, empty, emptyText = '표시할 데이터가 없습니다.' }: Props) {
  if (loading) return <div className="rounded-xl border border-slate-800 bg-slate-900 p-5 text-slate-300">불러오는 중...</div>;
  if (error) return <div className="rounded-xl border border-rose-900 bg-rose-950/40 p-5 text-rose-200">{error}</div>;
  if (empty) return <div className="rounded-xl border border-slate-800 bg-slate-900 p-5 text-slate-400">{emptyText}</div>;
  return null;
}
