export interface BankAccount {
  id: string;
  holder: string;
  balance_paise: number;
}

export interface Vendor {
  id: string;
  name: string;
  approved: boolean;
  bank_account: string;
  ifsc: string;
}

export interface PurchaseOrder {
  id: string;
  vendor_id: string;
  amount_paise: number;
  status: string;
  description: string;
}

export interface Invoice {
  id: string;
  vendor_id: string;
  po_id: string;
  stated_amount_paise: number;
  raw_text: string;
  source: string;
}

export interface Payment {
  id: string;
  invoice_id: string;
  payee_account: string;
  amount_paise: number;
  status: string;
  decision_id?: string;
}

export interface LedgerEntry {
  id: string;
  account: string;
  delta_paise: number;
  balance_after_paise: number;
  ref: string;
  ts: string;
}

export interface Mission {
  id: string;
  objective: string;
  intent_token?: string;
  plan_hash?: string;
  merkle_root?: string;
  status: string;
  sealed_at?: string;
}

export interface Delegation {
  id: string;
  mission_id: string;
  parent_agent: string;
  child_agent: string;
  capabilities: string; // JSON
  ceiling_paise: number;
  payee_scope: string; // JSON
  grant_ref?: string;
  signature?: string;
}

export interface Decision {
  id: string;
  mission_id: string;
  agent_id: string;
  tool: string;
  params: string; // JSON
  verdict: 'ALLOW' | 'HOLD' | 'BLOCK' | 'BYPASS';
  reason: string;
  proof: string; // JSON
  ts: string;
}

export interface APRecord {
  id: string;
  invoice_id: string;
  outcome: string;
  note: string;
  ts: string;
}

export interface ScenarioMetadata {
  scenario_id: string;
  status: 'CFO_SETUP' | 'SEALED' | 'READY_FOR_EXECUTION' | 'COMPLETED';
  objective: string;
  per_invoice_ceiling_paise: number;
  mission_ceiling_paise: number;
  plan_hash?: string;
  intent_token?: string;
  sealed_at?: string;
  created_at?: string;
}

export interface Counterfactual {
  projected_delta_paise: number;
  destination_account: string;
  status: string;
  prevented_loss_paise: number;
}

export interface ProbeResult {
  scenario_id: string;
  type: string;
  status: string;
  verdict: 'ALLOW' | 'HOLD' | 'BLOCK';
  reason: string;
  decision_id: string;
  data: any;
  proof: any;
  counterfactual?: Counterfactual | null;
}

export interface SystemState {
  scenario_id?: string;
  metadata?: ScenarioMetadata | null;
  accounts: BankAccount[];
  vendors: Vendor[];
  purchase_orders: PurchaseOrder[];
  invoices: Invoice[];
  payments: Payment[];
  ledger: LedgerEntry[];
  missions: Mission[];
  delegations: Delegation[];
  decisions: Decision[];
  ap_records: APRecord[];
}

