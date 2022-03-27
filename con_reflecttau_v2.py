import currency as tau

I = importlib

action_interface = [I.Func('execute', args=('payload', 'caller'))]

metadata = Hash()
balances = Hash(default_value=0.0)

total_supply = Variable()
swap_end_date = Variable()

burn_address = Variable()

@construct
def init():
    balances[ctx.caller] = 0

    metadata['action_reflection'] = 'con_reflecttau_v2_reflection'
    metadata['action_liquidity'] = 'con_reflecttau_v2_liquidity'
    metadata['action_treasury'] = 'con_reflecttau_v2_treasury'
    metadata['action_buyback'] = 'con_reflecttau_v2_buyback'
    metadata['action_dev'] = 'con_reflecttau_v2_developer'

    # TODO: Not needed
    metadata['tax'] = 2
    # TODO: Not needed
    metadata['tau_tax_threshold'] = 2
    metadata['token_name'] = "ReflectTAU.io"
    metadata['token_symbol'] = "RTAU"

    # TODO: Set real addresses
    metadata['operators'] = [
        'ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d',
        '6a9004cbc570592c21879e5ee319c754b9b7bf0278878b1cc21ac87eed0ee38d',
        'TODO'
    ]

    total_supply.set(0.0)
    burn_address.set('reflecttau_burn')
    swap_end_date.set(now + datetime.timedelta(days=180))

@export
def change_metadata(key: str, value: Any):
    assert ctx.caller in metadata['operators'], 'Only executable by operators!'
    assert key.lower() != 'operators', 'Can not change owners'
    assert value, 'Parameter "value" can not be empty'

    """
    If it is an action core contract, make sure that the
    contract exists and follows the agreed on interface
    """
    if isinstance(value, str) and value.startswith('action_'):
        con = I.import_module(value)

        error = 'Action contract does not follow the correct interface!'
        assert I.enforce_interface(con, action_interface), error

    """
    Save key and value for an operator. It's not globally
    set yet. Just temporarily saved for the current operator
    """
    metadata[key][ctx.caller] = value

    agreed = None

    # Check if all operators agree on the same value for the key
    for op in metadata['operators']:
        if metadata[key][op] != metadata[key][ctx.caller]:
            agreed = False
            break

    if agreed:
        # Finally set the value for the key
        metadata[key] = value

        """
        Since agreement was met and the value set,
        let's set each individual agreement to a
        different value so that one-time agreements
        can't be set immediately again by one operator
        """
        for op in metadata['operators']:
            metadata[key][op] = op

        return f'{key} = {value}'

@export
def assert_operators_agree(agreement: str, one_time: bool=True):
    """
    Operators can agree to specific action core executions.
    The agreements will then be checked in the action core
    contract before they execute.

    The agreement keys need to have the following form:
    <action_contract>:<function>:<arg_1>:<arg_2>:...

    The value needs to be: "agreed"

    If it is a 'one_time' agreement, it will be set to an
    empty string after checking, to not allow execution
    again without a new agreement from all operators.
    """
    assert metadata[agreement] == 'agreed', 'No agreement met!'

    if one_time:
        metadata[key] = ''

@export
def balance_of(address: str):
    return balances[address]

@export
def allowance(owner: str, spender: str):
    return balances[owner, spender]

@export
def metadata(key: str):
    return metadata[key]

@export
def contract():
    return ctx.this

@export
def burn_address():
    return burn_address.get()

# TODO: Can we get rid of this?
@export
def add_balance_to_reflect_action(amount: float):
    assert ctx.caller == metadata['action_reflection'], 'You are not allowed to do that'
    balances[metadata['action_reflection']] += amount

