export function GpuDashboardPage() {
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-semibold">GPU Dashboard</h2>
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5"><p className="text-slate-400">GPU Nodes</p><p className="text-3xl font-bold">1</p></div>
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5"><p className="text-slate-400">Total GPU</p><p className="text-3xl font-bold">8</p></div>
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5"><p className="text-slate-400">Requested GPU</p><p className="text-3xl font-bold">1</p></div>
      </div>
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-5 text-slate-300">
        MVP는 Kubernetes `nvidia.com/gpu` request/limit 기준입니다. DCGM/Prometheus 실사용률은 다음 단계 이후 확장합니다.
      </div>
    </section>
  );
}
