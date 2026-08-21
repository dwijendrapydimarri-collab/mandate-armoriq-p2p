import React, { useState } from 'react';
import { ScenarioMetadata, Vendor, PurchaseOrder } from '../types';

interface CFOSetupModalProps {
  isOpen: boolean;
  onClose: () => void;
  scenarioId: string;
  metadata?: ScenarioMetadata | null;
  existingVendors?: Vendor[];
  existingPOs?: PurchaseOrder[];
  onSetupSuccess: () => void;
}

interface FormVendor {
  id: string;
  name: string;
  bank_account: string;
  ifsc: string;
  approved: boolean;
}

interface FormPO {
  id: string;
  vendor_id: string;
  amount_rupees: string;
  description: string;
}

export const CFOSetupModal: React.FC<CFOSetupModalProps> = ({
  isOpen,
  onClose,
  scenarioId,
  metadata,
  existingVendors = [],
  existingPOs = [],
  onSetupSuccess,
}) => {
  const isSealed = metadata?.status === 'SEALED' || metadata?.status === 'READY_FOR_EXECUTION' || metadata?.status === 'COMPLETED';

  const [objective, setObjective] = useState(metadata?.objective || 'Autonomous Procure-to-Pay Mission');
  const [perInvoiceCeilingRs, setPerInvoiceCeilingRs] = useState(
    metadata ? (metadata.per_invoice_ceiling_paise / 100).toString() : '50000'
  );
  const [missionCeilingRs, setMissionCeilingRs] = useState(
    metadata ? (metadata.mission_ceiling_paise / 100).toString() : '300000'
  );

  const [vendors, setVendors] = useState<FormVendor[]>(
    existingVendors.length > 0
      ? existingVendors.map((v) => ({ ...v }))
      : [
          {
            id: 'V-01',
            name: 'Kirloskar Components',
            bank_account: '004701234567',
            ifsc: 'ICIC0000047',
            approved: true,
          },
          {
            id: 'V-02',
            name: 'Sunrise Packaging',
            bank_account: '201900887766',
            ifsc: 'SBIN0002019',
            approved: true,
          },
        ]
  );

  const [pos, setPOs] = useState<FormPO[]>(
    existingPOs.length > 0
      ? existingPOs.map((p) => ({
          id: p.id,
          vendor_id: p.vendor_id,
          amount_rupees: (p.amount_paise / 100).toString(),
          description: p.description,
        }))
      : [
          { id: 'PO-1001', vendor_id: 'V-01', amount_rupees: '38500', description: 'Precision Gears' },
          { id: 'PO-1002', vendor_id: 'V-02', amount_rupees: '12750', description: 'Corrugated Boxes' },
        ]
  );

  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleAddVendor = () => {
    const nextIdx = vendors.length + 1;
    setVendors([
      ...vendors,
      {
        id: `V-0${nextIdx}`,
        name: `New Vendor ${nextIdx}`,
        bank_account: '00470' + Math.floor(1000000 + Math.random() * 9000000),
        ifsc: 'ICIC0000047',
        approved: true,
      },
    ]);
  };

  const handleRemoveVendor = (idx: number) => {
    setVendors(vendors.filter((_, i) => i !== idx));
  };

  const handleAddPO = () => {
    const nextIdx = pos.length + 1;
    const defaultVendor = vendors[0]?.id || 'V-01';
    setPOs([
      ...pos,
      {
        id: `PO-100${nextIdx}`,
        vendor_id: defaultVendor,
        amount_rupees: '25000',
        description: 'Procurement item',
      },
    ]);
  };

  const handleRemovePO = (idx: number) => {
    setPOs(pos.filter((_, i) => i !== idx));
  };

  const handleSaveAndSeal = async (sealImmediately: boolean) => {
    setErrorMsg(null);
    setIsSubmitting(true);

    try {
      // Client validation
      const perInvPaise = Math.round(parseFloat(perInvoiceCeilingRs) * 100);
      const missionPaise = Math.round(parseFloat(missionCeilingRs) * 100);

      if (isNaN(perInvPaise) || perInvPaise <= 0 || isNaN(missionPaise) || missionPaise <= 0) {
        throw new Error('Ceilings must be valid positive numbers in Rupees.');
      }

      if (vendors.length === 0) {
        throw new Error('Please configure at least one vendor.');
      }

      const formattedPOs = pos.map((p) => {
        const amtPaise = Math.round(parseFloat(p.amount_rupees) * 100);
        if (isNaN(amtPaise) || amtPaise <= 0) {
          throw new Error(`Invalid amount for purchase order ${p.id}.`);
        }
        return {
          id: p.id,
          vendor_id: p.vendor_id,
          amount_paise: amtPaise,
          description: p.description,
        };
      });

      // 1. Submit CFO Setup
      const resSetup = await fetch('/api/scenario/cfo-setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario_id: scenarioId,
          vendors: vendors.map((v) => ({
            id: v.id,
            name: v.name,
            bank_account: v.bank_account,
            ifsc: v.ifsc,
            approved: v.approved,
          })),
          purchase_orders: formattedPOs,
          per_invoice_ceiling_paise: perInvPaise,
          mission_ceiling_paise: missionPaise,
        }),
      });

      if (!resSetup.ok) {
        const errData = await resSetup.json();
        throw new Error(errData.detail || 'Failed to save CFO setup.');
      }

      // 2. Seal if requested
      if (sealImmediately) {
        const resSeal = await fetch('/api/scenario/seal', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            scenario_id: scenarioId,
            objective: objective,
          }),
        });

        if (!resSeal.ok) {
          const errData = await resSeal.json();
          throw new Error(errData.detail || 'Failed to seal mission.');
        }
      }

      onSetupSuccess();
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'An error occurred during CFO setup.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50 sticky top-0 z-10">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 text-xs font-bold rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                PHASE 1: CFO SETUP
              </span>
              <h2 className="text-lg font-bold text-slate-100">Trusted Procurement Authority</h2>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Define approved vendors, payee bank accounts, open POs, and ceilings before mission seal.
            </p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200 text-xl font-bold p-1">
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 flex-1 text-sm">
          {isSealed && (
            <div className="p-3.5 bg-indigo-950/40 border border-indigo-500/40 rounded-lg text-indigo-200 flex items-start gap-2.5">
              <span className="text-lg">🔒</span>
              <div>
                <p className="font-semibold text-xs uppercase tracking-wide">Mission Authority is Sealed & Frozen</p>
                <p className="text-xs text-indigo-300/90 mt-0.5">
                  The trusted vendor master, PO references, and authority ceilings cannot be edited after seal. To change authority, click "New Judge Scenario" in the top bar.
                </p>
              </div>
            </div>
          )}

          {errorMsg && (
            <div className="p-3 bg-red-950/50 border border-red-500/50 rounded-lg text-red-200 text-xs">
              ⚠️ {errorMsg}
            </div>
          )}

          {/* Mission Objective */}
          <div>
            <label className="block text-xs font-mono uppercase text-slate-400 mb-1">Mission Objective</label>
            <input
              type="text"
              disabled={isSealed}
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 font-medium focus:border-amber-500 focus:outline-none disabled:opacity-60"
            />
          </div>

          {/* Authority Ceilings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-950/60 p-4 rounded-lg border border-slate-800">
            <div>
              <label className="block text-xs font-mono uppercase text-slate-400 mb-1">
                Per-Invoice Authority Ceiling (₹)
              </label>
              <input
                type="number"
                disabled={isSealed}
                value={perInvoiceCeilingRs}
                onChange={(e) => setPerInvoiceCeilingRs(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-1.5 text-slate-100 font-mono tabular-nums focus:border-amber-500 focus:outline-none disabled:opacity-60"
              />
              <p className="text-[11px] text-slate-500 mt-1">Invoices above this amount trigger human CFO HOLD</p>
            </div>
            <div>
              <label className="block text-xs font-mono uppercase text-slate-400 mb-1">
                Mission Cumulative Ceiling (₹)
              </label>
              <input
                type="number"
                disabled={isSealed}
                value={missionCeilingRs}
                onChange={(e) => setMissionCeilingRs(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-1.5 text-slate-100 font-mono tabular-nums focus:border-amber-500 focus:outline-none disabled:opacity-60"
              />
              <p className="text-[11px] text-slate-500 mt-1">Total spend cap for the entire mission</p>
            </div>
          </div>

          {/* Approved Vendors Table */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-mono uppercase text-slate-400 font-semibold">
                Approved Vendor Master ({vendors.length})
              </label>
              {!isSealed && (
                <button
                  type="button"
                  onClick={handleAddVendor}
                  className="text-xs text-amber-400 hover:text-amber-300 font-medium"
                >
                  + Add Vendor
                </button>
              )}
            </div>
            <div className="space-y-2">
              {vendors.map((v, idx) => (
                <div key={idx} className="grid grid-cols-12 gap-2 bg-slate-950/40 p-2.5 rounded border border-slate-800 items-center">
                  <div className="col-span-2">
                    <input
                      type="text"
                      disabled={isSealed}
                      placeholder="ID"
                      value={v.id}
                      onChange={(e) => {
                        const copy = [...vendors];
                        copy[idx].id = e.target.value;
                        setVendors(copy);
                      }}
                      className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs font-mono text-slate-200"
                    />
                  </div>
                  <div className="col-span-4">
                    <input
                      type="text"
                      disabled={isSealed}
                      placeholder="Vendor Name"
                      value={v.name}
                      onChange={(e) => {
                        const copy = [...vendors];
                        copy[idx].name = e.target.value;
                        setVendors(copy);
                      }}
                      className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200"
                    />
                  </div>
                  <div className="col-span-4">
                    <input
                      type="text"
                      disabled={isSealed}
                      placeholder="Bank Account"
                      value={v.bank_account}
                      onChange={(e) => {
                        const copy = [...vendors];
                        copy[idx].bank_account = e.target.value;
                        setVendors(copy);
                      }}
                      className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs font-mono text-slate-200"
                    />
                  </div>
                  <div className="col-span-2 flex items-center justify-end gap-2">
                    <label className="flex items-center gap-1 text-[11px] text-slate-400">
                      <input
                        type="checkbox"
                        disabled={isSealed}
                        checked={v.approved}
                        onChange={(e) => {
                          const copy = [...vendors];
                          copy[idx].approved = e.target.checked;
                          setVendors(copy);
                        }}
                      />
                      Appr
                    </label>
                    {!isSealed && (
                      <button
                        type="button"
                        onClick={() => handleRemoveVendor(idx)}
                        className="text-red-400 hover:text-red-300 text-xs px-1"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Open Purchase Orders Table */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-mono uppercase text-slate-400 font-semibold">
                Open Purchase Orders ({pos.length})
              </label>
              {!isSealed && (
                <button
                  type="button"
                  onClick={handleAddPO}
                  className="text-xs text-amber-400 hover:text-amber-300 font-medium"
                >
                  + Add PO
                </button>
              )}
            </div>
            <div className="space-y-2">
              {pos.map((p, idx) => (
                <div key={idx} className="grid grid-cols-12 gap-2 bg-slate-950/40 p-2.5 rounded border border-slate-800 items-center">
                  <div className="col-span-2">
                    <input
                      type="text"
                      disabled={isSealed}
                      placeholder="PO ID"
                      value={p.id}
                      onChange={(e) => {
                        const copy = [...pos];
                        copy[idx].id = e.target.value;
                        setPOs(copy);
                      }}
                      className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs font-mono text-slate-200"
                    />
                  </div>
                  <div className="col-span-3">
                    <select
                      disabled={isSealed}
                      value={p.vendor_id}
                      onChange={(e) => {
                        const copy = [...pos];
                        copy[idx].vendor_id = e.target.value;
                        setPOs(copy);
                      }}
                      className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200"
                    >
                      {vendors.map((v) => (
                        <option key={v.id} value={v.id}>
                          {v.id} ({v.name})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="col-span-3">
                    <input
                      type="number"
                      disabled={isSealed}
                      placeholder="Amount (₹)"
                      value={p.amount_rupees}
                      onChange={(e) => {
                        const copy = [...pos];
                        copy[idx].amount_rupees = e.target.value;
                        setPOs(copy);
                      }}
                      className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs font-mono text-slate-200 tabular-nums"
                    />
                  </div>
                  <div className="col-span-3">
                    <input
                      type="text"
                      disabled={isSealed}
                      placeholder="Description"
                      value={p.description}
                      onChange={(e) => {
                        const copy = [...pos];
                        copy[idx].description = e.target.value;
                        setPOs(copy);
                      }}
                      className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200"
                    />
                  </div>
                  <div className="col-span-1 text-right">
                    {!isSealed && (
                      <button
                        type="button"
                        onClick={() => handleRemovePO(idx)}
                        className="text-red-400 hover:text-red-300 text-xs px-1"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/80 flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-medium"
          >
            Cancel
          </button>
          {!isSealed && (
            <div className="flex items-center gap-2">
              <button
                disabled={isSubmitting}
                onClick={() => handleSaveAndSeal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 rounded-lg text-xs font-semibold transition"
              >
                Save Draft Setup
              </button>
              <button
                disabled={isSubmitting}
                onClick={() => handleSaveAndSeal(true)}
                className="px-5 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-lg text-xs font-bold transition flex items-center gap-1.5 shadow-lg shadow-amber-500/20"
              >
                <span>🔒</span>
                Seal Authority Envelope
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
