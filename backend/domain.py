"""
MANDATE — Domain Logic and DB Access
Handles the real database transactions, including initiate_payment which genuinely mutates the ledger.
"""

import os
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy.pool import NullPool

from backend.models import (
    BankAccount,
    Vendor,
    PurchaseOrder,
    Invoice,
    Payment,
    LedgerEntry,
    Mission,
    Delegation,
    Decision,
    APRecord,
    ScenarioMetadata,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "mandate.db")
SEED_DB_PATH = os.path.join(BASE_DIR, "mandate.seed.db")
SCENARIOS_DIR = os.path.join(BASE_DIR, "data", "scenarios")


def get_scenario_db_path(scenario_id: Optional[str] = None) -> str:
    """Returns the isolated database filepath for a scenario, or the canonical DB_PATH."""
    if not scenario_id or scenario_id == "canonical":
        return DB_PATH
    os.makedirs(SCENARIOS_DIR, exist_ok=True)
    # Sanitize scenario_id to prevent path traversal
    safe_id = "".join(c for c in scenario_id if c.isalnum() or c in ("-", "_"))
    return os.path.join(SCENARIOS_DIR, f"{safe_id}.db")


def get_engine(db_path: str = DB_PATH):
    return create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
    )



def get_session(db_path: str = DB_PATH) -> Session:
    engine = get_engine(db_path)
    return Session(engine)


def init_db(db_path: str = DB_PATH):
    engine = get_engine(db_path)
    SQLModel.metadata.create_all(engine)


def init_scenario_db(
    scenario_id: str,
    objective: str = "Judge Sandbox Procurement Mission",
    opening_balance_paise: int = 425000000,
    per_invoice_ceiling_paise: int = 5000000,
    mission_ceiling_paise: int = 30000000,
) -> str:
    """Initializes an isolated, empty sandbox database for a new judge scenario."""
    scenario_db_path = get_scenario_db_path(scenario_id)
    if os.path.exists(scenario_db_path):
        os.remove(scenario_db_path)

    init_db(scenario_db_path)
    now_iso = datetime.now(timezone.utc).isoformat()

    with get_session(scenario_db_path) as session:
        # Opening Bank Account
        account = BankAccount(
            id="ACC-MANDATE-01",
            holder=f"Mandate Industries Pvt Ltd (Sandbox {scenario_id})",
            balance_paise=opening_balance_paise,
        )
        session.add(account)

        # Opening Ledger Entry
        opening_entry = LedgerEntry(
            id=f"led_open_{scenario_id[:8]}",
            account="ACC-MANDATE-01",
            delta_paise=opening_balance_paise,
            balance_after_paise=opening_balance_paise,
            ref="OPENING_BALANCE",
            ts=now_iso,
        )
        session.add(opening_entry)

        # Scenario Metadata
        meta = ScenarioMetadata(
            scenario_id=scenario_id,
            status="CFO_SETUP",
            objective=objective,
            per_invoice_ceiling_paise=per_invoice_ceiling_paise,
            mission_ceiling_paise=mission_ceiling_paise,
            created_at=now_iso,
        )
        session.add(meta)
        session.commit()

    return scenario_db_path



def domain_list_open_purchase_orders(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    with get_session(db_path) as session:
        statement = select(PurchaseOrder).where(PurchaseOrder.status == "OPEN")
        results = session.exec(statement).all()
        return [po.model_dump() for po in results]


def domain_get_vendor_master(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    with get_session(db_path) as session:
        statement = select(Vendor)
        results = session.exec(statement).all()
        return [v.model_dump() for v in results]


def domain_fetch_invoices(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    with get_session(db_path) as session:
        statement = select(Invoice)
        results = session.exec(statement).all()
        return [inv.model_dump() for inv in results]


def domain_initiate_payment(
    invoice_id: str,
    payee_account: str,
    amount_paise: int,
    decision_id: Optional[str] = None,
    db_path: str = DB_PATH,
) -> Dict[str, Any]:
    """
    Genuine payment execution:
    Debits ACC-MANDATE-01, credits payee, appends LedgerEntry, creates Payment record.
    Must genuinely mutate SQLite DB.
    """
    if amount_paise <= 0:
        raise ValueError(f"Invalid payment amount: {amount_paise} paise")

    with get_session(db_path) as session:
        mandate_acc = session.get(BankAccount, "ACC-MANDATE-01")
        if not mandate_acc:
            raise RuntimeError("Account ACC-MANDATE-01 not found")

        if mandate_acc.balance_paise < amount_paise:
            raise RuntimeError(
                f"Insufficient funds: balance {mandate_acc.balance_paise} paise, requested {amount_paise} paise"
            )

        # Debit Mandate Account
        mandate_acc.balance_paise -= amount_paise
        session.add(mandate_acc)

        # Credit Payee Account if exists
        payee_acc = session.get(BankAccount, payee_account)
        if payee_acc:
            payee_acc.balance_paise += amount_paise
            session.add(payee_acc)

        import uuid
        now_iso = datetime.now(timezone.utc).isoformat()
        u_suffix = uuid.uuid4().hex[:8]

        # Create Payment Record
        payment_id = f"PAY-{invoice_id}-{int(datetime.now(timezone.utc).timestamp()*1000)}-{u_suffix}"
        payment = Payment(
            id=payment_id,
            invoice_id=invoice_id,
            payee_account=payee_account,
            amount_paise=amount_paise,
            status="PAID",
            decision_id=decision_id,
        )
        session.add(payment)

        # Append Ledger Entry
        ledger_id = f"LEDGER-{int(datetime.now(timezone.utc).timestamp()*1000)}-{u_suffix}"

        ledger = LedgerEntry(
            id=ledger_id,
            account="ACC-MANDATE-01",
            delta_paise=-amount_paise,
            balance_after_paise=mandate_acc.balance_paise,
            ref=f"PAY-{invoice_id}",
            ts=now_iso,
        )
        session.add(ledger)

        session.commit()
        session.refresh(mandate_acc)
        session.refresh(payment)
        session.refresh(ledger)

        return {
            "payment_id": payment.id,
            "status": "PAID",
            "amount_paise": amount_paise,
            "payee_account": payee_account,
            "balance_after_paise": mandate_acc.balance_paise,
            "ledger_id": ledger.id,
            "ts": now_iso,
        }


def domain_write_ap_record(
    invoice_id: str,
    outcome: str,
    note: str,
    db_path: str = DB_PATH,
) -> Dict[str, Any]:
    with get_session(db_path) as session:
        now_iso = datetime.now(timezone.utc).isoformat()
        rec_id = f"AP-{invoice_id}"
        existing = session.get(APRecord, rec_id)
        if existing:
            existing.outcome = outcome
            existing.note = note
            existing.ts = now_iso
            session.add(existing)
            record = existing
        else:
            record = APRecord(
                id=rec_id,
                invoice_id=invoice_id,
                outcome=outcome,
                note=note,
                ts=now_iso,
            )
            session.add(record)

        session.commit()
        session.refresh(record)
        return record.model_dump()
