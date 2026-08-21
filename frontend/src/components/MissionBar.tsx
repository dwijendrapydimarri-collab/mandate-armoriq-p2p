import React from 'react';
import { ShieldCheck, ShieldAlert, Lock, Unlock, Play, RefreshCw, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { Mission } from '../types';

interface MissionBarProps {
  mission: Mission | null;
  governanceMode: 'on' | 'off';
  armoriqMode: 'local' | 'real';
  isRunning: boolean;
  onRun: (governance: 'on' | 'off') => void;
  onReset: () => void;
}

export const MissionBar: React.FC<MissionBarProps> = ({
  mission,
  governanceMode,
  armoriqMode,
  isRunning,
  onRun,
  onReset,
}) => {
  const isSealed = Boolean(mission?.sealed_at);

  return (
    <header className="flex flex-col border-b border-slate-800 bg-slate-900/90 sticky top-0 z-30 shadow-md">
      {/* 1. Governance Warning Banner when OFF */}
      {governanceMode === 'off' && (
        <div className="w-full bg-rose-600 text-white font-bold py-1.5 px-4 text-center text-xs tracking-wider uppercase flex items-center justify-center gap-2 animate-pulse">
          <AlertTriangle className="w-4 h-4" />
          SANDBOX COMPARISON — GOVERNANCE DISABLED (ALL ATTACKS WILL SUCCEED)
          <AlertTriangle className="w-4 h-4" />
        </div>
      )}

      {/* 2. Adapter Mode Banner */}
      <div className="bg-slate-950/80 border-b border-slate-800/80 px-4 py-1 flex items-center justify-between text-xs text-slate-400 font-mono">
        <div className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span>
            {armoriqMode === 'local' ? (
              <span className="text-amber-400 font-semibold">ENFORCEMENT: LOCAL ADAPTER (ArmorIQ contract)</span>
            ) : (
              <span className="text-emerald-400 font-semibold">ENFORCEMENT: REAL ARMORIQ SDK PROXY</span>
            )}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span>SPEC: <strong className="text-slate-200">v1.0 SEALED</strong></span>
          <span>MONEY UNIT: <strong className="text-slate-200">INTEGER PAISE</strong></span>
        </div>
      </div>

      {/* 3. Main Mission Bar Controls & Envelope */}
      <div className="p-4 flex flex-wrap items-center justify-between gap-4">
        {/* Left: Project title & Mission Objective */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 border border-emerald-500/40 flex items-center justify-center shadow-inner">
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-slate-100 tracking-tight">MANDATE</h1>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                MISSION CONTROL
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Objective: <span className="text-slate-200 font-medium">Clear this week's vendor invoices with cryptographic bounds</span>
            </p>
          </div>
        </div>

        {/* Center: The Sealed Authority Envelope Box */}
        <div className="flex-1 max-w-2xl bg-slate-950/80 border border-slate-800 rounded-lg p-2.5 flex items-center justify-between text-xs font-mono shadow-inner">
          <div className="flex items-center gap-2 pr-3 border-r border-slate-800">
            {isSealed ? (
              <div className="flex items-center gap-1 text-emerald-400 font-semibold bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20">
                <Lock className="w-3.5 h-3.5" />
                <span>SEALED</span>
              </div>
            ) : (
              <div className="flex items-center gap-1 text-amber-400 font-semibold bg-amber-500/10 px-2 py-1 rounded border border-amber-500/20">
                <Unlock className="w-3.5 h-3.5" />
                <span>UNSEALED</span>
              </div>
            )}
          </div>

          <div className="grid grid-cols-3 gap-3 px-3 text-[11px]">
            <div>
              <span className="text-slate-500 block text-[10px]">PAYEE SCOPE</span>
              <span className="text-slate-300 font-bold">5 Master Accounts</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px]">INVOICE CEILING</span>
              <span className="text-slate-300 font-bold tabular-nums">₹50,000 / inv</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px]">PLAN HASH</span>
              <span className="text-emerald-400 font-mono truncate block max-w-[120px]" title={mission?.plan_hash || "Awaiting seal"}>
                {mission?.plan_hash ? `${mission.plan_hash.slice(0, 10)}...` : "Unsealed"}
              </span>
            </div>
          </div>

          <div className="pl-3 border-l border-slate-800 text-[10px] text-right">
            <span className="text-slate-500 block">SEALED AT</span>
            <span className="text-slate-300 tabular-nums">
              {mission?.sealed_at ? new Date(mission.sealed_at).toLocaleTimeString() : "--:--:--"}
            </span>
          </div>
        </div>

        {/* Right: Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => onRun('on')}
            disabled={isRunning}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-900/30 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Governed Run (ON)</span>
          </button>

          <button
            onClick={() => onRun('off')}
            disabled={isRunning}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold bg-rose-700 hover:bg-rose-600 text-white shadow-lg shadow-rose-950/40 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ShieldAlert className="w-4 h-4" />
            <span>Ungoverned (OFF)</span>
          </button>

          <button
            onClick={onReset}
            disabled={isRunning}
            title="Restore seed database snapshot in <1s"
            className="flex items-center gap-1 px-3 py-2 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRunning ? 'animate-spin' : ''}`} />
            <span>Reset DB</span>
          </button>
        </div>
      </div>
    </header>
  );
};
