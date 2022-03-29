import currency as tau
import con_reflecttau_v2 as rtau
import con_rocketswap_official_v1_1 as rswp

metadata = Hash()

contract = Variable()

@construct
def init():
	metadata['dex'] = 'con_rocketswap_official_v1_1'

	contract.set(ctx.this)

	approve()

@export
def approve():
    # Approve sending unlimited amount of TAU to DEX contract to be able to buy RTAU
    tau.approve(amount=999_999_999_999_999_999, to=metadata['dex'])

@export
def metadata(key: str):
    return metadata[key]

@export
def execute(payload: dict, caller: str):
	assert ctx.caller == rtau.contract(), 'You are not allowed to do that'
	return buyback_and_burn()

def buyback_and_burn():
	rtau_amount = rswp.buy(contract=rtau.contract(), currency_amount=tau.balance_of(contract.get()))
	rtau.transfer(rtau_amount, rtau.burn_address())
	return rtau_amount