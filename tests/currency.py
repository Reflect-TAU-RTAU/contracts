balances = Hash(default_value=0)

@construct
def seed():
    balances['a5565739151e6f8d3fbb03ab605a31cc285e36a717a95002a60e6e4d4e4fa411'] = 1000000000
    balances['hax'] = 5455
    balances['test'] = 1111

@export
def transfer(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'

    sender = ctx.caller

    assert balances[sender] >= amount, 'Not enough coins to send! ' + ctx.caller

    balances[sender] -= amount
    balances[to] += amount

@export
def balance_of(account: str):
    return balances[account]

@export
def allowance(owner: str, spender: str):
    return balances[owner, spender]

@export
def approve(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'

    sender = ctx.caller
    balances[sender, to] += amount
    return balances[sender, to]

@export
def transfer_from(amount: float, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative balances!'

    sender = ctx.caller

    assert balances[main_account, sender] >= amount, 'Not enough coins approved to send! You have {} and are trying to spend {}'\
        .format(balances[main_account, sender], amount)
    assert balances[main_account] >= amount, 'Not enough coins to send! ' + main_account

    balances[main_account, sender] -= amount
    balances[main_account] -= amount

    balances[to] += amount