I = importlib

import con_reflecttau_v2 as rtau
import con_rocketswap_official_v1_1 as rswp

@export
def execute(payload: dict, caller: str):
	assert ctx.caller == rtau.contract(), 'You are not allowed to do that'

	"""
	This is the key that each operator needs to submit into metadata. 
	The value of that key needs to be 'agreed' or otherwise this will fail. 
	"""
	key = f"{ctx.this}:{payload['function']}:{payload['amount']}:{payload['to']}"
	rtau.assert_operators_agree(agreement=key)

	if payload['function'] == 'send_token':
		return send_token(payload['contract'], payload['amount'], payload['to'])

	if payload['function'] == 'send_lp':
		return send_lp(payload['contract'], payload['amount'], payload['to'])

def send_token(token_contract: str, amount: float, to: str):
	return I.import_module(token_contract).transfer(amount=amount, to=to)

def send_lp(token_contract: str, amount: float, to: str):
	return rswp.transfer_liquidity(contract=token_contract, amount=amount, to=to)
