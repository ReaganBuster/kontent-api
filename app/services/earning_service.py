from sqlalchemy.orm import Session
from app.models.earning import Earning
from typing import List, Optional
import uuid
from decimal import Decimal
from datetime import datetime
class EarningService:
    def __init__(self, db: Session):
        self.db = db

    def get_earning(self, earning_id: uuid.UUID) -> Optional[Earning]:
        return self.db.query(Earning).filter(Earning.earning_id == earning_id).first()

    def get_earnings_by_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Earning]:
        return self.db.query(Earning).filter(Earning.user_id == user_id).order_by(Earning.created_at.desc()).offset(skip).limit(limit).all()

    def create_earning(self, user_id: uuid.UUID, connection_id: uuid.UUID, amount: Decimal, currency: str = "USD") -> Earning:
        db_earning = Earning(
            user_id=user_id,
            connection_id=connection_id,
            amount=amount,
            currency=currency,
            status="PENDING_PAYOUT"
        )
        self.db.add(db_earning)
        self.db.commit()
        self.db.refresh(db_earning)
        return db_earning

    def update_earning_status(self, earning_id: uuid.UUID, new_status: str, payout_transaction_id: Optional[uuid.UUID] = None) -> Optional[Earning]:
        db_earning = self.db.query(Earning).filter(Earning.earning_id == earning_id).first()
        if db_earning:
            db_earning.status = new_status
            if new_status == "PAID_OUT":
                db_earning.paid_out_at = datetime.utcnow()
                db_earning.payout_transaction_id = payout_transaction_id # Link to the actual payout transaction
            self.db.add(db_earning)
            self.db.commit()
            self.db.refresh(db_earning)
            return db_earning
        return None