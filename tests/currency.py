balances = Hash(default_value=0)

@construct
def seed():
    balances['ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d'] = 10000

@export
def transfer(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'

    sender = ctx.caller

    assert balances[sender] >= amount, 'Not enough coins to send! ' + ctx.caller

    balances[sender] -= amount
    balances[to] += amount

@export
def balance_of(account: str):
    return balances[account]

@export
def allowance(owner: str, spender: str):
    return balances[owner, spender]

@export
def approve(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'

    sender = ctx.caller
    balances[sender, to] += amount
    return balances[sender, to]

@export
def transfer_from(amount: float, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative balances!'

    sender = ctx.caller

    assert balances[main_account, sender] >= amount, 'Not enough coins approved to send! You have {} and are trying to spend {}'\
        .format(balances[main_account, sender], amount)
    assert balances[main_account] >= amount, 'Not enough coins to send! ' + main_account

    balances[main_account, sender] -= amount
    balances[main_account] -= amount

    balances[to] += amount
