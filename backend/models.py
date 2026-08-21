"""
MANDATE — SQLModel Data Models
All monetary amounts are stored strictly as integer paise (*_paise).
No floats are permitted anywhere in storage or arithmetic.
"""

from typing import Optional
from sqlmodel import SQLModel, Field


class BankAccount(SQLModel, table=True):
    __tablename__ = "bank_account"
    id: str = Field(primary_key=True)
    holder: str
    balance_paise: int = Field(default=0)


class Vendor(SQLModel, table=True):
    __tablename__ = "vendor"
    id: str = Field(primary_key=True)
    name: str
    approved: bool = Field(default=True)
    bank_account: str
    ifsc: str


class PurchaseOrder(SQLModel, table=True):
    __tablename__ = "purchase_order"
    id: str = Field(primary_key=True)
    vendor_id: str
    amount_paise: int
    status: str = Field(default="OPEN")
    description: str = Field(default="")


class Invoice(SQLModel, table=True):
    __tablename__ = "invoice"
    id: str = Field(primary_key=True)
    vendor_id: str
    po_id: str
    stated_amount_paise: int
    raw_text: str = Field(default="")
    source: str = Field(default="INCOMING_MAIL")


class Payment(SQLModel, table=True):
    __tablename__ = "payment"
    id: str = Field(primary_key=True)
    invoice_id: str
    payee_account: str
    amount_paise: int
    status: str = Field(default="PENDING")
    decision_id: Optional[str] = Field(default=None)


class LedgerEntry(SQLModel, table=True):
    __tablename__ = "ledger_entry"
    id: str = Field(primary_key=True)
    account: str
    delta_paise: int
    balance_after_paise: int
    ref: str
    ts: str


class Mission(SQLModel, table=True):
    __tablename__ = "mission"
    id: str = Field(primary_key=True)
    objective: str
    intent_token: Optional[str] = Field(default=None)
    plan_hash: Optional[str] = Field(default=None)
    merkle_root: Optional[str] = Field(default=None)
    status: str = Field(default="INITIALIZED")
    sealed_at: Optional[str] = Field(default=None)


class Delegation(SQLModel, table=True):
    __tablename__ = "delegation"
    id: str = Field(primary_key=True)
    mission_id: str
    parent_agent: str
    child_agent: str
    capabilities: str  # JSON list of string tool names
    ceiling_paise: int = Field(default=0)
    payee_scope: str  # JSON list of string account numbers
    grant_ref: Optional[str] = Field(default=None)
    signature: Optional[str] = Field(default=None)


class Decision(SQLModel, table=True):
    __tablename__ = "decision"
    id: str = Field(primary_key=True)
    mission_id: str
    agent_id: str
    tool: str
    params: str  # JSON dict
    verdict: str  # ALLOW | HOLD | BLOCK
    reason: str
    proof: str = Field(default="{}")  # JSON dict
    ts: str


class APRecord(SQLModel, table=True):
    __tablename__ = "ap_record"
    id: str = Field(primary_key=True)
    invoice_id: str
    outcome: str
    note: str
    ts: str


class ScenarioMetadata(SQLModel, table=True):
    __tablename__ = "scenario_metadata"
    scenario_id: str = Field(primary_key=True)
    status: str = Field(default="CFO_SETUP")  # CFO_SETUP | SEALED | EXECUTED
    objective: str = Field(default="Autonomous Procure-to-Pay Run")
    per_invoice_ceiling_paise: int = Field(default=5000000)
    mission_ceiling_paise: int = Field(default=30000000)
    plan_hash: Optional[str] = Field(default=None)
    intent_token: Optional[str] = Field(default=None)
    sealed_at: Optional[str] = Field(default=None)
    created_at: str

