import currency as tau
import con_reflecttau_v2 as rtau

I = importlib

metadata = Hash()

contract = Variable()
initial_liq_ready = Variable()

@construct
def init():
    metadata['dex'] = 'con_rocketswap_official_v1_1'
    contract.set(rtau.metadata('action_liquidity'))
    initial_liq_ready.set(False)

    approve()

@export
def approve():
    # Approve sending unlimited amount of TAU to DEX contract
    tau.approve(amount=999_999_999_999_999_999, to=metadata['dex'])
    # Approve sending unlimited amount of RTAU to DEX contract
    rtau.approve(amount=999_999_999_999_999_999, to=metadata['dex'])

@export
def change_metadata(key: str, value: Any):
    rtau.assert_signer_is_operator()
    metadata[key] = value

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
    rtau.assert_signer_is_operator()
    initial_liq_ready.set(True)

    rswp = I.import_module(metadata['dex'])
    return rswp.create_market(contract=rtau.contract(), currency_amount=tau_amount, token_amount=token_amount)

@export
def add_liquidity():
    rtau.assert_signer_is_operator()
    
    rswp = I.import_module(metadata['dex'])
    rswp.buy(contract=rtau.contract(), currency_amount=tau.balance_of(contract.get()) / 2)

    rswp_prices = ForeignHash(foreign_contract=metadata['dex'], foreign_name='prices')
    
    rtau_price = rswp_prices[rtau.contract()]
    
    tau_balance = tau.balance_of(contract.get())
    rtau_balance = rtau.balance_of(contract.get())
    rtau_amount = tau_balance / rtau_price

    if rtau_balance > rtau_amount:
        result = rswp.add_liquidity(contract=rtau.contract(), currency_amount=tau_balance)
    
    else:
        tau_amount = rtau_balance * rtau_price
        result = rswp.add_liquidity(contract=rtau.contract(), currency_amount=tau_amount)

    return result

def remove_liquidity(amount: float):
    rswp = I.import_module(metadata['dex'])
    return rswp.remove_liquidity(contract=rtau.contract(), amount=amount)

def transfer_liquidity(amount: float, to: str):
    rswp = I.import_module(metadata['dex'])
    return rswp.transfer_liquidity(contract=rtau.contract(), to=to, amount=amount)
