# TODO: Need to fix issue where users under specific amount of RTAU are not able to sell
# TODO: Make sure that each holder with amount of RTAU gets reflections
# TODO: Make threshold amount of RTAU for reflection adjustable

import currency as tau
import con_reflecttau_v2 as rtau
import con_rocketswap_official_v1_1 as rswp

forward_holders_index = Hash(default_value=False)
reverse_holders_index = Hash(default_value=False)
metadata = Hash()
reflections = Hash(default_value=0.0)

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

    # TODO: This means devs are in the reflection distribution directly?
    # this is only needed if the contract mints supply on deploy
    i = 1
    for op in rtau.metadata['operators']:
        forward_holders_index[i] = op
        reverse_holders_index[op] = i
        holders_amount.set(i)
        i += 1

    # Approve sending unlimited amount of TAU to developer action core contract for dev fees
    tau.approve(amount=999_999_999_999_999_999, to=rtau.metadata('action_dev'))
    # Approve sending unlimited amount of RTAU to DEX contract to be able to sell RTAU
    rtau.approve(amount=999_999_999_999_999_999, to=metadata['dex'])

@export
def execute(payload: dict, caller: str):
    assert ctx.caller == rtau.contract(), 'You are not allowed to do that'
    if payload['function'] == 'transfer':
	    return process_transfer(amount=payload['amount'], to=payload['to'], caller=caller)
    if payload['function'] == 'transfer_from':
	    return process_transfer(amount=payload['amount'], to=payload['to'], caller=caller, main_account=payload['main_account'])

def process_transfer(amount: float, to: str, caller: str, main_account: str=""):
    if (caller == metadata['dex'] and to != rtau.contract() and main_account == "" and metadata['is_initial_liq_ready']):
        amount -= process_taxes(taxes=calc_taxes(amount=amount,trade_type="buy"), trade_type="buy")

        if (reverse_holders_index[to] == False):
            new_holders_amount = holders_amount.get() + 1
            holders_amount.set(new_holders_amount)
            forward_holders_index[new_holders_amount] = to
            reverse_holders_index[to] = new_holders_amount
            
    elif (to==metadata['dex'] and ctx.signer == main_account and metadata['is_initial_liq_ready']):
        amount -= process_taxes(taxes=calc_taxes(amount=amount,trade_type="sell"), trade_type="sell")

        if (rtau.balance_of(main_account) > 1000000):
            if (reverse_holders_index[main_account] == False):
                new_holders_amount = holders_amount.get() + 1
                holders_amount.set(new_holders_amount)
                forward_holders_index[new_holders_amount] = main_account
                reverse_holders_index[main_account] = new_holders_amount
        else:
            if (reverse_holders_index[main_account] != False):
                forward_holders_index[reverse_holders_index] = False
                reverse_holders_index[main_account] = False

    return amount

def calc_taxes(amount: float, trade_type: str):
    if(trade_type == "buy"):
        return amount / 100 * metadata['buy_tax']
    elif(trade_type == "sell"):
        return amount / 100 * metadata['sell_tax']

def process_taxes(taxes: float, trade_type:str):
    # TODO: Are we able to send it with 'rtau.transfer()' instead?
    rtau.add_balance_to_reflect_action(taxes)

    tokens_for_dev = taxes / 100 * metadata['dev_perc_of_tax']
    tokens_for_ins = taxes / 100 * metadata['redistribute_perc']
    
    tau_amount = rswp.sell(contract=rtau.contract(), token_amount=(tokens_for_dev + tokens_for_ins))
    
    tau.transfer(amount=(tau_amount / 100 * taxes) / 100 * metadata['dev_perc_of_tax'], to=rtau.metadata('action_dev'))
    
    metadata['tau_pool'] += (tau_amount / 100 * taxes) / 100 * metadata['redistribute_perc']

    return taxes

@export
def redistribute_tau(start: int=0, end: int=0, reset_pool: bool=True):
    assert_caller_is_operator()

    if start == 0 and end == 0:
        start = 1
        end = holders_amount.get() + 1

    # TODO: Don't we want to use 'rtau.circulating_supply()' here?
    supply = rtau.total_supply() - rtau.balance_of(metadata['dex'])
    holder_balance_share = rtau.balance_of([forward_holders_index[holder_id]]) / supply * 100

    for holder_id in range(start, end):
        if (forward_holders_index[holder_id] != False):
            reflections[forward_holders_index[holder_id]] += metadata["tau_pool"] / 100 * holder_balance_share

    if reset_pool:
        metadata['tau_pool'] = decimal(0)

@export
def claim_tau():
    assert reflections[ctx.caller] > 0, "There is nothing to claim"
    tau.transfer(amount=reflections[ctx.caller], to=ctx.caller)
    reflections[ctx.caller] = decimal(0)

