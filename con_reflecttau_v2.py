import currency as tau

I = importlib

action_interface = [I.Func('execute', args=('payload', 'caller'))]

metadata = Hash()
balances = Hash(default_value=0.0)

total_supply = Variable()
swap_end_date = Variable()

burn_address = Variable()
contract = Variable()

@construct
def init():
    balances[ctx.caller] = 0

    metadata['action_reflection'] = 'con_reflecttau_v2_reflection'
    metadata['action_liquidity'] = 'con_reflecttau_v2_liquidity'
    metadata['action_treasury'] = 'con_reflecttau_v2_treasury'
    metadata['action_buyback'] = 'con_reflecttau_v2_buyback'
    metadata['action_dev'] = 'con_reflecttau_v2_developer'

    metadata['token_name'] = "ReflectTAU.io"
    metadata['token_symbol'] = "RTAU"

    # TODO: Set real addresses
    metadata['operators'] = [
        'ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d',
        'ff61544ea94eaaeb5df08ed863c4a938e9129aba6ceee5f31b6681bdede11b89',
        'TODO'
    ]

    total_supply.set(0.0)
    burn_address.set('reflecttau_burn_address')
    swap_end_date.set(now + datetime.timedelta(days=180))
    contract.set("con_reflecttau_v2")

@export
def change_metadata(key: str, value: Any):
    assert ctx.caller in metadata['operators'], 'Only executable by operators!'

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
        # Since all operators agree, set new value
        metadata[key] = value

        """
        Since agreement was met and the value set,
        let's set each individual agreement to a
        different value so that one-time agreements
        can't be set immediately again by one operator
        """
        for op in metadata['operators']:
            metadata[key][op] = hashlib.sha256(str(now))

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
        metadata[agreement] = ''

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
    return contract.get()

@export
def burn_address():
    return burn_address.get()

# TODO: Can we get rid of this? not really, its used
@export
def add_balance_to_reflect_action(amount: float):
    assert ctx.caller == metadata['action_reflection'], 'You are not allowed to do that'
    balances[metadata['action_reflection']] += amount

@export
def transfer(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'
    assert balances[ctx.caller] >= amount, 'Not enough coins to send!'

    balances[ctx.caller] -= amount
    balances[to] += execute('action_reflection', {'function': 'transfer', 'amount': amount, 'to': to})

@export
def approve(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'
    balances[ctx.caller, to] += amount

@export
def transfer_from(amount: float, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative balances!'
    assert balances[main_account, ctx.caller] >= amount, f'You approved {balances[main_account, ctx.caller]} but need {amount}'
    assert balances[main_account] >= amount, 'Not enough coins to send! '

    balances[main_account, ctx.caller] -= amount
    balances[main_account] -= amount
    balances[to] += execute('action_reflection', {'function': 'transfer_from', 'amount': amount, 'to': to, 'main_account': main_account})

def execute(action: str, payload: dict):
    assert metadata[action] is not None, 'Invalid action!'
    return I.import_module(metadata[action]).execute(payload, ctx.caller)

@export
def external_execute(action: str, payload: dict):
    return execute(action, payload)

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

    execute('action_reflection', {'function': 'add_to_holders_index', 'address': ctx.caller})

@export
def swap_rtau(rtau_amount: float):
    assert now < swap_end_date.get(), 'Swap period ended'
    assert rtau_amount > 0, 'Cannot swap negative balances!'

    I.import_module('con_reflecttau').transfer_from(
        main_account=ctx.caller, 
        amount=rtau_amount, 
        to=burn_address.get())

    # TODO: Set correct swap factor
    swap_amount = rtau_amount / 10000
    total_supply.set(total_supply.get() + swap_amount)
    balances[ctx.caller] += swap_amount

    execute('action_reflection', {'function': 'add_to_holders_index', 'address': ctx.caller})

@export
def time_until_swap_end():
    return swap_end_date.get() - now

@export
def circulating_supply():
    return total_supply.get() - balances[burn_address.get()]

@export
def total_supply():
    return total_supply.get()
