import React from 'react';
import { ShieldCheck, ShieldAlert, PauseCircle, ChevronRight, Check, X, Search } from 'lucide-react';
import { Decision } from '../types';

interface DecisionStreamProps {
  decisions: Decision[];
  onSelectDecision: (decision: Decision) => void;
  onApprove: (decisionId: string) => void;
  onReject: (decisionId: string) => void;
}

export const DecisionStream: React.FC<DecisionStreamProps> = ({
  decisions,
  onSelectDecision,
  onApprove,
  onReject,
}) => {
  // Newest first
  const sortedDecisions = [...decisions].reverse();

  return (
    <div className="flex flex-col h-full bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-inner">
      {/* Header */}
      <div className="p-3.5 border-b border-slate-800 bg-slate-900/90 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <h2 className="text-xs font-bold font-mono tracking-wider text-slate-100 uppercase">
            Live Decision Stream
          </h2>
        </div>
        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
          {decisions.length} recorded
        </span>
      </div>

      {/* Decision Cards List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2.5">
        {sortedDecisions.length === 0 ? (
          <div className="h-48 flex flex-col items-center justify-center text-slate-500 text-xs font-mono">
            <Search className="w-6 h-6 mb-2 text-slate-600 animate-bounce" />
            <span>Awaiting mission execution...</span>
          </div>
        ) : (
          sortedDecisions.map((dec) => {
            const isAllow = dec.verdict === 'ALLOW';
            const isHold = dec.verdict === 'HOLD';
            const isBlock = dec.verdict === 'BLOCK';

            const badgeBg = isAllow
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
              : isHold
              ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
              : 'bg-rose-500/10 text-rose-400 border-rose-500/30';

            const cardBorder = isAllow
              ? 'hover:border-emerald-500/50'
              : isHold
              ? 'border-amber-500/40 bg-amber-950/20'
              : 'border-rose-500/40 bg-rose-950/20';

            let parsedParams: any = {};
            try {
              parsedParams = JSON.parse(dec.params);
            } catch (e) {
              parsedParams = {};
            }

            return (
              <div
                key={dec.id}
                onClick={() => onSelectDecision(dec)}
                className={`p-3 rounded-lg bg-slate-950/80 border border-slate-800 transition cursor-pointer group shadow-sm ${cardBorder}`}
              >
                {/* Top: Agent & Verdict badge */}
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[11px] font-mono text-slate-400 font-semibold truncate max-w-[140px]">
                    {dec.agent_id}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono border uppercase flex items-center gap-1 ${badgeBg}`}>
                    {isAllow && <ShieldCheck className="w-3 h-3" />}
                    {isHold && <PauseCircle className="w-3 h-3" />}
                    {isBlock && <ShieldAlert className="w-3 h-3" />}
                    {dec.verdict}
                  </span>
                </div>

                {/* Middle: Tool & Key Params */}
                <div className="text-xs font-mono font-bold text-slate-200 mb-1 flex items-center justify-between">
                  <span>{dec.tool}()</span>
                  <span className="text-[10px] text-slate-500 font-normal">
                    {new Date(dec.ts).toLocaleTimeString()}
                  </span>
                </div>

                {parsedParams.invoice_id && (
                  <div className="text-[11px] font-mono text-slate-400 flex items-center justify-between bg-slate-900/60 px-2 py-1 rounded mb-1.5">
                    <span>Inv: <strong className="text-slate-200">{parsedParams.invoice_id}</strong></span>
                    {parsedParams.amount_paise && (
                      <span className="text-slate-200 tabular-nums">
                        ₹{(parsedParams.amount_paise / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </span>
                    )}
                  </div>
                )}

                {/* Reason text */}
                <p className="text-[11px] text-slate-400 leading-tight mb-2 line-clamp-2">
                  {dec.reason}
                </p>

                {/* Human in the loop action for HOLD */}
                {isHold && (
                  <div className="mt-2 pt-2 border-t border-amber-500/20 flex items-center justify-between gap-2" onClick={(e) => e.stopPropagation()}>
                    <span className="text-[10px] font-mono text-amber-300 font-semibold">CFO Gate:</span>
                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => onApprove(dec.id)}
                        className="px-2.5 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-[10px] font-mono font-bold flex items-center gap-1 transition shadow"
                      >
                        <Check className="w-3 h-3" /> Approve
                      </button>
                      <button
                        onClick={() => onReject(dec.id)}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-rose-400 border border-rose-500/30 text-[10px] font-mono font-bold flex items-center gap-1 transition shadow"
                      >
                        <X className="w-3 h-3" /> Reject
                      </button>
                    </div>
                  </div>
                )}

                {/* Bottom link affordance */}
                <div className="mt-1 flex items-center justify-end text-[10px] text-slate-500 group-hover:text-emerald-400 transition font-mono">
                  <span>Inspect Forensics</span>
                  <ChevronRight className="w-3 h-3 ml-0.5" />
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
