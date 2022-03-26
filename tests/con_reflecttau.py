# non stamp ballooning
import currency
I = importlib
# LST001
balances = Hash(default_value=0)
forward_holders_index = Hash(default_value=False)
reverse_holders_index = Hash(default_value=False)
holders_amount = Variable()
reflections = Hash(default_value=0.0)
# LST002
metadata = Hash()
total_supply = Variable()
# LST001
# LST002
@construct
def seed():
    
    metadata['rocketswap_contract'] = "con_rocketswap_official_v1_1"
    # LST002
    metadata['token_name'] = "ReflectTAU.io"
    metadata['token_symbol'] = "RTAU"
    metadata['operator'] = ctx.caller
    metadata['buy_tax'] = decimal(8)
    metadata['sell_tax'] = decimal(8) 
    metadata['redistribute_tau_perc'] = decimal(80)
    metadata['dev_perc_of_tax'] = decimal(20)
    metadata['is_initial_liq_ready'] = False
    metadata['tau_pool'] = decimal(0)
    balances[ctx.caller] = 1000000000
    forward_holders_index[1] = ctx.caller
    reverse_holders_index[ctx.caller] = 1
    total_supply.set(1000000000)
    holders_amount.set(1)
    
@export
def balance_of(address: str):
    return balances[address]
    
@export
def allowance(owner: str, spender: str):
    return balances[owner, spender]

# LST002
@export
def change_metadata(key: str, value: Any):
    assert ctx.caller == metadata['operator'
        ], 'Only operator can set metadata!'
    metadata[key] = value

# LST001
@export
def approve(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'
    balances[ctx.caller, to] += amount
    return balances[ctx.caller, to]

def calc_taxes(amount: float, trade_type: str):
    if(trade_type == "buy"):
        return amount/100*metadata['buy_tax']
    elif(trade_type == "sell"):
        return amount/100*metadata['sell_tax']

def process_taxes(taxes: float, trade_type:str):
    balances["con_reflecttau"] += taxes
    pay_fee(amount=taxes)
    return taxes
    
def pay_fee(amount:float):
    rocketswap = I.import_module(metadata['rocketswap_contract'])
    tokens_for_dev = amount/100*metadata['dev_perc_of_tax']
    tokens_for_ins = amount/100*metadata['redistribute_tau_perc']
    total_fees = tokens_for_dev + tokens_for_ins
    balances["con_reflecttau", metadata['rocketswap_contract']] += total_fees
    currency_amount = rocketswap.sell(contract="con_reflecttau",token_amount=total_fees)
    currency.approve(amount=currency_amount/100*amount/100*metadata['dev_perc_of_tax'], to=metadata['operator'])
    currency.transfer(amount=currency_amount/100*amount/100*metadata['dev_perc_of_tax'],to=metadata['operator'])
    metadata['tau_pool'] += currency_amount/100*amount/100*metadata['redistribute_tau_perc'],
    
def processTransferNonStandard(amount: float, to: str, main_account: str=""):
    if(ctx.caller == metadata['rocketswap_contract'] and to != ctx.this and main_account == "" and metadata['is_initial_liq_ready']):
        taxes = process_taxes(taxes=calc_taxes(amount=amount,trade_type="buy"), trade_type="buy")
        amount -= taxes
        if(reverse_holders_index[to] == False):
            new_holders_amount = holders_amount.get() + 1
            holders_amount.set(new_holders_amount)
            forward_holders_index[new_holders_amount] = to
            reverse_holders_index[to] = new_holders_amount
            
       
    elif(to==metadata['rocketswap_contract'] and ctx.signer == main_account and metadata['is_initial_liq_ready']):
        taxes = process_taxes(taxes=calc_taxes(amount=amount,trade_type="sell"), trade_type="sell")
        amount -= taxes
        if(balances[main_account] > 1000000):
            if(reverse_holders_index[main_account] == False):
                new_holders_amount = holders_amount.get() + 1
                holders_amount.set(new_holders_amount)
                forward_holders_index[new_holders_amount] = main_account
                reverse_holders_index[main_account] = new_holders_amount
        else:
            if(reverse_holders_index[main_account] != False):
                forward_holders_index[reverse_holders_index] = False
                reverse_holders_index[main_account] = False
    return amount

def get_total_supply_without_rocketswap():
    return total_supply.get() - balances[metadata['rocketswap_contract']]

@export
def redistribute_tau(start:int, end:int): #limit because global stumps limit can exceed, so we do in batches
    assert ctx.caller == metadata['operator'
        ], 'Only operator redistribute!'
    maximum = holders_amount.get()+1
    if(end > maximum):
        end = holders_amount.get()+1
    for holder_id in range(start, end):
        if(forward_holders_index[holder_id] != False):
            reflections[forward_holders_index[holder_id]] += metadata["tau_pool"]/100*(balances[forward_holders_index[holder_id]]/get_total_supply_without_rocketswap()*100)
    metadata['tau_pool'] = decimal(0)

@export
def claim_tau():
    assert reflections[ctx.caller] > 0, "There is nothing to claim"
    currency.transfer(amount=reflections[ctx.caller],to=ctx.caller)
    reflections[ctx.caller] = decimal(0)

# LST001
@export
def transfer(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'
    sender = ctx.caller
    assert balances[sender] >= amount, 'Not enough coins to send!'
    balances[sender] -= amount
    balances[to] += processTransferNonStandard(amount, to)
    
# LST001
@export
def transfer_from(amount: float, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative balances!'
    sender = ctx.caller
    assert balances[main_account, sender
        ] >= amount, 'Not enough coins approved to send! You have {} and are trying to spend {} ({})'.format(
        balances[main_account, sender], amount, ctx.caller)
    assert balances[main_account] >= amount, 'Not enough coins to send! You have {} and are trying to spend {} ({})'.format(
        balances[main_account], amount, main_account)
    balances[main_account, sender] -= amount
    balances[main_account] -= amount
    balances[to] += processTransferNonStandard(amount, to, main_account)
    
    
        
        