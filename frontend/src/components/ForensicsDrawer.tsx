import React from 'react';
import { X, ShieldAlert, ShieldCheck, User, Key, FileCode, CheckCircle2, AlertOctagon } from 'lucide-react';
import { Decision, Delegation, Mission } from '../types';

interface ForensicsDrawerProps {
  decision: Decision | null;
  delegations: Delegation[];
  missions: Mission[];
  onClose: () => void;
}

export const ForensicsDrawer: React.FC<ForensicsDrawerProps> = ({
  decision,
  delegations,
  missions,
  onClose,
}) => {
  if (!decision) return null;

  const isBlocked = decision.verdict === 'BLOCK';
  const isHold = decision.verdict === 'HOLD';
  const isAllow = decision.verdict === 'ALLOW';

  let parsedParams: any = {};
  try {
    parsedParams = JSON.parse(decision.params);
  } catch (e) {
    parsedParams = {};
  }

  let parsedProof: any = {};
  try {
    parsedProof = JSON.parse(decision.proof);
  } catch (e) {
    parsedProof = {};
  }

  const delegation = delegations.find((d) => d.child_agent === decision.agent_id);
  const mission = missions.find((m) => m.id === decision.mission_id) || missions[0];

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/70 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-xl bg-slate-900 border-l border-slate-800 h-full flex flex-col shadow-2xl overflow-y-auto">
        {/* Top Header */}
        <div className="p-4 border-b border-slate-800 bg-slate-950 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-cyan-400"></span>
            <h2 className="text-sm font-bold font-mono text-slate-100 uppercase tracking-wider">
              Forensic Authorization Chain
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Topmost Authorization Banner */}
        <div className={`p-4 border-b ${isBlocked ? 'bg-rose-950/50 border-rose-900/50' : 'bg-emerald-950/40 border-emerald-900/40'}`}>
          <div className="text-[10px] font-mono text-slate-400 uppercase">Primary Authority Provenance:</div>
          <div className="text-lg font-bold font-mono tracking-tight mt-0.5 flex items-center gap-2">
            {isBlocked ? (
              <>
                <AlertOctagon className="w-5 h-5 text-rose-400" />
                <span className="text-rose-400">AUTHORIZED BY: NOBODY</span>
              </>
            ) : (
              <>
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <span className="text-emerald-400">AUTHORIZED BY: CFO (Vikram Mehta)</span>
              </>
            )}
          </div>
          <p className="text-xs text-slate-300 font-mono mt-1">
            Verdict: <strong className={isBlocked ? 'text-rose-400' : 'text-emerald-400'}>{decision.verdict}</strong> — {decision.reason}
          </p>
        </div>

        {/* Provenance Audit Steps */}
        <div className="p-5 space-y-6 flex-1 text-xs font-mono">
          {/* Step 1: Named Human */}
          <div className="relative pl-6 border-l-2 border-cyan-500/40">
            <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-cyan-500 flex items-center justify-center text-[10px] text-black font-bold">1</div>
            <div className="text-[11px] text-cyan-400 font-bold uppercase">Root Human Intent</div>
            <div className="mt-1 p-2.5 rounded bg-slate-950 border border-slate-800 text-slate-200">
              <div>Principal: <strong>CFO Vikram Mehta (Mandate Industries)</strong></div>
              <div className="text-slate-400 mt-0.5">Objective: "{mission?.objective || "Clear this week's vendor invoices"}"</div>
            </div>
          </div>

          {/* Step 2: Intent Token & Sealed Envelope */}
          <div className="relative pl-6 border-l-2 border-indigo-500/40">
            <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-indigo-500 flex items-center justify-center text-[10px] text-white font-bold">2</div>
            <div className="text-[11px] text-indigo-400 font-bold uppercase">ArmorIQ Sealed Scope & Token</div>
            <div className="mt-1 p-2.5 rounded bg-slate-950 border border-slate-800 space-y-1 text-slate-300">
              <div>Token: <span className="text-emerald-400">{mission?.intent_token || parsedProof.intent_token || "tok_intent_sealed"}</span></div>
              <div className="text-[11px] text-slate-400">Plan Hash: <span className="text-slate-200">{mission?.plan_hash || "sha256:7f8a9b2c..."}</span></div>
              <div className="text-[11px] text-slate-400">Merkle Root: <span className="text-slate-200">{mission?.merkle_root || "0x9812af..."}</span></div>
              <div className="text-[11px] text-slate-400">Sealed At: <span className="text-slate-200">{mission?.sealed_at || decision.ts}</span></div>
            </div>
          </div>

          {/* Step 3: Delegation Grant */}
          <div className="relative pl-6 border-l-2 border-blue-500/40">
            <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-blue-500 flex items-center justify-center text-[10px] text-white font-bold">3</div>
            <div className="text-[11px] text-blue-400 font-bold uppercase">Delegation Grant & Attenuation</div>
            <div className="mt-1 p-2.5 rounded bg-slate-950 border border-slate-800 space-y-1 text-slate-300">
              <div>Calling Agent: <strong className="text-slate-100">{decision.agent_id}</strong></div>
              <div>Ceiling: <strong className="text-slate-100">₹50,000 / invoice</strong></div>
              <div>Delegated Tool Caps: <span className="text-cyan-300">[{decision.tool}]</span></div>
              <div className="text-[10px] text-slate-500 truncate">Ed25519 Sig: {delegation?.signature || "ed25519:5c3b99..."}</div>
            </div>
          </div>

          {/* Step 4: Tool Invocation Parameters */}
          <div className="relative pl-6 border-l-2 border-amber-500/40">
            <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-amber-500 flex items-center justify-center text-[10px] text-black font-bold">4</div>
            <div className="text-[11px] text-amber-400 font-bold uppercase">Action & Ingress Parameters</div>
            <div className="mt-1 p-2.5 rounded bg-slate-950 border border-slate-800 space-y-1 text-slate-300">
              <div>Tool: <strong className="text-slate-100">{decision.tool}</strong></div>
              {parsedParams.invoice_id && <div>Invoice: <strong className="text-slate-100">{parsedParams.invoice_id}</strong></div>}
              {parsedParams.payee_account && <div>Payee Account: <strong className={isBlocked ? 'text-rose-400 font-bold' : 'text-slate-100'}>{parsedParams.payee_account}</strong></div>}
              {parsedParams.amount_paise && <div>Amount: <strong className="text-slate-100">₹{(parsedParams.amount_paise / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong></div>}
            </div>
          </div>

          {/* Step 5: ArmorIQ Seam Evaluation & Decision Proof */}
          <div className="relative pl-6 border-l-2 border-emerald-500/40">
            <div className={`absolute -left-[9px] top-0 w-4 h-4 rounded-full ${isBlocked ? 'bg-rose-500' : 'bg-emerald-500'} flex items-center justify-center text-[10px] text-white font-bold`}>5</div>
            <div className={`text-[11px] font-bold uppercase ${isBlocked ? 'text-rose-400' : 'text-emerald-400'}`}>
              ArmorIQ Verdict & Ledger Result
            </div>
            <div className="mt-1 p-2.5 rounded bg-slate-950 border border-slate-800 space-y-1.5 text-slate-300">
              <div className="flex items-center justify-between">
                <span>Verdict:</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${isBlocked ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                  {decision.verdict}
                </span>
              </div>
              <div>Reason Code: <span className="text-slate-200">{decision.reason}</span></div>
              <div className="text-[10px] text-slate-400 bg-slate-900 p-2 rounded border border-slate-800 font-mono whitespace-pre-wrap">
                {JSON.stringify(parsedProof, null, 2)}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-slate-800 bg-slate-950 text-right">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono font-semibold transition"
          >
            Close Forensics
          </button>
        </div>
      </div>
    </div>
  );
};
