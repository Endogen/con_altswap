import unittest
from contracting.stdlib.bridge.time import Datetime

from contracting.client import ContractingClient
import logging


class MyTestCase(unittest.TestCase):
    currency = None
    con_reflecttau_v2 = None
    con_weth_lst001 = None
    con_lust_lst001 = None
    con_altswap_v2 = None

    def reset(self):
        self.c= ContractingClient()
        self.c.flush()
        self.c.signer = "ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d"

        with open("./currency.py") as f:
            code = f.read()
            self.c.submit(code, name="currency")

        with open("./con_reflecttau_v2.py") as f:
            code = f.read()
            self.c.submit(code, name="con_reflecttau_v2")

        with open("./con_weth_lst001.py") as f:
            code = f.read()
            self.c.submit(code, name="con_weth_lst001")

        with open("./con_lust_lst001.py") as f:
            code = f.read()
            self.c.submit(code, name="con_lust_lst001")

        with open("./con_altswap_v2.py") as f:
            code = f.read()
            self.c.submit(code, name="con_altswap_v2")

        self.currency = self.c.get_contract("currency")
        self.con_reflecttau_v2 = self.c.get_contract("con_reflecttau_v2")
        self.con_weth_lst001 = self.c.get_contract("con_weth_lst001")
        self.con_lust_lst001 = self.c.get_contract("con_lust_lst001")
        self.con_altswap_v2 = self.c.get_contract("con_altswap_v2")
        
    def test_flow(self):
        log = logging.getLogger("Tests")
        self.reset()
        logging.debug("\x1b[31;20mTEST ALTSWAP DEX\x1b[0m")

        logging.debug("1. Approving 1000 TAU to con_altswap_v2")
        self.currency.approve(amount=1000,to="con_altswap_v2")
        
        logging.debug("2. Approving 1000 WETH to con_altswap_v2")
        self.con_weth_lst001.approve(amount=1000,to="con_altswap_v2")

        logging.debug("3. Approving 1000 LUSD to con_altswap_v2")
        self.con_lust_lst001.approve(amount=1000,to="con_altswap_v2")

        logging.debug("4. Creating pool with LUSD, WETH, TAU")
        assets = {"con_lust_lst001": 100, "con_weth_lst001": 2, "currency": 2000}
        self.con_altswap_v2.createWeightedPool(poolName="LUSD-WETH-TAU", assets=assets)

        logging.debug("5. Check details of pool")
        logging.debug("Total LP: " + self.con_altswap_v2.pools["LUSD-WETH-TAU"])

        logging.debug("Init amount of LUSD: " + self.con_altswap_v2.pools["LUSD-WETH-TAU", "con_lust_lst001", "init"])
        logging.debug("Init amount of WETH: " + self.con_altswap_v2.pools["LUSD-WETH-TAU", "con_weth_lst001", "init"])
        logging.debug("Init amount of TAU : " + self.con_altswap_v2.pools["LUSD-WETH-TAU", "currency", "init"])

        logging.debug("Amount of LUSD: " + self.con_altswap_v2.pools["LUSD-WETH-TAU", "con_lust_lst001"])
        logging.debug("Amount of WETH: " + self.con_altswap_v2.pools["LUSD-WETH-TAU", "con_weth_lst001"])
        logging.debug("Amount of TAU : " + self.con_altswap_v2.pools["LUSD-WETH-TAU", "currency"])

        logging.debug("Weight amount of LUSD: " + self.con_altswap_v2.pools["LUSD-WETH-TAU", "con_lust_lst001", "weight"])
        logging.debug("Weight amount of WETH: " + self.con_altswap_v2.pools["LUSD-WETH-TAU", "con_weth_lst001", "weight"])
        logging.debug("Weight amount of TAU : " + self.con_altswap_v2.pools["LUSD-WETH-TAU", "currency", "weight"])

        logging.debug("Total LP Tokens  : " + self.con_altswap_v2.lp_tokens["LUSD-WETH-TAU"])
        logging.debug("LP Tokens of user: " + self.con_altswap_v2.lp_tokens["LUSD-WETH-TAU", "ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d"])

if __name__ == "__main__":
    log = logging.getLogger("Tests")
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    unittest.main()