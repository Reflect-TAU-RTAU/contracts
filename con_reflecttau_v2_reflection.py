# TODO: Need to fix issue where users under specific amount of RTAU are not able to sell
# TODO: Make sure that each holder with amount of RTAU gets reflections

import currency as tau
import con_reflecttau_v2 as rtau
import con_rocketswap_official_v1_1 as rswp

I = importlib

metadata = Hash()
reflections = Hash(default_value=0.0)
forward_holders_index = Hash(default_value=False)
reverse_holders_index = Hash(default_value=False)

holders_amount = Variable()

@construct
def init():
    metadata['buy_tax'] = decimal(8)
    metadata['sell_tax'] = decimal(8)
    metadata['redistribute_perc'] = decimal(80)
    metadata['dev_perc_of_tax'] = decimal(20)
    metadata['is_initial_liq_ready'] = False
    metadata['tau_pool'] = decimal(0)
    metadata['dex'] = 'con_rocketswap_official_v1_1'
    metadata['balance_limit'] = decimal(1_000_000)

    holders_amount.set(0)

    approve()

@export
def approve():
    # Approve sending unlimited amount of TAU to developer action core contract for dev fees
    tau.approve(amount=999_999_999_999_999_999, to=rtau.metadata('action_dev'))
    # Approve sending unlimited amount of RTAU to DEX contract to be able to sell RTAU
    rtau.approve(amount=999_999_999_999_999_999, to=metadata['dex'])

@export
def sync_initial_liq_state():
    assert_caller_is_operator()

    ready = I.import_module(rtau.metadata('action_liquidity')).metadata('is_initial_liq_ready')
    metadata['is_initial_liq_ready'] = ready

@export
def execute(payload: dict, caller: str):
    assert ctx.caller == rtau.contract(), 'You are not allowed to do that - rtau.contract() =' + " " + rtau.contract()

    if payload['function'] == 'transfer':
        return process_transfer(payload['amount'], payload['to'], caller)

    if payload['function'] == 'transfer_from':
        return process_transfer(payload['amount'], payload['to'], caller, payload['main_account'])
    
    if payload['function'] == 'add_to_holders_index':
        add_to_holders_index(payload['address'])

def process_transfer(amount: float, to: str, caller: str, main_account: str=""):
    if to == rtau.burn_address():
        return amount

    if metadata['is_initial_liq_ready']:
        # TODO: Set adding / removing from holders index correctly on each transfer?

        # DEX Buy
        if (caller == metadata['dex'] and to != ctx.this and main_account == ""):
            amount -= process_taxes(calc_taxes(amount, "buy"))
            add_to_holders_index(to)

        # DEX Sell
        elif (to==metadata['dex'] and ctx.signer == main_account):
            amount -= process_taxes(calc_taxes(amount, "sell"))

            if (rtau.balance_of(main_account) >= metadata['balance_limit']):
                add_to_holders_index(main_account)
            else:
                remove_from_holders_index(main_account)

    return amount

def calc_taxes(amount: float, trade_type: str):
    if(trade_type == "buy"):
        return amount / 100 * metadata['buy_tax']
    elif(trade_type == "sell"):
        return amount / 100 * metadata['sell_tax']

def process_taxes(taxes: float):
    # TODO: Are we able to send it with 'rtau.transfer()' instead?
    rtau.add_balance_to_reflect_action(amount=taxes)

    tau_amount = rswp.sell(contract=rtau.contract(), token_amount=taxes)
    
    tau.transfer(amount=(tau_amount / 100 * taxes) / 100 * metadata['dev_perc_of_tax'], to=rtau.metadata('action_dev'))
    
    metadata['tau_pool'] += (tau_amount / 100 * taxes) / 100 * metadata['redistribute_perc']

    return taxes

def add_to_holders_index(address: str):
    if (reverse_holders_index[address] == False):
        holders_amount.set(holders_amount.get() + 1)
        forward_holders_index[holders_amount.get()] = address
        reverse_holders_index[address] = holders_amount.get()

def remove_from_holders_index(address: str):
    if (reverse_holders_index[address] != False):
        forward_holders_index[reverse_holders_index] = False
        reverse_holders_index[address] = False

@export
def redistribute_tau(start: int=0, end: int=0, reset_pool: bool=True):
    assert_caller_is_operator()

    # TODO: wtf this is None and not default 0
    if start == None and end == None:
        start = 1
        end = holders_amount.get() + 1

    supply = rtau.circulating_supply() - rtau.balance_of(metadata['dex'])

    for holder_id in range(start, end):
        if (forward_holders_index[holder_id] != False):
            holder_balance_share = rtau.balance_of([forward_holders_index[holder_id]]) / supply * 100
            reflections[forward_holders_index[holder_id]] += metadata["tau_pool"] / 100 * holder_balance_share

    if reset_pool:
        metadata['tau_pool'] = decimal(0)

@export
def claim_tau():
    assert reflections[ctx.caller] > 0, "There is nothing to claim"
    tau.transfer(amount=reflections[ctx.caller], to=ctx.caller)
    reflections[ctx.caller] = decimal(0)

def assert_caller_is_operator():
    assert ctx.caller in rtau.metadata('operators'), 'Only executable by operators!'
