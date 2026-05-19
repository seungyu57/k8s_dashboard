import { useState } from 'react';
import { Header } from './components/layout/Header';
import { PageKey, Sidebar } from './components/layout/Sidebar';
import { EventPage } from './pages/EventPage';
import { GpuDashboardPage } from './pages/GpuDashboardPage';
import { NodeDetailPage } from './pages/NodeDetailPage';
import { NodeListPage } from './pages/NodeListPage';
import { OverviewPage } from './pages/OverviewPage';
import { PodDetailPage } from './pages/PodDetailPage';
import { PodListPage } from './pages/PodListPage';
import { PodLogPage } from './pages/PodLogPage';

export default function App() {
  const [page, setPage] = useState<PageKey>('overview');
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [selectedPod, setSelectedPod] = useState<{ namespace: string; name: string; container?: string } | null>(null);

  const content = (() => {
    switch (page) {
      case 'nodes':
        return <NodeListPage onSelectNode={(name) => { setSelectedNode(name); setPage('nodeDetail'); }} />;
      case 'nodeDetail':
        return <NodeDetailPage nodeName={selectedNode} onBack={() => setPage('nodes')} />;
      case 'pods':
        return <PodListPage onSelectPod={(namespace, name) => { setSelectedPod({ namespace, name }); setPage('podDetail'); }} />;
      case 'podDetail':
        return (
          <PodDetailPage
            namespace={selectedPod?.namespace ?? null}
            podName={selectedPod?.name ?? null}
            onBack={() => setPage('pods')}
            onLogs={(namespace, name, container) => { setSelectedPod({ namespace, name, container }); setPage('logs'); }}
          />
        );
      case 'events':
        return <EventPage />;
      case 'logs':
        return (
          <PodLogPage
            namespace={selectedPod?.namespace ?? null}
            podName={selectedPod?.name ?? null}
            container={selectedPod?.container ?? null}
            onBack={() => setPage('podDetail')}
          />
        );
      case 'gpu':
        return <GpuDashboardPage />;
      case 'overview':
      default:
        return <OverviewPage />;
    }
  })();

  return (
    <div className="flex min-h-screen">
      <Sidebar current={page} onNavigate={setPage} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-auto p-6">{content}</main>
      </div>
    </div>
  );
}
