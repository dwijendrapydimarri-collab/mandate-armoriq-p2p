import React from 'react';
import { Decision, Invoice, PurchaseOrder, Vendor } from '../types';

interface TrustBoundaryMapProps {
  decision: Decision | null;
  invoices: Invoice[];
  purchaseOrders: PurchaseOrder[];
  vendors: Vendor[];
}

export const TrustBoundaryMap: React.FC<TrustBoundaryMapProps> = ({
  decision,
  invoices,
  purchaseOrders,
  vendors,
}) => {
  if (!decision) {
    return (
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 text-center text-xs text-slate-500 font-mono">
        Select a decision card from the stream or execute a probe to inspect the Trust Boundary Map.
      </div>
    );
  }

  let params: any = {};
  try {
    params = typeof decision.params === 'string' ? JSON.parse(decision.params) : decision.params;
  } catch (e) {
    params = {};
  }

  const invoiceId = params.invoice_id;
  const requestedPayee = params.payee_account;
  const requestedAmountPaise = params.amount_paise;

  const invoice = invoices.find((i) => i.id === invoiceId);
  const po = invoice ? purchaseOrders.find((p) => p.id === invoice.po_id) : null;
  const vendor = invoice ? vendors.find((v) => v.id === invoice.vendor_id) : null;

  const approvedPayee = vendor?.bank_account || 'UNKNOWN';
  const approvedPoAmountPaise = po?.amount_paise || 0;

  const isPayeeConflict = requestedPayee && approvedPayee !== 'UNKNOWN' && requestedPayee !== approvedPayee;
  const isAmountConflict = requestedAmountPaise && approvedPoAmountPaise > 0 && requestedAmountPaise > approvedPoAmountPaise;
  const isCapabilityConflict = decision.reason.includes('CAPABILITY') || decision.reason.includes('AGENT');

  return (
    <div className="bg-slate-900/90 border border-slate-700/80 rounded-xl p-5 space-y-4 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <span>🛡️</span> Trust Boundary Map
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Cryptographic Authority Boundary vs Untrusted Claims for Decision <span className="font-mono text-slate-300">{decision.id}</span>
          </p>
        </div>
        <span
          className={`px-2.5 py-1 text-xs font-mono font-bold rounded ${
            decision.verdict === 'ALLOW'
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
              : decision.verdict === 'HOLD'
              ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
              : 'bg-red-500/20 text-red-400 border border-red-500/40'
          }`}
        >
          {decision.verdict}
        </span>
      </div>

      {/* Side-by-Side Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left: Trusted Facts */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
              <span>✓</span> TRUSTED AUTHORITY FACTS
            </span>
            <span className="text-[10px] font-mono bg-emerald-950/40 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/30">
              ORIGIN: CFO SETUP (SEALED)
            </span>
          </div>

          <div className="space-y-2 text-xs font-mono text-slate-300">
            <div className="flex justify-between p-2 bg-slate-900/80 rounded border border-slate-800">
              <span className="text-slate-400">Approved Vendor:</span>
              <span className="font-bold text-slate-200">{vendor ? `${vendor.name} (${vendor.id})` : 'Vendor Master'}</span>
            </div>

            <div
              className={`flex justify-between p-2 rounded border ${
                isPayeeConflict ? 'bg-emerald-950/20 border-emerald-500/50 text-emerald-300' : 'bg-slate-900/80 border-slate-800'
              }`}
            >
              <span className="text-slate-400">Sealed Payee A/C:</span>
              <span className="font-bold">{approvedPayee}</span>
            </div>

            <div
              className={`flex justify-between p-2 rounded border ${
                isAmountConflict ? 'bg-emerald-950/20 border-emerald-500/50 text-emerald-300' : 'bg-slate-900/80 border-slate-800'
              }`}
            >
              <span className="text-slate-400">Authorized PO Cap:</span>
              <span className="font-bold tabular-nums">
                ₹{(approvedPoAmountPaise / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </span>
            </div>

            <div className="flex justify-between p-2 bg-slate-900/80 rounded border border-slate-800">
              <span className="text-slate-400">Authority Issuer:</span>
              <span className="font-bold text-slate-200">CFO (Human-in-the-Loop)</span>
            </div>
          </div>
        </div>

        {/* Right: Untrusted Claims */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
              <span>⚠️</span> UNTRUSTED INVOICE CLAIMS
            </span>
            <span className="text-[10px] font-mono bg-amber-950/40 text-amber-300 px-2 py-0.5 rounded border border-amber-500/30">
              ORIGIN: UNTRUSTED INVOICE TEXT
            </span>
          </div>

          <div className="space-y-2 text-xs font-mono text-slate-300">
            <div className="flex justify-between p-2 bg-slate-900/80 rounded border border-slate-800">
              <span className="text-slate-400">Invoice ID:</span>
              <span className="font-bold text-slate-200">{invoiceId || 'N/A'}</span>
            </div>

            <div
              className={`flex justify-between p-2 rounded border ${
                isPayeeConflict ? 'bg-red-950/40 border-red-500 text-red-300 font-bold' : 'bg-slate-900/80 border-slate-800'
              }`}
            >
              <span className="text-slate-400">Requested Payee:</span>
              <span className="font-bold">{requestedPayee || 'N/A'}</span>
            </div>

            <div
              className={`flex justify-between p-2 rounded border ${
                isAmountConflict ? 'bg-red-950/40 border-red-500 text-red-300 font-bold' : 'bg-slate-900/80 border-slate-800'
              }`}
            >
              <span className="text-slate-400">Requested Amount:</span>
              <span className="font-bold tabular-nums">
                {requestedAmountPaise
                  ? `₹${(requestedAmountPaise / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
                  : 'N/A'}
              </span>
            </div>

            <div className="p-2 bg-slate-900/80 rounded border border-slate-800">
              <span className="text-slate-400 text-[11px] block mb-1">Advisory Claim:</span>
              <p className="text-slate-300 text-[11px] italic truncate">
                "{invoice?.raw_text || 'Standard remittance text.'}"
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Explanatory Authority Conflict Statement */}
      <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800 text-xs text-slate-300 space-y-1">
        <span className="font-mono font-bold text-slate-200 block text-[11px] uppercase tracking-wider">
          Authority Conflict Analysis:
        </span>
        <p className="text-slate-300 leading-relaxed">
          {decision.verdict === 'ALLOW' ? (
            <span className="text-emerald-400 font-semibold">
              ✓ All proposed parameters match the sealed Authority Envelope. Destination account and amount are within CFO-approved bounds.
            </span>
          ) : decision.verdict === 'HOLD' ? (
            <span className="text-amber-300 font-semibold">
              ⏸️ Proposed payment amount exceeds the single-invoice ceiling (₹50,000.00). Held for explicit human CFO re-authorization.
            </span>
          ) : isPayeeConflict ? (
            <span className="text-red-400 font-semibold">
              🚫 Authority Breach: Requested payee account ({requestedPayee}) is NOT present in the sealed Authority Envelope ({approvedPayee}). Untrusted invoice text cannot mutate vendor master authority.
            </span>
          ) : isAmountConflict ? (
            <span className="text-red-400 font-semibold">
              🚫 Authority Breach: Requested amount exceeds the open Purchase Order authority cap. Parameter shift rejected.
            </span>
          ) : isCapabilityConflict ? (
            <span className="text-red-400 font-semibold">
              🚫 Capability Breach: Subagent ({decision.agent_id}) does not hold delegated capability for tool '{decision.tool}'.
            </span>
          ) : (
            <span className="text-red-400 font-semibold">
              🚫 Blocked by ArmorIQ runtime boundary: {decision.reason}.
            </span>
          )}
        </p>
      </div>
    </div>
  );
};
