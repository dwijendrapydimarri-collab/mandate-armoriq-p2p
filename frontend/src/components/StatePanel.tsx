import React from 'react';
import { BankAccount, APRecord, Invoice, Vendor, PurchaseOrder } from '../types';
import { Wallet, FileSpreadsheet, ArrowDownRight, ShieldCheck, AlertTriangle } from 'lucide-react';

interface StatePanelProps {
  accounts: BankAccount[];
  invoices: Invoice[];
  vendors: Vendor[];
  purchaseOrders: PurchaseOrder[];
  apRecords: APRecord[];
  governanceMode: 'on' | 'off';
}

export const StatePanel: React.FC<StatePanelProps> = ({
  accounts,
  invoices,
  vendors,
  purchaseOrders,
  apRecords,
  governanceMode,
}) => {
  const mandateAccount = accounts.find((a) => a.id === 'ACC-MANDATE-01');
  const currentBalancePaise = mandateAccount?.balance_paise || 425000000;
  const openingBalancePaise = 425000000;

  // Comparison benchmark numbers
  const governedBenchmarkPaise = 399172600; // Rs 39,91,726
  const ungovernedBenchmarkPaise = 385756000; // Rs 38,57,560
  const preventedLossPaise = 13416600; // Rs 1,34,166

  const formatRupees = (paise: number) => {
    return (paise / 100).toLocaleString('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  const vendorMap = new Map(vendors.map((v) => [v.id, v.name]));
  const apMap = new Map(apRecords.map((r) => [r.invoice_id, r]));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-full">
      {/* 1. Treasury / Bank Balance Card */}
      <div className="lg:col-span-4 bg-slate-900/70 border border-slate-800 rounded-xl p-4 flex flex-col justify-between shadow-inner">
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Wallet className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-mono font-bold text-slate-300 uppercase">
                ACC-MANDATE-01 Balance
              </span>
            </div>
            <span className="text-[10px] font-mono text-slate-500">
              Mandate Industries Pvt Ltd
            </span>
          </div>

          {/* Large Monospace Tabular Balance */}
          <div className="mt-1">
            <div className="text-3xl font-bold font-mono tracking-tight text-slate-100 tabular-nums">
              ₹{formatRupees(currentBalancePaise)}
            </div>
            <div className="text-[11px] font-mono text-slate-400 mt-1 flex items-center gap-2">
              <span>Opening: ₹{formatRupees(openingBalancePaise)}</span>
              <span>•</span>
              <span className="text-rose-400">
                Disbursed: ₹{formatRupees(openingBalancePaise - currentBalancePaise)}
              </span>
            </div>
          </div>
        </div>

        {/* Comparison Mode Highlights */}
        <div className="mt-4 pt-3 border-t border-slate-800/80 bg-slate-950/60 p-3 rounded-lg border border-slate-800">
          <div className="text-[10px] font-mono font-bold text-slate-400 uppercase mb-2 flex items-center justify-between">
            <span>Governance Benchmark A/B</span>
            <span className="text-emerald-400 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3" /> Proven Loss Prevention
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            <div className="p-2 rounded bg-slate-900 border border-slate-800">
              <span className="text-[10px] text-slate-500 block">GOVERNED (ON)</span>
              <span className="font-bold text-emerald-400 tabular-nums">₹{formatRupees(governedBenchmarkPaise)}</span>
            </div>
            <div className="p-2 rounded bg-slate-900 border border-slate-800">
              <span className="text-[10px] text-slate-500 block">UNGOVERNED (OFF)</span>
              <span className="font-bold text-rose-400 tabular-nums">₹{formatRupees(ungovernedBenchmarkPaise)}</span>
            </div>
          </div>
          <div className="mt-2 text-center bg-emerald-500/10 border border-emerald-500/30 rounded py-1 text-xs font-mono text-emerald-300 font-bold">
            PREVENTED FRAUD LOSS: ₹{formatRupees(preventedLossPaise)}
          </div>
        </div>
      </div>

      {/* 2. Accounts Payable Register Table */}
      <div className="lg:col-span-8 bg-slate-900/70 border border-slate-800 rounded-xl p-4 flex flex-col shadow-inner overflow-hidden">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="w-4 h-4 text-cyan-400" />
            <h2 className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wider">
              Accounts Payable (AP) Destination Register
            </h2>
          </div>
          <span className="text-[10px] font-mono text-slate-500">
            {invoices.length} Invoices Ingested
          </span>
        </div>

        <div className="flex-1 overflow-x-auto overflow-y-auto max-h-56">
          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead className="text-[10px] text-slate-500 uppercase bg-slate-950/80 sticky top-0 border-b border-slate-800">
              <tr>
                <th className="py-2 px-2.5">Invoice</th>
                <th className="py-2 px-2.5">Vendor</th>
                <th className="py-2 px-2.5">PO Ref</th>
                <th className="py-2 px-2.5 text-right">Stated Amount</th>
                <th className="py-2 px-2.5 text-center">Status</th>
                <th className="py-2 px-2.5">Audit Note</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300 text-[11px]">
              {invoices.map((inv) => {
                const record = apMap.get(inv.id);
                const outcome = record?.outcome || 'PENDING';
                const isPaid = outcome === 'PAID';
                const isHeld = outcome === 'HOLD' || outcome === 'HELD';
                const isBlocked = outcome === 'BLOCKED' || outcome === 'FLAGGED_FOR_REVIEW';

                const outcomeBadge = isPaid
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  : isHeld
                  ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                  : isBlocked
                  ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                  : 'bg-slate-800 text-slate-500 border-slate-700';

                return (
                  <tr key={inv.id} className="hover:bg-slate-850/50 transition">
                    <td className="py-2 px-2.5 font-bold text-slate-200">{inv.id}</td>
                    <td className="py-2 px-2.5 text-slate-400 truncate max-w-[130px]" title={vendorMap.get(inv.vendor_id)}>
                      {vendorMap.get(inv.vendor_id) || inv.vendor_id}
                    </td>
                    <td className="py-2 px-2.5 text-slate-400">{inv.po_id}</td>
                    <td className="py-2 px-2.5 text-right tabular-nums text-slate-200">
                      ₹{formatRupees(inv.stated_amount_paise)}
                    </td>
                    <td className="py-2 px-2.5 text-center">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase ${outcomeBadge}`}>
                        {outcome}
                      </span>
                    </td>
                    <td className="py-2 px-2.5 text-slate-400 text-[10px] truncate max-w-[200px]" title={record?.note || "Awaiting processing"}>
                      {record?.note || "Awaiting processing"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
