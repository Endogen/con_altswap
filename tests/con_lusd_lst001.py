# LST001
balances = Hash(default_value=0)
# LST002
metadata = Hash()
@construct
def seed():
    # LST002
    metadata['operator'] = ctx.caller
    # operator needs to be the clearinghouse contract
    metadata['owner'] = "con_lamden_link_bsc_v1"
    balances['ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d'] = 10000
# LST002
@export
def change_metadata(key: str, value: Any):
    assert ctx.caller == metadata['operator'], 'Only operator can set metadata!'
    metadata[key] = value
@export
def mint(amount: float, to: str):
    owner = metadata['owner']
    assert ctx.caller == owner, f'Only owner can mint! Current owner is {owner}, Caller is {ctx.caller}'
    assert amount > 0, 'Cannot mint negative balances!'
    balances[to] += amount
# LST001
@export
def transfer(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'
    assert balances[ctx.caller] >= amount, 'Not enough coins to send!'
    balances[ctx.caller] -= amount
    balances[to] += amount
# LST001
@export
def approve(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'
    balances[ctx.caller, to] += amount
# LST001
@export
def transfer_from(amount: float, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative balances!'
    assert balances[main_account, ctx.caller] >= amount, 'Not enough coins approved to send! You have {} and are trying to spend {}'\
        .format(balances[main_account, ctx.caller], amount)
    assert balances[main_account] >= amount, 'Not enough coins to send!'
    balances[main_account, ctx.caller] -= amount
    balances[main_account] -= amount
    balances[to] += amount
