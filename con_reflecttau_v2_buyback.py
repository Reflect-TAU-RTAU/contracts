import currency as tau
import con_reflecttau_v2 as rtau

I = importlib

metadata = Hash()

contract = Variable()

@construct
def init(name: str):
    metadata['dex'] = 'con_rocketswap_official_v1_1'
    contract.set(name)
    approve()

@export
def approve():
    # Approve sending unlimited amount of TAU to DEX contract to be able to buy RTAU
    tau.approve(amount=999_999_999_999_999_999, to=metadata['dex'])
    # Approve sending unlimited amount of RTAU to burn address
    rtau.approve(amount=999_999_999_999_999_999, to=rtau.burn_address())

@export
def change_metadata(key: str, value: Any):
    rtau.assert_signer_is_operator()
    metadata[key] = value

@export
def execute(payload: dict, caller: str):
    assert ctx.caller == rtau.contract(), 'You are not allowed to do that'

    if payload['function'] == 'buyback_and_burn':
        return buyback_and_burn()

def buyback_and_burn():
    rswp = I.import_module(metadata['dex'])
    
    rtau_amount = rswp.buy(contract=rtau.contract(), currency_amount=tau.balance_of(contract.get()))
    rtau.transfer(amount=rtau.balance_of(contract.get()), to=rtau.burn_address())
    return rtau_amount
