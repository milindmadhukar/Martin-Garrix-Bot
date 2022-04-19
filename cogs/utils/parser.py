def parse_amount(amount: str, other_quantity: int):
    if amount.isnumeric():
        return int(amount)
    elif amount == 'all':
        return other_quantity
    elif amount == 'half':
        return other_quantity // 2