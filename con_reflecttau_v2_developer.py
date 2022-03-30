import currency as tau
import con_reflecttau_v2 as rtau

@export
def execute(payload: dict, caller: str):
	assert ctx.caller == rtau.contract(), 'You are not allowed to do that'

	if payload['function'] == 'distribute_tau_share':
		return distribute_tau_share()
		
	if payload['function'] == 'distribute_rtau_share':
		return distribute_rtau_share()

def distribute_tau_share():
	total_amount = tau.balance_of(ctx.this)
	shareholders = len(rtau.metadata['operators'])
	individual_amount = int(total_amount / shareholders)

	for op in rtau.metadata['operators']:
		tau.transfer(amount, op)

	return f'{individual_amount}'

def distribute_rtau_share():
	total_amount = rtau.balance_of(ctx.this)
	shareholders = len(rtau.metadata['operators'])
	individual_amount = int(total_amount / shareholders)

	for op in rtau.metadata['operators']:
		rtau.transfer(amount, op)

	return f'{individual_amount}'
