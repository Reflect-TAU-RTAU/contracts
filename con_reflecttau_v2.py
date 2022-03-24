import currency as tau

I = importlib

action_interface = [I.Func('execute', args=('payload', 'caller'))]

actions = Hash()
metadata = Hash()
balances = Hash(default_value=0)

total_supply = Variable()
tax_enabled = Variable()
swap_enabled = Variable()
swap_end_date = Variable()

SWAP_FACTOR = 100
BURN_ADDRESS = 'internal_save_burn'

@construct
def seed():
    balances[ctx.caller] = 10000000000000

    actions['staking'] = 'con_save_staking'
    actions['liquidity'] = 'con_save_liquidity'
    actions['treasury'] = 'con_save_treasury'
    actions['buyback'] = 'con_save_buyback'
    actions['dev'] = 'con_save_dev'

    metadata['tax'] = 2
    metadata['tau_tax_threshold'] = 2
    metadata['dex'] = 'con_rocketswap_official_v1_1'
    metadata['token_name'] = "SAVE Token"
    metadata['token_symbol'] = "SAVE"
    metadata['owner'] = ctx.caller

    total_supply.set(0)

    tax_enabled.set(True)
    swap_enabled.set(True)
    swap_end_date.set(now + datetime.timedelta(days=180))

@export
def change_metadata(key: str, value: Any):
    assert_owner(); metadata[key] = value

@export
def balance_of(address: str):
    return balances[address]

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
    balances[to] += amount

    if tax_enabled.get():
        if ctx.caller == metadata['dex'] or to == metadata['dex']:
            pay_tax(amount)

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
    balances[to] += amount

    if tax_enabled.get():
        if ctx.caller == metadata['dex'] or to == metadata['dex']:
            pay_tax(amount)

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
def register_action(action: str, contract: str):
    assert_owner()
    
    assert actions[action] is None, 'Action already registered!'

    con = I.import_module(contract)

    error = 'Action contract does not follow the correct interface!'
    assert I.enforce_interface(con, action_interface), error

    actions[action] = contract

@export
def unregister_action(action: str):
    assert_owner()
    
    assert actions[action] is not None, 'Action does not exist!'

    actions[action] = None

@export
def execute(action: str, payload: dict):
    assert_owner()

    contract = actions[action]
    assert contract is not None, 'Invalid action!'

    return I.import_module(contract).execute(payload, ctx.caller)

@export
def swap_basic_to_save(basic_amount: float):
    assert now < swap_end_date.get(), 'Swap period ended'
    assert swap_enabled.get() == True, 'Swap currently disabled'
    assert basic_amount > 0, 'Cannot swap negative balances!'

    I.import_module('con_doug_lst001').transfer_from(
        main_account=ctx.caller, 
        amount=basic_amount, 
        to=BURN_ADDRESS)

    swap_amount = basic_amount / SWAP_FACTOR
    total_supply.set(total_supply.get() + swap_amount)
    balances[ctx.caller] += swap_amount

@export
def time_until_swap_end():
    return swap_end_date.get() - now

@export
def tax_enabled(enabled: bool):
    assert_owner(); tax_enabled.set(enabled)

@export
def swap_enabled(enabled: bool):
    assert_owner(); swap_enabled.set(enabled)

@export
def circulating_supply():
    return int(total_supply.get() - balances[BURN_ADDRESS])

@export
def total_supply():
    return int(total_supply.get())

def assert_owner():
    assert ctx.caller == metadata['owner'], 'Only executable by owner!'
