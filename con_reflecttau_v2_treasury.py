import con_reflecttau_v2 as rtau

I = importlib

metadata = Hash()

contract = Variable()

@construct
def init(name: str):
	metadata['dex'] = 'con_rocketswap_official_v1_1'
	contract.set(name)

@export
def change_metadata(key: str, value: Any):
    rtau.assert_signer_is_operator()
    metadata[key] = value

@export
def execute(payload: dict, caller: str):
	assert ctx.caller == rtau.contract(), 'You are not allowed to do that'

	key = f"{contract.get()}#{payload['function']}#{payload['amount']}#{payload['to']}"
	rtau.assert_operators_agree(agreement=key)

	if payload['function'] == 'withdraw_token':
		return withdraw_token(payload['contract'], payload['amount'], payload['to'])

	if payload['function'] == 'withdraw_lp':
		return withdraw_lp(payload['contract'], payload['amount'], payload['to'])

@export
def deposit_token(token_contract: str, amount: float):
	token = I.import_module(token_contract)
	return token.transfer_from(amount=amount, to=contract.get(), main_account=ctx.caller)

@export
def deposit_lp(token_contract: str, amount: float):
	rswp = I.import_module(metadata['dex'])
	return rswp.transfer_liquidity_from(contract=token_contract, to=contract.get(), main_account=ctx.caller, amount=amount)

def withdraw_token(token_contract: str, amount: float, to: str):
	token = I.import_module(token_contract)
	return token.transfer(amount=amount, to=to)

def withdraw_lp(token_contract: str, amount: float, to: str):
	rswp = I.import_module(metadata['dex'])
	return rswp.transfer_liquidity(contract=token_contract, amount=amount, to=to)
