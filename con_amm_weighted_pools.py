I = importlib

token_interface = [
    I.Func('transfer', args=('amount', 'to')), 
    I.Func('approve', args=('amount', 'to')), 
    I.Func('transfer_from', args=('amount', 'to', 'main_account'))
]

pools = Hash(default_value=0.0)
lp_tokens = Hash(default_value=0.0)

fee = Variable()
operator = Variable()

@construct
def seed():
    fee.set(0.4)
    operator.set("ff61544ea94eaaeb5df08ed863c4a938e9129aba6ceee5f31b6681bdede11b89")

@export
def createWeightedPool(poolName: str, assets: dict):
    assert not pools[poolName], "A pool with this name already exists"
    
    sum_assets = sum(assets.values())

    for contract, amount in assets.items():
        token = I.import_module(contract)

        assert amount > 0, f"Amount of {contract} need to be more than 0"
        assert I.enforce_interface(token, token_interface), f'Invalid token interface for {contract}!'
        
        token.transfer_from(amount=amount, to=ctx.this, main_account=ctx.caller) 

        pools[poolName, contract] = amount
        pools[poolName, contract, 'init'] = amount
        pools[poolName, contract, 'weight'] = amount / sum_assets

    lp_tokens[poolName] = 100
    lp_tokens[poolName, ctx.caller] = 100

    pools[poolName] = list(assets.keys())

@export
def addLiquidity(poolName: str, assets: dict):
    sum_assets = sum(assets.values())

    for contract, amount in assets.items():
        token = I.import_module(contract)

        assert amount == sum_assets / 100 * (pools[poolName, contract, 'weight'] * 100), f"Amount and weights for {contract} not matching"
        assert I.enforce_interface(token, token_interface), f'Invalid token interface for {contract}!'
        assert amount > 0, f"Amount of {contract} need to be more than 0"

        token.transfer_from(amount=amount, to=ctx.this, main_account=ctx.caller)
        
        pools[poolName, contract] += amount
        sum_assets_init += pools[poolName, contract, 'init']
        
    lp_to_mint = (sum_assets / sum_assets_init) * 100

    lp_tokens[poolName] += lp_to_mint
    lp_tokens[poolName, ctx.caller] += lp_to_mint
    
    return lp_to_mint

@export
def removeLiquidity(poolName: str, amountLPTokens: float):
    assert amountLPTokens <= lp_tokens[poolName, ctx.caller], "You don't own that many LP points"
    assert lp_tokens[poolName] - amountLPTokens > 1, "You need to leave atleast 1 LP point"
    assert amountLPTokens > 0, "Amount needs to be more than 0"
    
    for contract in pools[poolName]:
        amount = pools[poolName, contract] / lp_tokens[poolName] * amountLPTokens
        
        I.import_module(contract).transfer(amount=amount, to=ctx.caller)
        
        pools[poolName, contract] -= amount
        lp_tokens[poolName] -= amountLPTokens
        lp_tokens[poolName, ctx.caller] -= amountLPTokens

@export
def transferLiquidity(poolName: str, amountLPTokens: float, to: str):
    assert amountLPTokens <= lp_tokens[poolName, ctx.caller], "You don't own that many LP points"
    assert amountLPTokens > 0, "Amount needs to be more than 0"

    lp_tokens[poolName, to] += amountLPTokens
    lp_tokens[poolName, ctx.caller] -= amountLPTokens

@export
def approveLiquidity(poolName: str, amountLPTokens: float, main_account: str, to: str):
    assert amountLPTokens <= lp_tokens[poolName, ctx.caller], "You don't own that many LP points"
    assert amountLPTokens > 0, "Amount needs to be more than 0"

    lp_tokens[poolName, ctx.caller, to] += amountLPTokens

@export
def transferLiquidityFrom(poolName: str, amountLPTokens: float, main_account: str, to: str):
    assert amountLPTokens <= lp_tokens[poolName, main_account], "Not enough LP points to send"
    assert lp_tokens[poolName, main_account, to] >= amountLPTokens, "Not enough LP points approved to send"
    assert amountLPTokens > 0, "Amount needs to be more than 0"
    
    lp_tokens[poolName, to] += amountLPTokens
    lp_tokens[poolName, main_account] -= amountLPTokens
    lp_tokens[poolName, main_account, to] -= amountLPTokens

@export
def swap(poolName: str, amountFrom: float, contractFrom: str, contractTo: str):
    assert amountFrom > 0, "Amount needs to be more than 0"

    fee_amount = amountFrom / 100 * fee.get()
    swap_amount = amountFrom - fee_amount
    
    local_balances = [pools[poolName, contractFrom], pools[poolName, contractTo]]
    local_weights = [pools[poolName, contractFrom, 'weight'], pools[poolName, contractTo, 'weight']]

    denominator = local_balances[0] + swap_amount
    base = local_balances[0] / denominator
    exponent = local_weights[0] / local_weights[1]
    power = base ** exponent

    final_amount = local_balances[1] * ((1 - power) if power < 1 else 0)
    
    I.import_module(contractFrom).transfer_from(amount=swap_amount + fee_amount, to=ctx.this, main_account=ctx.caller)
    I.import_module(contractTo).transfer(amount=final_amount, to=ctx.caller)

    pools[poolName, contractFrom] += swap_amount
    pools[poolName, contractTo] -= swap_amount
    
    return final_amount

@export
def adjustFee(feeInPercent: float):
    assert ctx.caller == operator.get(), "Only executable by operator"
    fee.set(feeInPercent)
