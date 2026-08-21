import React from 'react';
import { Counterfactual } from '../types';

interface CounterfactualProofProps {
  counterfactual: Counterfactual;
}

export const CounterfactualProof: React.FC<CounterfactualProofProps> = ({ counterfactual }) => {
  const lossRupees = (counterfactual.prevented_loss_paise / 100).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return (
    <div className="bg-slate-950/90 border-2 border-red-500/30 rounded-xl p-4 space-y-3 relative overflow-hidden shadow-lg">
      {/* Background watermark */}
      <div className="absolute right-2 top-2 text-[60px] font-black text-red-500/5 select-none pointer-events-none">
        BLOCKED
      </div>

      {/* Header Badge */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="px-2.5 py-1 text-xs font-mono font-black tracking-wider bg-red-950/80 text-red-400 border border-red-500/50 rounded flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-red-400 animate-ping"></span>
            COUNTERFACTUAL — NOT EXECUTED
          </span>
        </div>
        <span className="text-[11px] font-mono text-emerald-400 font-bold bg-emerald-950/40 border border-emerald-500/30 px-2 py-0.5 rounded">
          PREVENTED LOSS: ₹{lossRupees}
        </span>
      </div>

      {/* Detail Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs font-mono pt-1">
        <div className="bg-slate-900/90 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400 text-[11px] block">Projected Ledger Debit:</span>
          <span className="text-red-400 font-bold text-base tabular-nums mt-0.5 block">
            -₹{lossRupees}
          </span>
        </div>

        <div className="bg-slate-900/90 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400 text-[11px] block">Projected Destination:</span>
          <span className="text-slate-200 font-semibold text-xs mt-1 block truncate">
            {counterfactual.destination_account}
          </span>
        </div>

        <div className="bg-slate-900/90 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400 text-[11px] block">Actual Sandbox Balance:</span>
          <span className="text-emerald-400 font-semibold text-xs mt-1 block flex items-center gap-1">
            <span>✓</span>
            Zero Drift (Protected)
          </span>
        </div>
      </div>

      <p className="text-[11px] text-slate-400 italic">
        * ArmorIQ blocked this transaction before MCP tool entry. The tool body was never executed, and no ledger rows were written.
      </p>
    </div>
  );
};
