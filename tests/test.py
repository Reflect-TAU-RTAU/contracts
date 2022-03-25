import unittest
from contracting.stdlib.bridge.time import Datetime

from contracting.client import ContractingClient
import logging


class MyTestCase(unittest.TestCase):
    currency = None
    reflecttau = None
    basic = None
    reflecttau_v2 = None
    reflecttau_v2_buyback = None
    reflecttau_v2_developer = None
    reflecttau_v2_liquidity = None
    reflecttau_v2_treasury = None
    rocketswap = None
    rswp_token = None

    def reset(self):
        self.c= ContractingClient()
        self.c.flush()
        self.c.signer = "ff61544ea94eaaeb5df08ed863c4a938e9129aba6ceee5f31b6681bdede11b89"

        with open("./currency.py") as f:
            code = f.read()
            self.c.submit(code, name="currency")

        with open("./con_rswp_lst001.py") as f:
            code = f.read()
            self.c.submit(code, name="con_rswp_lst001")

        with open("./con_reflecttau.py") as f:
            code = f.read()
            self.c.submit(code, name="con_reflecttau")

        with open("./con_doug_lst001.py") as f:
            code = f.read()
            self.c.submit(code, name="con_doug_lst001")

        with open("./con_rocketswap_official_v1_1.py") as f:
            code = f.read()
            self.c.submit(code, name="con_rocketswap_official_v1_1")

        with open("../con_reflecttau_v2.py") as f:
            code = f.read()
            self.c.submit(code, name="con_reflecttau_v2")

        with open("../con_reflecttau_v2_buyback.py") as f:
            code = f.read()
            self.c.submit(code, name="con_reflecttau_v2_buyback")

        with open("../con_reflecttau_v2_developer.py") as f:
            code = f.read()
            self.c.submit(code, name="con_reflecttau_v2_developer")
        
        with open("../con_reflecttau_v2_liquidity.py") as f:
            code = f.read()
            self.c.submit(code, name="con_reflecttau_v2_liquidity")
        
        with open("../con_reflecttau_v2_treasury.py") as f:
            code = f.read()
            self.c.submit(code, name="con_reflecttau_v2_treasury")


        self.currency = self.c.get_contract("currency")
        self.reflecttau = self.c.get_contract("con_reflecttau")
        self.basic = self.c.get_contract("con_doug_lst001")
        self.reflecttau_v2 = self.c.get_contract("con_reflecttau_v2")
        self.reflecttau_v2_buyback = self.c.get_contract("con_reflecttau_v2_buyback")
        self.reflecttau_v2_developer = self.c.get_contract("con_reflecttau_v2_developer")
        self.reflecttau_v2_liquidity = self.c.get_contract("con_reflecttau_v2_liquidity")
        self.reflecttau_v2_treasury = self.c.get_contract("con_reflecttau_v2_treasury")
        self.rocketswap = self.c.get_contract("con_rocketswap_official_v1_1")
        self.rswp_token = self.c.get_contract("con_rswp_lst001")
        
        
    def test_flow(self):
        log = logging.getLogger("Tests")
        self.reset()
        logging.debug("^-------------------- TEST RTAU V2 TOKEN ----------------------------------------^")
        logging.debug("--------------------- 1. TEST SWAP BASIC TO RTAU V2 TOKEN ------------------------")

        logging.debug("Approving 10 BASIC to con_reflecttau_v2")
        self.basic.approve(amount=10,to="con_reflecttau_v2")
        logging.debug("Swapped 10 BASIC to (RETURN VALUE)" + str(self.reflecttau_v2.swap_basic(basic_amount=10)) + "/ (REAL NEW ADDRESS BALANCE)"+ str(self.reflecttau_v2.balance_of(address=self.c.signer))+" RTAU V2")

        logging.debug("--------------------- 2. TEST SWAP RTAU TO RTAU V2 TOKEN -------------------------")

        logging.debug("Approving 10 RTAU to con_reflecttau_v2")
        self.reflecttau.approve(amount=10,to="con_reflecttau_v2")
        logging.debug("Swapped 10 RTAU to (RETURN VALUE)" + str(self.reflecttau_v2.swap_rtau(rtau_amount=10)) + "/ (REAL NEW ADDRESS BALANCE)"+ str(self.reflecttau_v2.balance_of(address=self.c.signer))+" RTAU V2")

        #self.currency.approve(amount=4,to="con_rocketswap_official_v1_1",signer="hax")
        #self.reflecttau_v2.approve(amount=990090000,to="con_rocketswap_official_v1_1")
        #self.currency.approve(amount=11111111,to="con_rocketswap_official_v1_1")

        #self.rswp_token.approve(amount=1,to="con_rocketswap_official_v1_1")
        #logging.debug("Useless RSWP Pair created o: " + str(self.rocketswap.create_market(contract="con_rswp_lst001",currency_amount=1,token_amount=1)))
        #logging.debug("Pair created: " + str(self.rocketswap.create_market(contract="con_reflecttau_v2",currency_amount=65000,token_amount=680000000)))

       

if __name__ == "__main__":
    log = logging.getLogger("Tests")
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    unittest.main()