import currency as tau
import con_reflecttau_v2 as rtau
import con_rocketswap_official_v1_1 as rswp

RSWP_CONTRACT = 'con_rocketswap_official_v1_1'

@export
def execute(payload: dict, caller: str):
	assert ctx.caller == rtau.contract(), 'You are not allowed to do that'
	return add_liquidity()

def add_liquidity():
	rswp_prices = ForeignHash(foreign_contract=RSWP_CONTRACT, foreign_name='prices')
	
	rtau_price = rswp_prices[rtau.contract()]
	
	tau_balance = int(tau.balance_of(ctx.this))
	rtau_balance = int(rtau.balance_of(ctx.this))
	rtau_amount = int(tau_balance / rtau_price) + 1

	if rtau_balance > rtau_amount:
		tau.approve(amount=tau_balance, to=RSWP_CONTRACT)
		rtau.approve(amount=rtau_amount, to=RSWP_CONTRACT)

		result = rswp.add_liquidity(contract=RTAU_CONTRACT, currency_amount=tau_balance)
	
	else:
		tau_amount = rtau_balance * rtau_price
		rtau_amount = int(tau_amount / rtau_price) + 1
		
		tau.approve(amount=tau_amount, to=RSWP_CONTRACT)
		rtau.approve(amount=rtau_amount, to=RSWP_CONTRACT)
		
		result = rswp.add_liquidity(contract=RTAU_CONTRACT, currency_amount=tau_amount)

	return result
