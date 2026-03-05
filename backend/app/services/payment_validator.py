import re
from datetime import datetime
from decimal import Decimal
from ..schemas.payment import PaymentProcessRequest

class PaymentValidator:
    # Luhn algorithm implementation for card number validation
    @staticmethod
    def luhn_check(card_number: str) -> bool:
        card_number = card_number.strip()
        digit = [int(d) for d in card_number if d.isdigit()]
        if len(digit) < 13 or len(digit) > 19:
            return False
        total = sum(digit[-1::-2]) + sum(
            (2 * d // 10 + 2 * d % 10) if 2 * d > 9 else 2 * d
            for d in digit[-2::-2]
        )
        return total % 10 == 0

    # Validation steps for payment processing
    @staticmethod
    def validate(req: PaymentProcessRequest) -> tuple[str, str]:
        card = req.payment_info.card_number.strip()
        cvv = req.payment_info.cvv.strip()
        expiry = req.payment_info.expiry.strip()

        # Total amount check
        if req.total <= Decimal("0"):
            return ("declined", "Invalid balance!")
        # Card number check using Luhn method
        if not card.isdigit() or not (13 <= len(card) <= 19) or not PaymentValidator.luhn_check(card):
            return ("declined", "Invalid card number!")
        # CVV must be 3 or 4 digits
        if not cvv.isdigit() or len(cvv) not in (3, 4):
            return ("declined", "Invalid CVV!")
        # Expiry date format check
        if not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", expiry):
            return ("declined", "Invalid expiry date format!")

        month, year = expiry.split("/")
        exp_date = datetime(int("20" + year), int(month), 1)
        now = datetime.now()
        current_month = datetime(now.year, now.month, 1)

        # Expiry date check
        if exp_date < current_month:
            return ("declined", "Card has expired!")

        # All check pass -> return approved
        return ("approved", "Payment approved!")