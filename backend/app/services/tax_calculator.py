from decimal import Decimal, ROUND_HALF_UP
from typing import Dict
## Define tax rates for each province/territory in Canada
PROVINCE_TAX_RATES : Dict[str, Decimal] = {
    "ON": Decimal("0.13"),
    "QC": Decimal("0.15"),
    "NS": Decimal("0.15"),
    "NB": Decimal("0.15"),
    "MB": Decimal("0.12"),
    "BC": Decimal("0.12"),
    "PE": Decimal("0.15"),
    "SK": Decimal("0.11"),
    "AB": Decimal("0.05"),
    "NL": Decimal("0.15"),
    "NT": Decimal("0.05"),
    "YT": Decimal("0.05"),
    "NU": Decimal("0.05"),
}

two_places = Decimal('0.01')
def calculate_money(value: Decimal) -> Decimal:
    return value.quantize(two_places, rounding=ROUND_HALF_UP)

def get_tax_rate(province: str) -> Decimal:
    code = province.strip().upper()
    return PROVINCE_TAX_RATES.get(code, Decimal("0.05"))

def calculate_tax(taxable_amount: Decimal, province: str) -> tuple[Decimal, Decimal]:
    tax_rate = get_tax_rate(province)
    tax = calculate_money(taxable_amount * tax_rate)
    return tax_rate, tax