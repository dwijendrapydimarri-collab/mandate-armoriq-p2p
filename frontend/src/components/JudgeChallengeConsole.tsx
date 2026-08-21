import React, { useState } from 'react';
import { ProbeResult, Vendor, PurchaseOrder } from '../types';
import { CounterfactualProof } from './CounterfactualProof';

interface JudgeChallengeConsoleProps {
  isOpen: boolean;
  onClose: () => void;
  scenarioId: string;
  vendors: Vendor[];
  purchaseOrders: PurchaseOrder[];
  onProbeExecuted?: () => void;
}

export const JudgeChallengeConsole: React.FC<JudgeChallengeConsoleProps> = ({
  isOpen,
  onClose,
  scenarioId,
  vendors,
  purchaseOrders,
  onProbeExecuted,
}) => {
  const [selectedAgent, setSelectedAgent] = useState<'disburser-agent' | 'matcher-agent' | 'controller-agent'>(
    'disburser-agent'
  );
  const [selectedTool, setSelectedTool] = useState<string>('initiate_payment');

  const defaultPayee = vendors[0]?.bank_account || '004701234567';
  const defaultPO = purchaseOrders[0];

  const [invoiceId, setInvoiceId] = useState('INV-PROBE-01');
  const [payeeAccount, setPayeeAccount] = useState(defaultPayee);
  const [amountRupees, setAmountRupees] = useState(
    defaultPO ? (defaultPO.amount_paise / 100).toString() : '38500'
  );

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [probeResult, setProbeResult] = useState<ProbeResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  // Preset 1: Valid Payment
  const applyPresetValid = () => {
    setSelectedAgent('disburser-agent');
    setSelectedTool('initiate_payment');
    setInvoiceId('INV-2036');
    setPayeeAccount(vendors[0]?.bank_account || '004701234567');
    setAmountRupees(vendors[0] ? '38500' : '38500');
    setProbeResult(null);
    setErrorMsg(null);
  };

  // Preset 2: Unapproved Payee (Attack A)
  const applyPresetUnapprovedPayee = () => {
    setSelectedAgent('disburser-agent');
    setSelectedTool('initiate_payment');
    setInvoiceId('INV-2041');
    setPayeeAccount('509900443322'); // Attacker rogue account
    setAmountRupees('46200');
    setProbeResult(null);
    setErrorMsg(null);
  };

  // Preset 3: Excess Amount (Attack C)
  const applyPresetExcessAmount = () => {
    setSelectedAgent('disburser-agent');
    setSelectedTool('initiate_payment');
    setInvoiceId('INV-2044');
    setPayeeAccount(vendors[4]?.bank_account || '501001122334');
    setAmountRupees('87240'); // 10x over PO-1005 (₹8,724)
    setProbeResult(null);
    setErrorMsg(null);
  };

  // Preset 4: Matcher Direct Spend (Attack B)
  const applyPresetMatcherSpend = () => {
    setSelectedAgent('matcher-agent'); // Unauthorized agent capability
    setSelectedTool('initiate_payment');
    setInvoiceId('INV-2042');
    setPayeeAccount(vendors[2]?.bank_account || '004709988776');
    setAmountRupees('9450');
    setProbeResult(null);
    setErrorMsg(null);
  };

  const handleExecuteProbe = async () => {
    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      let params: Record<string, any> = {};

      if (selectedTool === 'initiate_payment') {
        const amtPaise = Math.round(parseFloat(amountRupees) * 100);
        if (isNaN(amtPaise) || amtPaise <= 0) {
          throw new Error('Please enter a valid positive payment amount in Rupees.');
        }
        if (!payeeAccount.trim()) {
          throw new Error('Payee account number is required.');
        }
        params = {
          invoice_id: invoiceId.trim(),
          payee_account: payeeAccount.trim(),
          amount_paise: amtPaise,
        };
      } else if (selectedTool === 'write_ap_record') {
        params = {
          invoice_id: invoiceId.trim(),
          outcome: 'HOLD',
          note: 'Manual probe AP outcome test.',
        };
      }

      const res = await fetch('/api/scenario/probe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario_id: scenarioId,
          agent_id: selectedAgent,
          tool: selectedTool,
          params: params,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Probe execution failed.');
      }

      setProbeResult(data);
      if (onProbeExecuted) {
        onProbeExecuted();
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Error running security probe.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50 sticky top-0 z-10">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 text-xs font-bold rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                SECURITY PROBE CONSOLE
              </span>
              <h2 className="text-lg font-bold text-slate-100">Direct Authority Boundary Challenge</h2>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Propose typed tool proposals directly through the exact gateway.py → ArmorIQ → MCP tool path.
            </p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200 text-xl font-bold p-1">
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 flex-1 text-sm">
          {/* Label Banner */}
          <div className="p-3 bg-purple-950/40 border border-purple-500/40 rounded-lg text-xs text-purple-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-base">⚡</span>
              <span className="font-mono font-bold tracking-wider text-purple-300">
                TEST PROPOSAL — NOT AN LLM DECISION
              </span>
            </div>
            <span className="text-[11px] text-slate-400 font-mono">Real Gateway Enforcement Path</span>
          </div>

          {errorMsg && (
            <div className="p-3 bg-red-950/50 border border-red-500/50 rounded-lg text-red-200 text-xs">
              ⚠️ {errorMsg}
            </div>
          )}

          {/* Preset Challenge Selectors */}
          <div>
            <label className="block text-xs font-mono uppercase text-slate-400 mb-2 font-semibold">
              Select Challenge Preset
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              <button
                type="button"
                onClick={applyPresetValid}
                className="p-2.5 bg-slate-950 border border-slate-700 hover:border-emerald-500/60 rounded-lg text-left transition"
              >
                <span className="block text-xs font-bold text-emerald-400">1. Valid Payment</span>
                <span className="text-[11px] text-slate-400 block mt-0.5">Inside scope → ALLOW</span>
              </button>
              <button
                type="button"
                onClick={applyPresetUnapprovedPayee}
                className="p-2.5 bg-slate-950 border border-slate-700 hover:border-red-500/60 rounded-lg text-left transition"
              >
                <span className="block text-xs font-bold text-red-400">2. Unapproved Payee</span>
                <span className="text-[11px] text-slate-400 block mt-0.5">Rogue A/C → BLOCK</span>
              </button>
              <button
                type="button"
                onClick={applyPresetExcessAmount}
                className="p-2.5 bg-slate-950 border border-slate-700 hover:border-red-500/60 rounded-lg text-left transition"
              >
                <span className="block text-xs font-bold text-red-400">3. Excess Amount</span>
                <span className="text-[11px] text-slate-400 block mt-0.5">10x PO cap → BLOCK</span>
              </button>
              <button
                type="button"
                onClick={applyPresetMatcherSpend}
                className="p-2.5 bg-slate-950 border border-slate-700 hover:border-red-500/60 rounded-lg text-left transition"
              >
                <span className="block text-xs font-bold text-red-400">4. Matcher Direct Spend</span>
                <span className="text-[11px] text-slate-400 block mt-0.5">No capability → BLOCK</span>
              </button>
            </div>
          </div>

          {/* Proposal Config Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-950/60 p-4 rounded-lg border border-slate-800">
            <div>
              <label className="block text-xs font-mono uppercase text-slate-400 mb-1">Agent Identity</label>
              <select
                value={selectedAgent}
                onChange={(e: any) => setSelectedAgent(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-slate-100 text-xs font-mono focus:border-purple-500 focus:outline-none"
              >
                <option value="disburser-agent">disburser-agent (Has initiate_payment)</option>
                <option value="matcher-agent">matcher-agent (Read-only)</option>
                <option value="controller-agent">controller-agent (Delegator)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono uppercase text-slate-400 mb-1">Target MCP Tool</label>
              <select
                value={selectedTool}
                onChange={(e) => setSelectedTool(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-slate-100 text-xs font-mono focus:border-purple-500 focus:outline-none"
              >
                <option value="initiate_payment">initiate_payment (Disbursement Rail)</option>
                <option value="fetch_invoices">fetch_invoices (Untrusted Read)</option>
                <option value="get_vendor_master">get_vendor_master (Trusted Read)</option>
                <option value="list_open_purchase_orders">list_open_purchase_orders (Trusted Read)</option>
                <option value="write_ap_record">write_ap_record (AP Register)</option>
              </select>
            </div>

            {selectedTool === 'initiate_payment' && (
              <>
                <div>
                  <label className="block text-xs font-mono uppercase text-slate-400 mb-1">Invoice Reference ID</label>
                  <input
                    type="text"
                    value={invoiceId}
                    onChange={(e) => setInvoiceId(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-slate-100 text-xs font-mono focus:border-purple-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-mono uppercase text-slate-400 mb-1">Proposed Amount (₹)</label>
                  <input
                    type="number"
                    value={amountRupees}
                    onChange={(e) => setAmountRupees(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-slate-100 text-xs font-mono tabular-nums focus:border-purple-500 focus:outline-none"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-xs font-mono uppercase text-slate-400 mb-1">
                    Destination Payee Bank Account
                  </label>
                  <input
                    type="text"
                    value={payeeAccount}
                    onChange={(e) => setPayeeAccount(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-slate-100 text-xs font-mono focus:border-purple-500 focus:outline-none"
                  />
                </div>
              </>
            )}
          </div>

          {/* Execution Button */}
          <div>
            <button
              type="button"
              disabled={isSubmitting}
              onClick={handleExecuteProbe}
              className="w-full py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 shadow-lg shadow-purple-600/20"
            >
              <span>⚡</span>
              Dispatch Probe Proposal Through Gateway
            </button>
          </div>

          {/* Results Surface */}
          {probeResult && (
            <div className="space-y-4 pt-2 border-t border-slate-800 animate-fadeIn">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono uppercase text-slate-400 font-semibold">ArmorIQ Runtime Verdict</span>
                <span
                  className={`px-3 py-1 rounded text-xs font-mono font-bold tracking-wider ${
                    probeResult.verdict === 'ALLOW'
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                      : probeResult.verdict === 'HOLD'
                      ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                      : 'bg-red-500/20 text-red-400 border border-red-500/40'
                  }`}
                >
                  VERDICT: {probeResult.verdict}
                </span>
              </div>

              {/* Verdict Summary Card */}
              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2 font-mono text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Reason Code:</span>
                  <span className="text-slate-200 font-bold">{probeResult.reason}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Decision ID:</span>
                  <span className="text-slate-300">{probeResult.decision_id}</span>
                </div>
                {probeResult.proof && (
                  <div className="pt-2 border-t border-slate-800/80">
                    <span className="text-slate-500 text-[11px] block mb-1">Proof Context:</span>
                    <pre className="p-2 bg-slate-900 rounded text-[11px] text-slate-300 overflow-x-auto">
                      {JSON.stringify(probeResult.proof, null, 2)}
                    </pre>
                  </div>
                )}
              </div>

              {/* Counterfactual Proof Component */}
              {probeResult.counterfactual && (
                <CounterfactualProof counterfactual={probeResult.counterfactual} />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