# TODO: Still needed?
def transfer_internal(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'
    assert balances[ctx.this] >= amount, 'Not enough coins to send!'

    balances[ctx.this] -= amount
    balances[to] += amount

@export
def transfer(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'
    assert balances[ctx.caller] >= amount, 'Not enough coins to send!'

    balances[ctx.caller] -= amount
    balances[to] += execute(metadata['action_reflection'], {'function': 'transfer', 'amount': amount, 'to': to})

@export
def approve(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'
    balances[ctx.caller, to] += amount

@export
def transfer_from(amount: float, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative balances!'
    assert balances[main_account, ctx.caller] >= amount, f'You approved {balances[main_account, ctx.caller]} but need {amount}'
    assert balances[main_account] >= amount, 'Not enough coins to send!'

    balances[main_account, ctx.caller] -= amount
    balances[main_account] -= amount
    balances[to] += execute(metadata['action_reflection'], {'function': 'transfer_from', 'amount': amount, 'to': to, 'main_account': main_account})

# TODO: Needs to be completely reworked
def pay_tax(amount: float):
    tax_amount = amount / 100 * metadata['tax']

    if tax_amount > 0:
        prices = ForeignHash(
            foreign_contract=metadata['dex'], 
            foreign_name='prices')

        if not prices[ctx.this]:
            return

        tau_tax = tax_amount * prices[ctx.this]
        tau_balance = tau.balance_of(ctx.signer)

        missing = tau_tax - tau_balance
        error = f'Not enough TAU to pay tax. Missing {missing} TAU'
        assert tau_balance >= tau_tax, error

        # TAU tax
        tau.transfer_from(
            main_account=ctx.signer, 
            amount=tau_tax, 
            to=ctx.this)

        missing = tax_amount - balances[ctx.signer]
        error = f'Not enough {metadata["token_symbol"]} to pay tax. Missing {missing} {metadata["token_symbol"]}'
        assert balances[ctx.signer] >= tax_amount, error

        # SAVE tax
        balances[ctx.this] += tax_amount
        balances[ctx.signer] -= tax_amount

# TODO: Needs to be completely reworked
@export
def disperse_funds():
    """
    50% TAU --> liquidity
    25% TAU --> buyback & burn
    25% TAU --> treasury

    50% SAVE --> liquidity
    25% SAVE --> staking
    25% SAVE --> devs
    """

    assert actions['liquidity'], 'No action set for "liquidity"'
    assert actions['buyback'], 'No action set for "buyback"'
    assert actions['treasury'], 'No action set for "treasury"'
    assert actions['staking'], 'No action set for "staking"'

    tau_balance = int(tau.balance_of(ctx.this))

    if tau_balance < metadata['tau_tax_threshold']:
        return

    # TAU Liquidity
    tau_liq_share = tau_balance / 2
    tau.transfer(tau_liq_share, actions['liquidity'])
    tau_balance -= tau_liq_share

    # TAU Buyback & Burn
    tau_buyback_share = tau_balance / 2
    tau.transfer(tau_buyback_share, actions['buyback'])
    tau_balance -= tau_buyback_share    

    # TAU Treasury
    tau.transfer(tau_balance, actions['treasury'])

    save_balance = int(balances[ctx.this])

    save_liq_share = save_balance / 2
    save_balance -= save_liq_share

    # SAVE Liquidity
    transfer_internal(save_liq_share, actions['liquidity'])

    save_staking_share = save_balance / 2
    save_balance -= save_staking_share

    # SAVE Staking
    transfer_internal(save_staking_share, actions['staking'])

    # SAVE Dev funds
    transfer_internal(save_balance, actions['treasury'])

@export
def execute(action: str, payload: dict):
    assert metadata[action] is not None, 'Invalid action!' # Invalid Action Error here is that action = con_reflecttau_v2_reflection on transfer() but the action is actually called action_reflection (not contract name)
    return I.import_module(metadata[action]).execute(payload, ctx.caller)

@export
def swap_basic(basic_amount: float):
    assert now < swap_end_date.get(), 'Swap period ended'
    assert basic_amount > 0, 'Cannot swap negative balances!'

    I.import_module('con_doug_lst001').transfer_from(
        main_account=ctx.caller, 
        amount=basic_amount, 
        to=burn_address.get())

    swap_amount = basic_amount / 100
    total_supply.set(total_supply.get() + swap_amount)
    balances[ctx.caller] += swap_amount

# TODO: What's the swap factor?
@export
def swap_rtau(rtau_amount: float):
    assert now < swap_end_date.get(), 'Swap period ended'
    assert rtau_amount > 0, 'Cannot swap negative balances!'

    I.import_module('con_reflecttau').transfer_from(
        main_account=ctx.caller, 
        amount=rtau_amount, 
        to=burn_address.get())

    swap_amount = rtau_amount / 10000
    total_supply.set(total_supply.get() + swap_amount)
    balances[ctx.caller] += swap_amount

@export
def time_until_swap_end():
    return swap_end_date.get() - now

@export
def circulating_supply():
    return total_supply.get() - balances[burn_address.get()]

@export
def total_supply():
    return total_supply.get()
