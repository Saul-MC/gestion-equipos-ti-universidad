from datetime import date


def compute_age(purchase_date: date | None) -> int:
    if not purchase_date:
        return 0
    today = date.today()
    return max(0, today.year - purchase_date.year - ((today.month, today.day) < (purchase_date.month, purchase_date.day)))






