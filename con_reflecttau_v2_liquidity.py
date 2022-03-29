import currency as tau
import con_reflecttau_v2 as rtau
import con_rocketswap_official_v1_1 as rswp

metadata = Hash()

contract = Variable()

@construct
def init():
    # TODO: Make this a variable?
    metadata['is_initial_liq_ready'] = False
    # TODO: Remove rswp import and only use metadata['dex']
    metadata['dex'] = 'con_rocketswap_official_v1_1'

    contract.set("con_reflecttau_v2_liquidity")

    approve()

@export
def approve():
    # Approve sending unlimited amount of TAU to DEX contract
    tau.approve(amount=999_999_999_999_999_999, to=metadata['dex'])
    # Approve sending unlimited amount of RTAU to DEX contract
    rtau.approve(amount=999_999_999_999_999_999, to=metadata['dex'])

@export
def metadata(key: str):
    return metadata[key]

@export
def execute(payload: dict, caller: str):
    assert ctx.caller == rtau.contract(), 'You are not allowed to do that'

    if payload['function'] == 'withdraw_tau':
        key = f"{contract.get()}:{payload['function']}:{payload['amount']}:{payload['to']}"
        rtau.assert_operators_agree(agreement=key)
        return withdraw_tau(payload['amount'], payload['to'])

    if payload['function'] == 'withdraw_rtau':
        key = f"{contract.get()}:{payload['function']}:{payload['amount']}:{payload['to']}"
        rtau.assert_operators_agree(agreement=key)
        return withdraw_rtau(payload['amount'], payload['to'])

    if payload['function'] == 'transfer_liquidity':
        key = f"{contract.get()}:{payload['function']}:{payload['amount']}:{payload['to']}"
        rtau.assert_operators_agree(agreement=key)
        return transfer_liquidity(payload['amount'], payload['to'])

    if payload['function'] == 'remove_liquidity':
        key = f"{contract.get()}:{payload['function']}:{payload['amount']}"
        rtau.assert_operators_agree(agreement=key)
        return withdraw_rtau(payload['amount'])

@export
def deposit_tau(amount: float):
    tau.transfer_from(amount=amount, to=contract.get(), main_account=ctx.caller)

@export
def deposit_rtau(amount: float):
    rtau.transfer_from(amount=amount, to=contract.get(), main_account=ctx.caller)

def withdraw_tau(amount: float, to: str):
    return tau.transfer(amount=amount, to=to)

def withdraw_rtau(amount: float, to: str):
    return rtau.transfer(amount=amount, to=to)

@export
def create_market(tau_amount: float, token_amount: float):
    assert_caller_is_operator()

    metadata['is_initial_liq_ready'] = True
    rswp.create_market(contract=rtau.contract(), currency_amount=tau_amount, token_amount=token_amount)

@export
def add_liquidity():
    assert_caller_is_operator()

    rswp_prices = ForeignHash(foreign_contract=metadata['dex'], foreign_name='prices')
    
    rtau_price = rswp_prices[rtau.contract()]
    
    tau_balance = int(tau.balance_of(contract.get()))
    rtau_balance = int(rtau.balance_of(contract.get()))
    rtau_amount = int(tau_balance / rtau_price) + 1

    if rtau_balance > rtau_amount:
        result = rswp.add_liquidity(contract=rtau.contract(), currency_amount=tau_balance)
    
    else:
        tau_amount = rtau_balance * rtau_price
        # TODO: Needed?
        rtau_amount = int(tau_amount / rtau_price) + 1
        
        result = rswp.add_liquidity(contract=rtau.contract(), currency_amount=tau_amount)

    return result

def remove_liquidity(amount: float):
    return rswp.remove_liquidity(contract=rtau.contract(), amount=amount)

def transfer_liquidity(amount: float, to: str):
    return rswp.transfer_liquidity(contract=rtau.contract(), to=to, amount=amount)

def assert_caller_is_operator():
    assert ctx.caller in rtau.metadata('operators'), 'Only executable by operators!'
