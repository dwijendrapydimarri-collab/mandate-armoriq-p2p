import React from 'react';
import { Decision } from '../types';

interface AuthorityCliffReplayProps {
  decision: Decision | null;
}

export const AuthorityCliffReplay: React.FC<AuthorityCliffReplayProps> = ({ decision }) => {
  if (!decision) return null;

  const isBlocked = decision.verdict === 'BLOCK';
  const isAllowed = decision.verdict === 'ALLOW';
  const isHeld = decision.verdict === 'HOLD';

  return (
    <div className="bg-slate-900/90 border border-slate-700/80 rounded-xl p-5 space-y-4 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <span>⚡</span> Authority Cliff Execution Path
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Realtime trace from Agent Proposal → Gateway → ArmorIQ Boundary → MCP Rail → Ledger
          </p>
        </div>

        {isBlocked ? (
          <span className="px-2.5 py-1 text-xs font-mono font-black bg-red-950/80 text-red-400 border border-red-500/50 rounded">
            AUTHORIZED BY: NOBODY
          </span>
        ) : isHeld ? (
          <span className="px-2.5 py-1 text-xs font-mono font-bold bg-amber-950/80 text-amber-300 border border-amber-500/50 rounded">
            PARKED FOR CFO RESUME
          </span>
        ) : (
          <span className="px-2.5 py-1 text-xs font-mono font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-500/50 rounded">
            AUTHORIZED & DISBURSED
          </span>
        )}
      </div>

      {/* 5-Step Pipeline Flow */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-2.5 text-xs font-mono">
        {/* Step 1: Agent Proposal */}
        <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1">
          <span className="text-slate-500 text-[10px] block">1. AGENT PROPOSAL</span>
          <span className="text-blue-300 font-bold block">{decision.agent_id}</span>
          <span className="text-[11px] text-slate-400 block truncate">Tool: {decision.tool}</span>
        </div>

        {/* Step 2: Gateway */}
        <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1">
          <span className="text-slate-500 text-[10px] block">2. SOLE GATEWAY</span>
          <span className="text-slate-200 font-bold block">gateway.py</span>
          <span className="text-[11px] text-slate-400 block">Single point of dispatch</span>
        </div>

        {/* Step 3: ArmorIQ Boundary (The Cliff) */}
        <div
          className={`p-3 rounded-lg border space-y-1 ${
            isBlocked
              ? 'bg-red-950/40 border-red-500 shadow-lg shadow-red-500/10'
              : isHeld
              ? 'bg-amber-950/40 border-amber-500'
              : 'bg-emerald-950/40 border-emerald-500'
          }`}
        >
          <span className="text-slate-400 text-[10px] font-bold block">3. ARMORIQ BOUNDARY</span>
          <span
            className={`font-black text-sm block ${
              isBlocked ? 'text-red-400' : isHeld ? 'text-amber-400' : 'text-emerald-400'
            }`}
          >
            {decision.verdict}
          </span>
          <span className="text-[10px] text-slate-300 block truncate">{decision.reason}</span>
        </div>

        {/* Step 4: MCP Tool */}
        <div
          className={`p-3 rounded-lg border space-y-1 ${
            isBlocked
              ? 'bg-slate-950/40 border-slate-800/40 opacity-40'
              : isHeld
              ? 'bg-slate-950/60 border-slate-800 opacity-60'
              : 'bg-slate-950 border-emerald-500/40'
          }`}
        >
          <span className="text-slate-500 text-[10px] block">4. MCP TOOL RAIL</span>
          <span className="text-slate-200 font-bold block">{decision.tool}</span>
          <span className="text-[10px] text-slate-400 block">
            {isBlocked ? '✕ NOT ENTERED' : isHeld ? '⏸️ HELD' : '✓ EXECUTED'}
          </span>
        </div>

        {/* Step 5: Ledger Mutation */}
        <div
          className={`p-3 rounded-lg border space-y-1 ${
            isBlocked
              ? 'bg-slate-950/40 border-slate-800/40 opacity-40'
              : isHeld
              ? 'bg-slate-950/60 border-slate-800 opacity-60'
              : 'bg-slate-950 border-emerald-500/40'
          }`}
        >
          <span className="text-slate-500 text-[10px] block">5. SANDBOX LEDGER</span>
          <span className="text-slate-200 font-bold block">ACC-MANDATE-01</span>
          <span className="text-[10px] text-slate-400 block">
            {isBlocked ? '0.00 DEBIT (UNCHANGED)' : isHeld ? 'PENDING APPROVAL' : 'DEBIT POSTED'}
          </span>
        </div>
      </div>
    </div>
  );
};
