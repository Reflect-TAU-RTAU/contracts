
import currency as tau
import con_reflecttau_v2 as rtau

I = importlib

metadata = Hash()
reflections = Hash(default_value=0.0)
forward_holders_index = Hash(default_value=False)
reverse_holders_index = Hash(default_value=False)

contract = Variable()
holders_amount = Variable()

@construct
def init(name: str):
    metadata['tax'] = decimal(12)
    metadata['tau_pool'] = decimal(0)
    metadata['balance_limit'] = decimal(1_000)
    metadata['dex'] = 'con_rocketswap_official_v1_1'

    # Rewards
    metadata['redistribute_perc'] = 66.67
    # Team
    metadata['dev_perc_of_tax'] = 16.67
    # Buyback and Burn
    metadata['buyback_perc_of_tax'] = 8.33
    # Auto-LP
    metadata['autolp_perc_of_tax'] = 8.33

    contract.set(name)
    holders_amount.set(0)

    approve()

@export
def approve():
    # Approve sending unlimited amount of TAU to developer action core contract for dev fees
    tau.approve(amount=999_999_999_999_999_999, to=rtau.get_metadata('action_dev'))
    # Approve sending unlimited amount of RTAU to DEX contract to be able to sell RTAU
    rtau.approve(amount=999_999_999_999_999_999, to=metadata['dex'])

@export
def change_metadata(key: str, value: Any):
    rtau.assert_signer_is_operator()
    metadata[key] = value

@export
def execute(payload: dict, caller: str):
    assert ctx.caller == rtau.contract(), 'You are not allowed to do that'

    if payload['function'] == 'transfer':
        assert not 'external' in payload, 'External call not allowed!'
        return process_transfer(payload['amount'], payload['to'], caller)

    if payload['function'] == 'transfer_from':
        assert not 'external' in payload, 'External call not allowed!'
        return process_transfer(payload['amount'], payload['to'], caller, payload['main_account'])
    
    if payload['function'] == 'manage_holders_index':
        assert not 'external' in payload, 'External call not allowed!'
        manage_holders_index(payload['address'], payload['amount'])

    if payload['function'] == 'redistribute_tau':
        return redistribute_tau(payload['start'], payload['end'], payload['reset_pool'])

    if payload['function'] == 'calc_taxes':
        return calc_taxes(payload['amount'], payload['to'])

def process_transfer(amount: float, to: str, caller: str, main_account: str=""):
    tax = calc_taxes(amount, to)

    # DEX Buy
    if (caller == metadata['dex'] and to != contract.get() and main_account == ""):
        amount -= process_taxes(tax)

        manage_holders_index(to, rtau.balance_of(to))

    # DEX Sell
    elif (to == metadata['dex'] and ctx.signer == main_account and ctx.caller != rtau.get_metadata('action_liquidity')):
        amount -= process_taxes(tax)

        manage_holders_index(main_account, rtau.balance_of(main_account))
    
    # Normal Transfer (not transfer_from, here they dont include a sender so we use signer)
    elif (not to.startswith('con_') and not main_account.startswith('con_')):

        manage_holders_index(to, rtau.balance_of(to) + amount)
        manage_holders_index(ctx.signer, rtau.balance_of(ctx.signer))
                
    return amount

def calc_taxes(amount: float, to: str):
    if to in (rtau.get_metadata('action_liquidity'), rtau.get_metadata('action_buyback'), rtau.burn_address()):
        return decimal(0)

    return amount / 100 * metadata['tax']

def process_taxes(taxes: float):
    if taxes > 0:
        rswp = I.import_module(metadata['dex']) 
        tau_amount = rswp.sell(contract=rtau.contract(), token_amount=taxes)
        
        tau.transfer(amount=(tau_amount / 100 * metadata['dev_perc_of_tax']), to=rtau.get_metadata('action_dev'))
        tau.transfer(amount=(tau_amount / 100 * metadata['buyback_perc_of_tax']), to=rtau.get_metadata('action_buyback'))
        tau.transfer(amount=(tau_amount / 100 * metadata['autolp_perc_of_tax']), to=rtau.get_metadata('action_liquidity'))

        metadata['tau_pool'] += (tau_amount / 100 * metadata['redistribute_perc'])

    return taxes

def manage_holders_index(address: str, amount: float):
    if amount >= metadata['balance_limit']:
        # Add to holders index and be eligible for TAU reflection
        if (reverse_holders_index[address] == False):
            holders_amount.set(holders_amount.get() + 1)
            forward_holders_index[holders_amount.get()] = address
            reverse_holders_index[address] = holders_amount.get()
    else:
        # Remove from holders index and not be eligible for TAU reflection
        if (reverse_holders_index[address] != False):
            forward_holders_index[reverse_holders_index[address]] = False
            reverse_holders_index[address] = False

def redistribute_tau(start: int=None, end: int=None, reset_pool: bool=None):
    if start == None:
        start = 1

    if end == None:
        end = holders_amount.get() + 1

    if reset_pool == None:
        reset_pool = True

    supply = rtau.circulating_supply() - rtau.balance_of(metadata['dex'])

    for holder_id in range(start, end):
        if (forward_holders_index[holder_id] != False):
            holder_balance_share = rtau.balance_of(address=forward_holders_index[holder_id]) / supply * 100
            reflections[forward_holders_index[holder_id]] += metadata["tau_pool"] / 100 * holder_balance_share

    if reset_pool:
        metadata['tau_pool'] = decimal(0)

@export
def claim_tau():
    assert reflections[ctx.caller] > 0, "There is nothing to claim"
    tau.transfer(amount=reflections[ctx.caller], to=ctx.caller)
    reflections[ctx.caller] = decimal(0)
