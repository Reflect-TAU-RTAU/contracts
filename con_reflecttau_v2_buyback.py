import currency as tau
import con_reflecttau_v2 as rtau
import con_rocketswap_official_v1_1 as rswp

@export
def execute(payload: dict, caller: str):
	assert ctx.caller == rtau.contract(), 'You are not allowed to do that'
	return buyback_and_burn()

# TODO: Do we need to approve sending TAU to rswp?
def buyback_and_burn():
	rtau_amount = rswp.buy(contract=rtau.contract(), amount=tau.balance_of(ctx.this))
	rtau.transfer(rtau_amount, rtau.burn_address())
	return rtau_amount