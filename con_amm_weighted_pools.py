I = importlib
token_interface = [I.Func('transfer', args=('amount', 'to')), I.Func(
    'approve', args=('amount', 'to')), I.Func('transfer_from', args=(
    'amount', 'to', 'main_account'))]

pools = Hash(default_value=False)
pools_creation_values = Hash(default_value=False)
pool_weights = Hash(default_value=False)
lp_tokens_users = Hash(default_value=0.0)
lp_tokens_total = Hash(default_value=0.0)
lp_tokens_approvals = Hash(default_value=0.0)

fee = Variable()
operator = Variable()

@construct
def seed():
    fee.set(0.4)
    operator.set("ff61544ea94eaaeb5df08ed863c4a938e9129aba6ceee5f31b6681bdede11b89")

@export
def createWeightedPool(poolName: str, assets: dict, weights: dict):
    # assets {"currency": 2, "con_mineit": 1, "con_lusd_lst001": 1}
    # weigths {"currency":0.5, "con_mineit": 0.25, "con_lusd_lst001":0.25}
    assert pools[poolName] == False, "A pool with this name already exists"
    sum_assets = 0
    for contract, amount in assets.items():
        assert amount > 0, "Amounts need to be more then 0"
        sum_assets += amount
    for contract, amount in assets.items():
        assert amount == sum_assets / 100 * (weights[contract] * 100), "Token Amount and Weights are not matching"
    for contract, amount in assets.items():
        token = I.import_module(contract)
        assert I.enforce_interface(token, token_interface
        ), f'Invalid token interface for {contract}!'
        token.transfer_from(amount=amount, to=ctx.this, main_account=ctx.caller)
        pools[poolName, contract] = amount
        pools_creation_values[poolName, contract] = amount
        pool_weights[poolName, contract] = weights[contract]
    lp_tokens_users[poolName, ctx.caller] = 100
    lp_tokens_total[poolName] = 100

    return poolName


@export
def addLiquidity(poolName: str, assets: dict):
    sum_assets_deposit = 0
    sum_assets = 0
    for contract, amount in assets.items():
        assert amount > 0, "Amounts need to be more then 0"
        sum_assets_deposit += amount
        sum_assets += pools_creation_values[poolName, contract]
    for contract,amount in assets.items():
        assert amount == sum_assets_deposit / 100 * (pool_weights[poolName, contract] * 100), "Token Amount and Weights are not matching"
    for contract, amount in assets.items():
        token = I.import_module(contract)
        assert I.enforce_interface(token, token_interface
        ), f'Invalid token interface for {contract}!'
        token.transfer_from(amount=amount, to=ctx.this, main_account=ctx.caller)
        pools[poolName, contract] += amount
        
    total_lp_points = lp_tokens_total[poolName]
    lp_to_mint = (sum_assets_deposit / sum_assets) * 100
    lp_tokens_total[poolName] += lp_to_mint
    lp_tokens_users[poolName, ctx.caller] += lp_to_mint

    return lp_to_mint


@export
def removeLiquidity(poolName: str, amountLPTokens: float):
    assert amountLPTokens <= lp_tokens_users[poolName, ctx.caller], "You don't own that many LP points"
    assert lp_tokens_total[poolName] - amountLPTokens > 1, "You need to leave atleast 1 LP point"
    assert amountLPTokens > 0, "Needs to more then 0"
    total_lp_points = lp_tokens_total[poolName]
    for contract in pools[poolName].all():
        amount = pools[poolName, contract] / total_lp_points * amountLPTokens
        token.transfer(amount=amount, to=ctx.caller)
        pools[poolName, contract] -= amount
        lp_tokens_total[poolName] -= amountLPTokens
        lp_tokens_users[poolName, ctx.caller] -= amountLPTokens


@export
def transferLiquidity(poolName: str, amountLPTokens: float, to: str):
    assert amountLPTokens <= lp_tokens_users[poolName, ctx.caller], "You don't own that many LP points"
    assert amountLPTokens > 0, "Needs to more then 0"
    lp_tokens_users[poolName, ctx.caller] -= amountLPTokens
    lp_tokens_users[poolName, to] += amountLPTokens

@export
def approveLiquidity(poolName: str, amountLPTokens: float, main_account: str, to: str):
   assert amountLPTokens <= lp_tokens_users[poolName, ctx.caller], "You don't own that many LP points"
   assert amountLPTokens > 0, "Needs to more then 0"
   lp_tokens_approvals[poolName, ctx.caller, to] += amountLPTokens

@export
def transferLiquidityFrom(poolName: str, amountLPTokens: float, main_account: str, to: str):
    assert amountLPTokens <= lp_tokens_users[poolName, main_account], "Not enough LP points to send"
    assert amountLPTokens > 0, "Needs to more then 0"
    lp_tokens_users[poolName, main_account] -= amountLPTokens
    lp_tokens_users[poolName, to] += amountLPTokens
    lp_tokens_approvals[poolName, main_account, to] -= amountLPTokens


@export
def swap(poolName: str, amountFrom: float, contractFrom: str, contractTo: str):
    assert amountFrom > 0, "Needs to more then 0"
    fee_amount = amountFrom/100*fee.get()
    swap_amount = amountFrom - fee_amount
    local_balances = [pools[poolName, contractFrom], pools[poolName, contractTo]]
    local_weights = [pool_weights[poolName, contractFrom], pool_weights[poolName, contractTo]]
    final_amount = calc_out_given_in(local_balances[0], local_weights[0], local_balances[1], local_weights[1], swap_amount)       
    fromToken = I.import_module(contractFrom)   
    toToken =  I.import_module(contractTo)   
    fromToken.transfer_from(amount=swap_amount, to=ctx.this, main_account=ctx.caller)
    fromToken.transfer_from(amount=fee_amount, to=operator.get(), main_account=ctx.caller)
    pools[poolName, contractFrom] += swap_amount
    toToken.transfer(amount=final_amount, to= ctx.caller)
    pools[poolName, contractTo] -= swap_amount
    return final_amount

    
def calc_out_given_in(balance_in: decimal,
                          weight_in: decimal,
                          balance_out: decimal,
                          weight_out: decimal,
                          amount_in: decimal):

    denominator = balance_in + amount_in
    base = div(balance_in, denominator)  # balanceIn.divUp(denominator);
    exponent = div(weight_in, weight_out)  # weightIn.divDown(weightOut);
    power = powerIt(base, exponent)  # base.powUp(exponent);

    return mul(balance_out, complement(power))  # balanceOut.mulDown(power.complement());


def mul(a: decimal, b: decimal):
    return a*b


def div(a: decimal, b: decimal):
    result =  a/b
    return result


def complement(a: decimal):
    return (1 - a) if a < 1 else 0


def powerIt(a: decimal,b:decimal):
    return a**b



