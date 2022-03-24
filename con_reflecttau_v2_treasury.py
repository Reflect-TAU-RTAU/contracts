I = importlib

import con_rocketswap_official_v1_1 as rswp

RTAU_CONTRACT = 'con_reflecttau_v2'

@export
def execute(payload: dict, caller: str):
	assert ctx.caller == RTAU_CONTRACT, 'You are not allowed to do that'

	if payload['function'] == 'send_token':
		return send_token(payload['contract'], payload['amount'], payload['to'])

	if payload['function'] == 'send_lp':
		return send_lp(payload['contract'], payload['amount'], payload['to'])

def send_token(contract: str, amount: float, to: str):
	return I.import_module(contract).transfer(amount, to)

def send_lp(contract: str, amount: float, to: str):
	return rswp.transfer_liquidity(contract=contract, amount=amount, to=to)
