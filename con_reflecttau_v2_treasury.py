I = importlib

import con_reflecttau_v2 as rtau
import con_rocketswap_official_v1_1 as rswp

@construct
def init():
	contract.set(ctx.this)

@export
def execute(payload: dict, caller: str):
	assert ctx.caller == rtau.contract(), 'You are not allowed to do that'

	key = f"{contract.get()}:{payload['function']}:{payload['amount']}:{payload['to']}"
	rtau.assert_operators_agree(agreement=key)

	if payload['function'] == 'withdraw_token':
		return withdraw_token(payload['contract'], payload['amount'], payload['to'])

	if payload['function'] == 'withdraw_lp':
		return withdraw_lp(payload['contract'], payload['amount'], payload['to'])

@export
def deposit_token(token_contract: str, amount: float):
	return I.import_module(token_contract).transfer_from(amount=amount, to=contract.get(), main_account=ctx.caller)

@export
def deposit_lp(token_contract: str, amount: float):
	return rswp.transfer_liquidity_from(contract=token_contract, to=contract.get(), main_account=ctx.caller, amount=amount)

def withdraw_token(token_contract: str, amount: float, to: str):
	return I.import_module(token_contract).transfer(amount=amount, to=to)

def withdraw_lp(token_contract: str, amount: float, to: str):
	return rswp.transfer_liquidity(contract=token_contract, amount=amount, to=to)
