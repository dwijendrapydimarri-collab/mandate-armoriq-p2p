import React from 'react';
import { ScenarioMetadata } from '../types';

interface ScenarioBarProps {
  scenarioId: string;
  metadata?: ScenarioMetadata | null;
  isRunning: boolean;
  onLoadCanonical: () => void;
  onNewScenario: () => void;
  onOpenCfoSetup: () => void;
  onOpenInvoiceIntake: () => void;
  onOpenProbeConsole: () => void;
  onOpenTracker: () => void;
  onReset: () => void;
}

export const ScenarioBar: React.FC<ScenarioBarProps> = ({
  scenarioId,
  metadata,
  isRunning,
  onLoadCanonical,
  onNewScenario,
  onOpenCfoSetup,
  onOpenInvoiceIntake,
  onOpenProbeConsole,
  onOpenTracker,
  onReset,
}) => {
  const isCanonical = scenarioId === 'canonical' || !metadata;
  const status = metadata?.status || 'CANONICAL';

  const getStatusBadge = () => {
    switch (status) {
      case 'CFO_SETUP':
        return (
          <span className="px-2 py-0.5 text-xs font-semibold rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
            PHASE 1: CFO SETUP (PRE-SEAL)
          </span>
        );
      case 'SEALED':
        return (
          <span className="px-2 py-0.5 text-xs font-semibold rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
            SEALED (IMMUTABLE AUTHORITY)
          </span>
        );
      case 'READY_FOR_EXECUTION':
        return (
          <span className="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            PHASE 2: INTAKE READY
          </span>
        );
      case 'COMPLETED':
        return (
          <span className="px-2 py-0.5 text-xs font-semibold rounded bg-slate-500/20 text-slate-300 border border-slate-500/30">
            MISSION COMPLETED
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            CANONICAL DEMO FIXTURE
          </span>
        );
    }
  };

  return (
    <div className="bg-slate-900/90 border-b border-slate-800 px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 text-sm">
      {/* Left: Active Scenario & Sandbox Indicator */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <span className="text-slate-400 text-xs font-mono uppercase tracking-wider">Workspace:</span>
          <span className="font-mono font-medium text-slate-200 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700">
            {isCanonical ? 'canonical_mandate_01' : scenarioId}
          </span>
        </div>
        {getStatusBadge()}
      </div>

      {/* Center: Phase Navigation / Actions for Judge */}
      <div className="flex items-center gap-2">
        {!isCanonical && status === 'CFO_SETUP' && (
          <button
            onClick={onOpenCfoSetup}
            disabled={isRunning}
            className="px-3 py-1 bg-amber-600/30 hover:bg-amber-600/50 text-amber-200 border border-amber-500/40 rounded text-xs font-medium transition flex items-center gap-1.5"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            Edit CFO Setup & Seal
          </button>
        )}

        {!isCanonical && (status === 'SEALED' || status === 'READY_FOR_EXECUTION') && (
          <button
            onClick={onOpenInvoiceIntake}
            disabled={isRunning}
            className="px-3 py-1 bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-200 border border-indigo-500/40 rounded text-xs font-medium transition flex items-center gap-1.5"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            + Add Untrusted Invoice
          </button>
        )}

        <button
          onClick={onOpenProbeConsole}
          disabled={isRunning}
          className="px-3 py-1 bg-purple-600/30 hover:bg-purple-600/50 text-purple-200 border border-purple-500/40 rounded text-xs font-medium transition flex items-center gap-1.5 shadow-sm"
        >
          <svg className="w-3.5 h-3.5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Security Probe Console
        </button>

        <button
          onClick={onOpenTracker}
          disabled={isRunning}
          className="px-3 py-1 bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-200 border border-emerald-500/40 rounded text-xs font-semibold transition flex items-center gap-1.5 shadow-sm"
          title="Inspect live submission blockers and verification proof"
        >
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          Submission Tracker
        </button>
      </div>


      {/* Right: Sandbox Controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={onNewScenario}
          disabled={isRunning}
          className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 rounded text-xs font-medium transition flex items-center gap-1"
          title="Create a fresh isolated procurement mission workspace"
        >
          <svg className="w-3.5 h-3.5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
          </svg>
          New Judge Scenario
        </button>

        {!isCanonical && (
          <button
            onClick={onLoadCanonical}
            disabled={isRunning}
            className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-600 rounded text-xs font-medium transition"
            title="Switch back to the canonical deterministic demo fixture"
          >
            Load Canonical Demo
          </button>
        )}

        <button
          onClick={onReset}
          disabled={isRunning}
          className="px-2.5 py-1 bg-red-950/40 hover:bg-red-900/60 text-red-300 border border-red-800/40 rounded text-xs font-medium transition flex items-center gap-1"
          title="Reset this sandbox to its initial opening state"
        >
          <svg className="w-3 h-3 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Reset Sandbox
        </button>
      </div>
    </div>
  );
};
