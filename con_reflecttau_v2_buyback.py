import currency as tau
import con_reflecttau_v2 as rtau

I = importlib

metadata = Hash()

@construct
def init():
    metadata['dex'] = 'con_rocketswap_official_v1_1'
    approve()

@export
def approve():
    # Approve sending unlimited amount of TAU to DEX contract to be able to buy RTAU
    tau.approve(amount=999_999_999_999_999_999, to=metadata['dex'])

@export
def change_metadata(key: str, value: Any):
    rtau.assert_signer_is_operator()
    metadata[key] = value

@export
def execute(payload: dict, caller: str):
    assert ctx.caller == rtau.contract(), 'You are not allowed to do that'
    return buyback_and_burn()

def buyback_and_burn():
    rswp = I.import_module(metadata['dex'])
    rtau_amount = rswp.buy(contract=rtau.contract(), currency_amount=tau.balance_of(ctx.this))
    rtau.transfer(rtau_amount, rtau.burn_address())
    return rtau_amount
