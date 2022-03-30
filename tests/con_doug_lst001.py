balances = Hash(default_value=0)
metadata = Hash()

@construct
def seed():
    balances[
        'a5565739151e6f8d3fbb03ab605a31cc285e36a717a95002a60e6e4d4e4fa411'
        ] = 100000000
    metadata['token_name'] = 'Super Doug Dash'
    metadata['token_symbol'] = 'DOUG'
    metadata['operator'
        ] = 'a5565739151e6f8d3fbb03ab605a31cc285e36a717a95002a60e6e4d4e4fa411'

@export
def change_metadata(key: str, value: Any):
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'
    metadata[key] = value

@export
def transfer(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'
    assert balances[ctx.caller] >= amount, 'Not enough coins to send!'
    balances[ctx.caller] -= amount
    balances[to] += amount

@export
def approve(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'
    balances[ctx.caller, to] += amount

@export
def transfer_from(amount: float, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative balances!'
    assert balances[main_account, ctx.caller
        ] >= amount, 'Not enough coins approved to send! You have {} and are trying to spend {}'.format(
        balances[main_account, ctx.caller], amount)
    assert balances[main_account] >= amount, 'Not enough coins to send!'
    balances[main_account, ctx.caller] -= amount
    balances[main_account] -= amount
    balances[to] += amount
