import unittest
import logging

from decimal import *
from contracting.stdlib.bridge.time import Datetime
from contracting.client import ContractingClient

MAX_RELATIVE_ERROR = Decimal(1e-17)

class MyTestCase(unittest.TestCase):
    currency = None
    con_reflecttau_v2 = None
    con_weth_lst001 = None
    con_lusd_lst001 = None
    con_altswap_v2 = None

    def reset(self):
        self.c= ContractingClient()
        self.c.flush()
        self.c.signer = "ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d"

        with open("./currency.py") as f:
            code = f.read()
            self.c.submit(code, name="currency")

        with open("./con_weth_lst001.py") as f:
            code = f.read()
            self.c.submit(code, name="con_weth_lst001")

        with open("./con_lusd_lst001.py") as f:
            code = f.read()
            self.c.submit(code, name="con_lusd_lst001")

        with open("../con_altswap_v2.py") as f:
            code = f.read()
            self.c.submit(code, name="con_altswap_v2")

        self.currency = self.c.get_contract("currency")
        self.con_reflecttau_v2 = self.c.get_contract("con_reflecttau_v2")
        self.con_weth_lst001 = self.c.get_contract("con_weth_lst001")
        self.con_lusd_lst001 = self.c.get_contract("con_lusd_lst001")
        self.con_altswap_v1 = self.c.get_contract("con_altswap_v1")
        self.con_altswap_v2 = self.c.get_contract("con_altswap_v2")

    def expect_equal_with_error(result: Decimal, expected: Decimal):
        if result <= expected + MAX_RELATIVE_ERROR and result >= expected - MAX_RELATIVE_ERROR:
            return True
        return False

    def get_pool_details(self):
        logging.debug("Check details of pool")
        logging.debug("  Total LP: " + str(self.con_altswap_v2.pools["LUSD-WETH-TAU"]))

        logging.debug("  Init amount of LUSD: " + str(self.con_altswap_v2.pools["LUSD-WETH-TAU", "con_lusd_lst001", "init"]))
        logging.debug("  Init amount of WETH: " + str(self.con_altswap_v2.pools["LUSD-WETH-TAU", "con_weth_lst001", "init"]))
        logging.debug("  Init amount of TAU : " + str(self.con_altswap_v2.pools["LUSD-WETH-TAU", "currency", "init"]))

        logging.debug("  Amount of LUSD: " + str(self.con_altswap_v2.pools["LUSD-WETH-TAU", "con_lusd_lst001"]))
        logging.debug("  Amount of WETH: " + str(self.con_altswap_v2.pools["LUSD-WETH-TAU", "con_weth_lst001"]))
        logging.debug("  Amount of TAU : " + str(self.con_altswap_v2.pools["LUSD-WETH-TAU", "currency"]))

        logging.debug("  Weight of LUSD: " + str(self.con_altswap_v2.pools["LUSD-WETH-TAU", "con_lusd_lst001", "weight"]))
        logging.debug("  Weight of WETH: " + str(self.con_altswap_v2.pools["LUSD-WETH-TAU", "con_weth_lst001", "weight"]))
        logging.debug("  Weight of TAU : " + str(self.con_altswap_v2.pools["LUSD-WETH-TAU", "currency", "weight"]))

        logging.debug("  Total LP Tokens  : " + str(self.con_altswap_v2.lp_tokens["LUSD-WETH-TAU"]))

        logging.debug("  Contract balance LUSD: " + str(self.con_lusd_lst001.balances["con_altswap_v2"]))
        logging.debug("  Contract balance WETH: " + str(self.con_weth_lst001.balances["con_altswap_v2"]))
        logging.debug("  Contract balance TAU : " + str(self.currency.balances["con_altswap_v2"]))

    def test_flow(self):
        log = logging.getLogger("Tests")
        self.reset()

        logging.debug("\x1b[31;20mTEST ALTSWAP DEX\x1b[0m")

        logging.debug("Balance of ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d")
        logging.debug(f"  LUSD: {self.con_lusd_lst001.balances['ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d']}")
        logging.debug(f"  WETH: {self.con_weth_lst001.balances['ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d']}")
        logging.debug(f"  TAU : {self.currency.balances['ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d']}")

        logging.debug("Approving 1000 TAU to con_altswap_v2")
        self.currency.approve(amount=5000,to="con_altswap_v2")
        
        logging.debug("Approving 1000 WETH to con_altswap_v2")
        self.con_weth_lst001.approve(amount=5000,to="con_altswap_v2")

        logging.debug("Approving 1000 LUSD to con_altswap_v2")
        self.con_lusd_lst001.approve(amount=5000,to="con_altswap_v2")

        logging.debug("---- Three Asset Pool ----")
        assets = {"con_lusd_lst001": 30, "con_weth_lst001": 20, "currency": 50}
        logging.debug(f"Creating pool {assets}")
        self.con_altswap_v2.createWeightedPool(poolName="LUSD-WETH-TAU", assets=assets)

        logging.debug("Balance of ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d")
        logging.debug(f"  LUSD: {self.con_lusd_lst001.balances['ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d']}")
        logging.debug(f"  WETH: {self.con_weth_lst001.balances['ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d']}")
        logging.debug(f"  TAU : {self.currency.balances['ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d']}")

        self.get_pool_details()

        logging.debug("LP Tokens of ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d: " + str(self.con_altswap_v2.lp_tokens["LUSD-WETH-TAU", "ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d"]))

        assets = {"con_lusd_lst001": 85.5, "con_weth_lst001": 57, "currency": 142.5}
        logging.debug(f"Add liquidity to pool {assets}")
        logging.debug("LP to mint: " + str(self.con_altswap_v2.addLiquidity(poolName="LUSD-WETH-TAU",assets=assets)))

        self.get_pool_details()

        logging.debug("LP Tokens of ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d: " + str(self.con_altswap_v2.lp_tokens["LUSD-WETH-TAU", "ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d"]))

        logging.debug("Remove 285 LP from pool")
        self.con_altswap_v2.removeLiquidity(poolName="LUSD-WETH-TAU", amountLPTokens=285)

        self.get_pool_details()

        logging.debug("LP Tokens of ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d: " + str(self.con_altswap_v2.lp_tokens["LUSD-WETH-TAU", "ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d"]))

        logging.debug("Transfer 50 LP to 46883e75f5974bcc86bc4a74e5f257bef104795894a80eaee2be92ba53de2ec1")
        self.con_altswap_v2.transferLiquidity(poolName="LUSD-WETH-TAU", amountLPTokens=50, to="46883e75f5974bcc86bc4a74e5f257bef104795894a80eaee2be92ba53de2ec1")

        self.get_pool_details()

        logging.debug("LP Tokens of ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d: " + str(self.con_altswap_v2.lp_tokens["LUSD-WETH-TAU", "ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d"]))
        logging.debug("LP Tokens of 46883e75f5974bcc86bc4a74e5f257bef104795894a80eaee2be92ba53de2ec1: " + str(self.con_altswap_v2.lp_tokens["LUSD-WETH-TAU", "46883e75f5974bcc86bc4a74e5f257bef104795894a80eaee2be92ba53de2ec1"]))

        poolName = "LUSD-WETH-TAU"
        amountLPTokens = 10
        main_account = "ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d"
        to = "46883e75f5974bcc86bc4a74e5f257bef104795894a80eaee2be92ba53de2ec1"

        logging.debug(f"LP Balance of {main_account}: {self.con_altswap_v2.liquidityBalanceOf(poolName='LUSD-WETH-TAU', account=main_account)}")
        logging.debug(f"LP Balance of {to}: {self.con_altswap_v2.liquidityBalanceOf(poolName='LUSD-WETH-TAU', account=to)}")

        logging.debug(f"Approve Liquidity: pool = {poolName} amount = {amountLPTokens} main account = {main_account[:8]}... to = {to[:8]}...")
        self.con_altswap_v2.approveLiquidity(poolName="LUSD-WETH-TAU", amountLPTokens=amountLPTokens, main_account="ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d", to="46883e75f5974bcc86bc4a74e5f257bef104795894a80eaee2be92ba53de2ec1")

        logging.debug(f"Transfer liquidity: pool = {poolName} amount = {amountLPTokens} main account = {main_account[:8]}... to = {to[:8]}...")
        self.con_altswap_v2.transferLiquidityFrom(poolName="LUSD-WETH-TAU", amountLPTokens=amountLPTokens, main_account="ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d", to="46883e75f5974bcc86bc4a74e5f257bef104795894a80eaee2be92ba53de2ec1")

        logging.debug(f"LP Balance of {main_account}: {self.con_altswap_v2.liquidityBalanceOf(poolName='LUSD-WETH-TAU', account=main_account)}")
        logging.debug(f"LP Balance of {to}: {self.con_altswap_v2.liquidityBalanceOf(poolName='LUSD-WETH-TAU', account=to)}")

        logging.debug("  Amount of LUSD: " + str(self.con_altswap_v2.pools["LUSD-WETH-TAU", "con_lusd_lst001"]))
        logging.debug("  Amount of WETH: " + str(self.con_altswap_v2.pools["LUSD-WETH-TAU", "con_weth_lst001"]))
        logging.debug("  Amount of TAU : " + str(self.con_altswap_v2.pools["LUSD-WETH-TAU", "currency"]))

        logging.debug(f"Swapping from 10 TAU to LUSD - Result: {self.con_altswap_v2.swap(poolName=poolName, amountFrom=10, contractFrom='currency', contractTo='con_lusd_lst001')}")
        
        logging.debug("  Amount of LUSD: " + str(self.con_altswap_v2.pools["LUSD-WETH-TAU", "con_lusd_lst001"]))
        logging.debug("  Amount of WETH: " + str(self.con_altswap_v2.pools["LUSD-WETH-TAU", "con_weth_lst001"]))
        logging.debug("  Amount of TAU : " + str(self.con_altswap_v2.pools["LUSD-WETH-TAU", "currency"]))

        logging.debug("Balance of ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d")
        logging.debug(f"  LUSD: {self.con_lusd_lst001.balances['ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d']}")
        logging.debug(f"  WETH: {self.con_weth_lst001.balances['ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d']}")
        logging.debug(f"  TAU : {self.currency.balances['ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d']}")

        logging.debug("---- Two Asset Pool ----")
        assets = {"con_lusd_lst001": 50, "currency": 50}
        logging.debug(f"Creating pool {assets}")
        self.con_altswap_v2.createWeightedPool(poolName="LUSD-TAU", assets=assets)

        logging.debug("  Amount of LUSD: " + str(self.con_altswap_v2.pools["LUSD-TAU", "con_lusd_lst001"]))
        logging.debug("  Amount of TAU : " + str(self.con_altswap_v2.pools["LUSD-TAU", "currency"]))

        logging.debug("  Weight of LUSD: " + str(self.con_altswap_v2.pools["LUSD-TAU", "con_lusd_lst001", "weight"]))
        logging.debug("  Weight of TAU : " + str(self.con_altswap_v2.pools["LUSD-TAU", "currency", "weight"]))

        logging.debug("Balance of ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d")
        logging.debug(f"  LUSD: {self.con_lusd_lst001.balances['ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d']}")
        logging.debug(f"  TAU : {self.currency.balances['ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d']}")

        logging.debug(f"Swapping from 25 TAU to LUSD - Result: {self.con_altswap_v2.swap(poolName='LUSD-TAU', amountFrom=25, contractFrom='currency', contractTo='con_lusd_lst001')}")
        
        logging.debug("  Amount of LUSD: " + str(self.con_altswap_v2.pools["LUSD-TAU", "con_lusd_lst001"]))
        logging.debug("  Amount of TAU : " + str(self.con_altswap_v2.pools["LUSD-TAU", "currency"]))

        logging.debug("Balance of ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d")
        logging.debug(f"  LUSD: {self.con_lusd_lst001.balances['ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d']}")
        logging.debug(f"  TAU : {self.currency.balances['ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d']}")        


if __name__ == "__main__":
    log = logging.getLogger("Tests")
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    unittest.main()
