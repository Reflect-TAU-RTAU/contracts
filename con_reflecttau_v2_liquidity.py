import currency as tau
import con_reflecttau_v2 as rtau
import con_rocketswap_official_v1_1 as rswp

TAU_CONTRACT = 'currency'
RTAU_CONTRACT = 'con_reflecttau_v2'
RSWP_CONTRACT = 'con_rocketswap_official_v1_1'

@export
def execute(payload: dict, caller: str):
	assert ctx.caller == RTAU_CONTRACT, 'You are not allowed to do that'
	add_liquidity()

def add_liquidity():
	rswp_prices = ForeignHash(foreign_contract=RSWP_CONTRACT, foreign_name='prices')
	
	save_price = rswp_prices[RTAU_CONTRACT]
	
	tau_balance = int(tau.balance_of(ctx.this))
	save_balance = int(rtau.balance_of(ctx.this))
	save_amount = int(tau_balance / save_price) + 1

	if save_balance > save_amount:
		tau.approve(amount=tau_balance, to=RSWP_CONTRACT)
		rtau.approve(amount=save_amount, to=RSWP_CONTRACT)

		result = rswp.add_liquidity(contract=RTAU_CONTRACT, currency_amount=tau_balance)
	
	else:
		tau_amount = save_balance * save_price
		save_amount = int(tau_amount / save_price) + 1
		
		tau.approve(amount=tau_amount, to=RSWP_CONTRACT)
		rtau.approve(amount=save_amount, to=RSWP_CONTRACT)
		
		result = rswp.add_liquidity(contract=RTAU_CONTRACT, currency_amount=tau_amount)

	return result
