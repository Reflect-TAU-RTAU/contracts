import con_reflecttau_v2 as save

RTAU_CONTRACT = 'con_reflecttau_v2'

@export
def execute(payload: dict, caller: str):
	assert ctx.caller == RTAU_CONTRACT, 'You are not allowed to do that'
	return withdraw_save(payload['amount'])

def withdraw_save(amount: float):
	return save.transfer(amount, ctx.signer)