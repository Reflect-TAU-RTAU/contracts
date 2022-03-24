import currency as tau
import con_reflecttau_v2 as save
import con_rocketswap_official_v1_1 as rswp

RTAU_CONTRACT = 'con_reflecttau_v2'

@export
def execute(payload: dict, caller: str):
	assert ctx.caller == RTAU_CONTRACT, 'You are not allowed to do that'
	return buyback_and_burn()

def buyback_and_burn():
	save_amount = rswp.buy(contract=RTAU_CONTRACT, amount=int(tau.balance_of(ctx.this)))
	save.transfer(int(save.balance_of(ctx.this)), 'internal_save_burn')
	return save_amount