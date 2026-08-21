import React, { useState, useEffect } from 'react';
import { SystemState, Decision } from './types';
import { ScenarioBar } from './components/ScenarioBar';
import { MissionBar } from './components/MissionBar';
import { AuthorityEnvelope } from './components/AuthorityEnvelope';
import { AgentGraph } from './components/AgentGraph';
import { DecisionStream } from './components/DecisionStream';
import { StatePanel } from './components/StatePanel';
import { ForensicsDrawer } from './components/ForensicsDrawer';
import { CFOSetupModal } from './components/CFOSetupModal';
import { InvoiceIntakeModal } from './components/InvoiceIntakeModal';
import { JudgeChallengeConsole } from './components/JudgeChallengeConsole';
import { TrustBoundaryMap } from './components/TrustBoundaryMap';
import { AuthorityCliffReplay } from './components/AuthorityCliffReplay';
import { SubmissionTrackerModal } from './components/SubmissionTrackerModal';

export const App: React.FC = () => {
  const [activeScenarioId, setActiveScenarioId] = useState<string>('canonical');
  const [state, setState] = useState<SystemState>({
    accounts: [],
    vendors: [],
    purchase_orders: [],
    invoices: [],
    payments: [],
    ledger: [],
    missions: [],
    delegations: [],
    decisions: [],
    ap_records: [],
  });

  const [governanceMode, setGovernanceMode] = useState<'on' | 'off'>('on');
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [selectedDecision, setSelectedDecision] = useState<Decision | null>(null);

  // Modals
  const [isCfoSetupOpen, setIsCfoSetupOpen] = useState(false);
  const [isInvoiceIntakeOpen, setIsInvoiceIntakeOpen] = useState(false);
  const [isProbeConsoleOpen, setIsProbeConsoleOpen] = useState(false);
  const [isTrackerOpen, setIsTrackerOpen] = useState(false);
  const [showEnvelopeDetail, setShowEnvelopeDetail] = useState(false);


  const fetchState = async (scenId: string = activeScenarioId) => {
    try {
      const url = scenId === 'canonical' ? '/api/state' : `/api/state?scenario_id=${scenId}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setState(data);
        // If decision was selected, refresh it
        if (selectedDecision) {
          const fresh = data.decisions.find((d: Decision) => d.id === selectedDecision.id);
          if (fresh) setSelectedDecision(fresh);
        }
      }
    } catch (e) {
      console.error('Failed to fetch state:', e);
    }
  };

  useEffect(() => {
    fetchState(activeScenarioId);

    // Setup SSE Stream
    const sseUrl = activeScenarioId === 'canonical' ? '/api/stream' : `/api/stream?scenario_id=${activeScenarioId}`;
    const eventSource = new EventSource(sseUrl);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setState(data);
      } catch (e) {
        console.error('SSE JSON parse error:', e);
      }
    };

    return () => {
      eventSource.close();
    };
  }, [activeScenarioId]);

  const handleRun = async (mode: 'on' | 'off') => {
    setGovernanceMode(mode);
    setIsRunning(true);
    try {
      if (activeScenarioId === 'canonical') {
        const res = await fetch(`/api/run?governance=${mode}&auto_approve=true`, {
          method: 'POST',
        });
        if (res.ok) await fetchState('canonical');
      } else {
        const res = await fetch('/api/scenario/run', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            scenario_id: activeScenarioId,
            auto_approve_held: true,
          }),
        });
        if (res.ok) await fetchState(activeScenarioId);
      }
    } catch (e) {
      console.error('Failed to trigger run:', e);
    } finally {
      setIsRunning(false);
    }
  };

  const handleReset = async () => {
    setIsRunning(true);
    try {
      if (activeScenarioId === 'canonical') {
        const res = await fetch('/api/reset', { method: 'POST' });
        if (res.ok) {
          await fetchState('canonical');
          setSelectedDecision(null);
        }
      } else {
        const res = await fetch('/api/scenario/new', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            scenario_id: activeScenarioId,
            opening_balance_paise: 425000000,
          }),
        });
        if (res.ok) {
          await fetchState(activeScenarioId);
          setSelectedDecision(null);
        }
      }
    } catch (e) {
      console.error('Reset failed:', e);
    } finally {
      setIsRunning(false);
    }
  };

  const handleCreateNewScenario = async () => {
    const newId = `judge_scen_${Math.floor(1000 + Math.random() * 9000)}`;
    try {
      const res = await fetch('/api/scenario/new', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario_id: newId,
          objective: 'Custom Procurement Mission',
          opening_balance_paise: 425000000,
        }),
      });
      if (res.ok) {
        setActiveScenarioId(newId);
        setSelectedDecision(null);
        setIsCfoSetupOpen(true);
      }
    } catch (e) {
      console.error('Failed to create scenario:', e);
    }
  };

  const handleLoadCanonical = () => {
    setActiveScenarioId('canonical');
    setSelectedDecision(null);
  };

  const handleApprove = async (decisionId: string) => {
    try {
      const url =
        activeScenarioId === 'canonical'
          ? `/api/approve/${decisionId}`
          : `/api/approve/${decisionId}?scenario_id=${activeScenarioId}`;
      const res = await fetch(url, { method: 'POST' });
      if (res.ok) {
        await fetchState(activeScenarioId);
      }
    } catch (e) {
      console.error('Approve failed:', e);
    }
  };

  const handleReject = async (decisionId: string) => {
    try {
      const url =
        activeScenarioId === 'canonical'
          ? `/api/reject/${decisionId}`
          : `/api/reject/${decisionId}?scenario_id=${activeScenarioId}`;
      const res = await fetch(url, { method: 'POST' });
      if (res.ok) {
        await fetchState(activeScenarioId);
      }
    } catch (e) {
      console.error('Reject failed:', e);
    }
  };

  const latestMission = state.missions.length > 0 ? state.missions[state.missions.length - 1] : null;

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col font-sans text-slate-100">
      {/* 1. Judge Mode Scenario Bar (Top-Level Sandbox Navigation) */}
      <ScenarioBar
        scenarioId={activeScenarioId}
        metadata={state.metadata}
        isRunning={isRunning}
        onLoadCanonical={handleLoadCanonical}
        onNewScenario={handleCreateNewScenario}
        onOpenCfoSetup={() => setIsCfoSetupOpen(true)}
        onOpenInvoiceIntake={() => setIsInvoiceIntakeOpen(true)}
        onOpenProbeConsole={() => setIsProbeConsoleOpen(true)}
        onOpenTracker={() => setIsTrackerOpen(true)}
        onReset={handleReset}
      />

      {/* 2. Mission Bar */}
      <MissionBar
        mission={latestMission}
        governanceMode={governanceMode}
        armoriqMode="local"
        isRunning={isRunning}
        onRun={handleRun}
        onReset={handleReset}
      />

      {/* Toggleable Authority Envelope Visual Security Box */}
      <div className="px-4 pt-3 max-w-[1920px] w-full mx-auto">
        <div className="flex items-center justify-between mb-2">
          <button
            onClick={() => setShowEnvelopeDetail(!showEnvelopeDetail)}
            className="text-xs font-mono font-bold text-slate-400 hover:text-slate-200 flex items-center gap-1.5 transition"
          >
            <span>{showEnvelopeDetail ? '▼' : '▶'}</span>
            <span>{showEnvelopeDetail ? 'Hide' : 'Inspect'} Authority Envelope Structure & Delegations</span>
          </button>
        </div>

        {showEnvelopeDetail && (
          <div className="mb-3 animate-fadeIn">
            <AuthorityEnvelope
              mission={latestMission}
              metadata={state.metadata}
              delegations={state.delegations}
              vendors={state.vendors}
              purchaseOrders={state.purchase_orders}
              armoriqMode="local"
              onOpenCfoSetup={() => setIsCfoSetupOpen(true)}
            />
          </div>
        )}
      </div>

      {/* 3. Main Mission Control Grid */}
      <main className="flex-1 p-4 grid grid-cols-1 lg:grid-cols-12 gap-4 max-w-[1920px] w-full mx-auto">
        {/* Left/Center (8 cols): Zone 2 - Agent Graph */}
        <div className="lg:col-span-8 flex flex-col min-h-[460px] h-[520px]">
          <AgentGraph
            decisions={state.decisions}
            delegations={state.delegations}
            governanceMode={governanceMode}
            onSelectDecision={setSelectedDecision}
          />
        </div>

        {/* Right (4 cols): Zone 3 - Decision Stream */}
        <div className="lg:col-span-4 flex flex-col h-[520px]">
          <DecisionStream
            decisions={state.decisions}
            onSelectDecision={setSelectedDecision}
            onApprove={handleApprove}
            onReject={handleReject}
          />
        </div>

        {/* Selected Decision Deep Analysis Surfaces: Trust Boundary Map & Authority Cliff Replay */}
        {selectedDecision && (
          <div className="lg:col-span-12 space-y-4 animate-fadeIn">
            <TrustBoundaryMap
              decision={selectedDecision}
              invoices={state.invoices}
              purchaseOrders={state.purchase_orders}
              vendors={state.vendors}
            />
            <AuthorityCliffReplay decision={selectedDecision} />
          </div>
        )}

        {/* Bottom (12 cols): Zone 4 - State Panel & Ledger */}
        <div className="lg:col-span-12">
          <StatePanel
            accounts={state.accounts}
            invoices={state.invoices}
            purchaseOrders={state.purchase_orders}
            vendors={state.vendors}
            apRecords={state.ap_records}
            governanceMode={governanceMode}
          />
        </div>
      </main>

      {/* Forensics Drawer (Overlay) */}
      <ForensicsDrawer
        decision={selectedDecision}
        delegations={state.delegations}
        missions={state.missions}
        onClose={() => setSelectedDecision(null)}
      />

      {/* Modals */}
      <CFOSetupModal
        isOpen={isCfoSetupOpen}
        onClose={() => setIsCfoSetupOpen(false)}
        scenarioId={activeScenarioId}
        metadata={state.metadata}
        existingVendors={state.vendors}
        existingPOs={state.purchase_orders}
        onSetupSuccess={() => fetchState(activeScenarioId)}
      />

      <InvoiceIntakeModal
        isOpen={isInvoiceIntakeOpen}
        onClose={() => setIsInvoiceIntakeOpen(false)}
        scenarioId={activeScenarioId}
        vendors={state.vendors}
        purchaseOrders={state.purchase_orders}
        onIntakeSuccess={() => fetchState(activeScenarioId)}
      />

      <JudgeChallengeConsole
        isOpen={isProbeConsoleOpen}
        onClose={() => setIsProbeConsoleOpen(false)}
        scenarioId={activeScenarioId}
        vendors={state.vendors}
        purchaseOrders={state.purchase_orders}
        onProbeExecuted={() => fetchState(activeScenarioId)}
      />

      <SubmissionTrackerModal
        isOpen={isTrackerOpen}
        onClose={() => setIsTrackerOpen(false)}
      />
    </div>
  );
};

export default App;


