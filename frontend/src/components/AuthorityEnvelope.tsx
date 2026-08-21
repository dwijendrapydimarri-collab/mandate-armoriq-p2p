import React from 'react';
import { Mission, Delegation, ScenarioMetadata, Vendor, PurchaseOrder } from '../types';

interface AuthorityEnvelopeProps {
  mission: Mission | null;
  metadata?: ScenarioMetadata | null;
  delegations: Delegation[];
  vendors: Vendor[];
  purchaseOrders: PurchaseOrder[];
  armoriqMode?: string;
  onOpenCfoSetup?: () => void;
}

export const AuthorityEnvelope: React.FC<AuthorityEnvelopeProps> = ({
  mission,
  metadata,
  delegations,
  vendors,
  purchaseOrders,
  armoriqMode = 'local',
  onOpenCfoSetup,
}) => {
  const isSealed = mission?.status === 'SEALED' || metadata?.status === 'SEALED' || metadata?.status === 'READY_FOR_EXECUTION' || metadata?.status === 'COMPLETED';

  const approvedVendors = vendors.filter((v) => v.approved);
  const perInvoiceCeilingPaise = metadata?.per_invoice_ceiling_paise ?? 5000000;
  const missionCeilingPaise = metadata?.mission_ceiling_paise ?? 30000000;

  const perInvoiceRs = (perInvoiceCeilingPaise / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 });
  const missionRs = (missionCeilingPaise / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 });

  return (
    <div className="bg-slate-900/90 border border-slate-700/80 rounded-xl p-4 space-y-3.5 relative shadow-xl backdrop-blur-md">
      {/* Header: Title & Sealed Lock Badge */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2.5">
          <div
            className={`w-7 h-7 rounded-lg flex items-center justify-center text-sm font-bold shadow ${
              isSealed
                ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40'
                : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
            }`}
          >
            {isSealed ? '🔒' : '🔓'}
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              Sealed Authority Envelope
              {isSealed ? (
                <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded">
                  FROZEN & IMMUTABLE
                </span>
              ) : (
                <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded">
                  DRAFT / UNSEALED
                </span>
              )}
            </h3>
            <p className="text-[11px] text-slate-400">
              Named CFO → Plan Capture → Cryptographic Intent Token & Delegation Grants
            </p>
          </div>
        </div>

        {!isSealed && onOpenCfoSetup && (
          <button
            onClick={onOpenCfoSetup}
            className="px-2.5 py-1 bg-amber-500 hover:bg-amber-400 text-slate-950 rounded text-xs font-bold transition"
          >
            Configure & Seal
          </button>
        )}
      </div>

      {/* Grid: Authority Bounds */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs font-mono">
        {/* Approved Payees */}
        <div className="bg-slate-950/70 p-3 rounded-lg border border-slate-800 space-y-1 md:col-span-2">
          <span className="text-slate-400 text-[11px] uppercase tracking-wider block font-semibold">
            Approved Payees ({approvedVendors.length})
          </span>
          <div className="flex flex-wrap gap-1.5 pt-1">
            {approvedVendors.map((v) => (
              <span
                key={v.id}
                className="px-2 py-0.5 bg-slate-900 text-slate-200 border border-slate-700/80 rounded text-[11px] flex items-center gap-1"
                title={`${v.name} (${v.bank_account})`}
              >
                <span className="text-emerald-400 font-bold">✓</span>
                <span className="font-bold">{v.id}</span>: {v.bank_account}
              </span>
            ))}
          </div>
        </div>

        {/* Per-Invoice Ceiling */}
        <div className="bg-slate-950/70 p-3 rounded-lg border border-slate-800 space-y-1">
          <span className="text-slate-400 text-[11px] uppercase tracking-wider block font-semibold">
            Per-Invoice Ceiling
          </span>
          <span className="text-amber-300 font-bold text-sm tabular-nums block mt-1">₹{perInvoiceRs}</span>
          <span className="text-[10px] text-slate-500 block">&gt; ₹{perInvoiceRs} triggers CFO HOLD</span>
        </div>

        {/* Mission Spend Cap */}
        <div className="bg-slate-950/70 p-3 rounded-lg border border-slate-800 space-y-1">
          <span className="text-slate-400 text-[11px] uppercase tracking-wider block font-semibold">
            Mission Spend Cap
          </span>
          <span className="text-indigo-300 font-bold text-sm tabular-nums block mt-1">₹{missionRs}</span>
          <span className="text-[10px] text-slate-500 block">Open POs: {purchaseOrders.length}</span>
        </div>
      </div>

      {/* Delegation Grants */}
      <div className="bg-slate-950/50 p-3 rounded-lg border border-slate-800/80 text-xs">
        <span className="text-slate-400 text-[11px] font-mono uppercase tracking-wider block font-semibold mb-1.5">
          Delegated Subagent Capabilities
        </span>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs font-mono">
          <div className="p-2 bg-slate-900/80 rounded border border-slate-800 flex items-center justify-between">
            <span className="text-blue-300 font-semibold">matcher-agent:</span>
            <span className="px-2 py-0.5 bg-blue-950/40 text-blue-300 border border-blue-500/30 rounded text-[11px]">
              capabilities: ["fetch_invoices"] (Read-Only)
            </span>
          </div>
          <div className="p-2 bg-slate-900/80 rounded border border-slate-800 flex items-center justify-between">
            <span className="text-emerald-300 font-semibold">disburser-agent:</span>
            <span className="px-2 py-0.5 bg-emerald-950/40 text-emerald-300 border border-emerald-500/30 rounded text-[11px]">
              capabilities: ["initiate_payment"] (Disbursement Rail)
            </span>
          </div>
        </div>
      </div>

      {/* Cryptographic Token State & Honest Local Disclosure */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-[11px] font-mono text-slate-400">
        <div className="flex items-center gap-3">
          <span>
            plan_hash:{' '}
            <span className="text-slate-200">{mission?.plan_hash ? mission.plan_hash.slice(0, 16) + '...' : 'pending_seal'}</span>
          </span>
          <span>
            intent_token:{' '}
            <span className="text-slate-200">{mission?.intent_token ? mission.intent_token.slice(0, 16) + '...' : 'pending_mint'}</span>
          </span>
        </div>

        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span>ENFORCEMENT: {armoriqMode.toUpperCase()} ADAPTER (ArmorIQ contract)</span>
        </div>
      </div>
    </div>
  );
};
