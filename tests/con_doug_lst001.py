balances = Hash(default_value=0)
metadata = Hash()

@construct
def seed():
    balances[
        'ff61544ea94eaaeb5df08ed863c4a938e9129aba6ceee5f31b6681bdede11b89'
        ] = 100000000
    metadata['token_name'] = 'Super Doug Dash'
    metadata['token_symbol'] = 'DOUG'
    metadata['operator'
        ] = 'ff61544ea94eaaeb5df08ed863c4a938e9129aba6ceee5f31b6681bdede11b89'

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
