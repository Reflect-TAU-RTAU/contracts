# TODO: Needed?
import currency as tau
import con_reflecttau_v2 as rtau
# TODO: Needed?
import con_rocketswap_official_v1_1 as rswp

forward_holders_index = Hash(default_value=False)
reverse_holders_index = Hash(default_value=False)

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

    i = 1
    for op in rtau.metadata['operators']:
        forward_holders_index[i] = op
        reverse_holders_index[op] = i
        holders_amount.set(i)
        i += 1

@export
def execute(payload: dict, caller: str):
    assert ctx.caller == RTAU_CONTRACT, 'You are not allowed to do that'

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

        if (balances[main_account] > 1000000):
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
	# TODO: Both methods make a sell. Needs to be one sell and then the TAU splitted
    pay_dev_fee(amount=taxes)
    pay_redistribute_tau(amount=taxes)

    balances[con_rtau] += taxes
    
    return taxes

# TODO: Needs to be rewritten to allow settings RTAU balance from outside of token contract
def pay_dev_fee(amount: float):
    tokens_for_dev = amount / 100 * metadata['dev_perc_of_tax']
    
    balances[con_rtau, metadata['dex']] += tokens_for_dev

    currency_amount = I.import_module(metadata['dex']).sell(
        contract=con_rtau, 
        token_amount=tokens_for_dev
    )

	# TODO: Just send to developer action core contract and split later in there
    currency.approve(amount=currency_amount,to=metadata['operator'])
    currency.transfer(amount=currency_amount,to=metadata['operator'])

# TODO: Needs to be rewritten to allow settings RTAU balance from outside of token contract
def pay_redistribute_tau(amount: float):
    tokens_for_ins = amount / 100 * metadata['redistribute_perc']
    balances[con_rtau, metadata['dex']] += tokens_for_ins

    metadata['tau_pool'] += I.import_module(metadata['dex']).sell(
        contract=con_rtau, 
        token_amount=tokens_for_ins
    )

def get_total_supply_without_rocketswap():
    return total_supply.get() - balances[metadata['dex']]

@export
def redistribute_tau(start: int=0, end: int=0, reset_pool: bool=True):
    assert_caller_is_operator()

    if start == 0 and end == 0:
        start = 1
        end = holders_amount.get() + 1

    for holder_id in range(start, end):
        if (forward_holders_index[holder_id] != False):
            reflections[forward_holders_index[holder_id]] += metadata["tau_pool"] / 100 * (balances[forward_holders_index[holder_id]] / get_total_supply_without_rocketswap() * 100)

    if reset_pool:
        metadata['tau_pool'] = decimal(0)

@export
def claim_tau():
    assert reflections[ctx.caller] > 0, "There is nothing to claim"
    currency.transfer(amount=reflections[ctx.caller], to=ctx.caller)
    reflections[ctx.caller] = decimal(0)

