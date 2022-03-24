import unittest
from contracting.stdlib.bridge.time import Datetime

from contracting.client import ContractingClient
import logging


class MyTestCase(unittest.TestCase):
    currency = None
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
        logging.debug("--------------------- TEST NEW TOKEN ------------------------")
        
        self.currency.approve(amount=4,to="con_rocketswap_official_v1_1",signer="hax")
        self.reflecttau_v2.approve(amount=990090000,to="con_rocketswap_official_v1_1")
        self.currency.approve(amount=11111111,to="con_rocketswap_official_v1_1")

        self.rswp_token.approve(amount=1,to="con_rocketswap_official_v1_1")
        logging.debug("Useless RSWP Pair created o: " + str(self.rocketswap.create_market(contract="con_rswp_lst001",currency_amount=1,token_amount=1)))
        logging.debug("Pair created: " + str(self.rocketswap.create_market(contract="con_reflecttau_v2",currency_amount=65000,token_amount=680000000)))

        # self.mintorburn_v2.change_metadata(key="is_initial_liq_ready", value=True)
        
        # logging.debug("Buy Fee set to: 10%")
        # logging.debug("Sell Fee set to: 10%")
        # self.rswp_token.approve(amount=1000000,to="con_rocketswap_official_v1_1")
        # self.currency.approve(amount=1,to="con_rocketswap_official_v1_1")
        

        # logging.debug("Current Liquidity: " + str(self.rocketswap.liquidity_balance_of(contract="con_reflecttau",account=self.c.signer)))

        # self.mintorburn_v2.approve(amount=111111,to="con_rocketswap_official_v1_1")        
        # self.currency.approve(amount=2000000,to="con_rocketswap_official_v1_1")

    

        # logging.debug("--------------------- SELL ------------------------")
        # logging.debug("User has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Sold for: " + str(self.rocketswap.sell(contract="con_reflecttau", token_amount=100000)) + " TAU")
        # logging.debug("User now has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Contract now has: " + str(self.currency.balance_of(account="con_reflecttau")) + " TAU")
        # logging.debug("Contract has TAU RESERVED VARIABLE: " + str(self.mintorburn_v2.metadata["tau_pool"]) + " TAU")

        # logging.debug("--------------------- SELL ------------------------")
        # logging.debug("User has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Sold for: " + str(self.rocketswap.sell(contract="con_reflecttau", token_amount=100000)) + " TAU")
        # logging.debug("User now has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Contract now has: " + str(self.currency.balance_of(account="con_reflecttau")) + " TAU")
        # logging.debug("Contract has TAU RESERVED VARIABLE: " + str(self.mintorburn_v2.metadata["tau_pool"]) + " TAU")

        # logging.debug("--------------------- BUY ------------------------")
        # logging.debug("User has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Purchased: " + str(self.rocketswap.buy(contract="con_reflecttau", currency_amount=4)) + " RTAU")
        # logging.debug("User now has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Contract now has: " + str(self.currency.balance_of(account="con_reflecttau")) + " TAU")
        # logging.debug("Contract has TAU RESERVED VARIABLE: " + str(self.mintorburn_v2.metadata["tau_pool"]) + " TAU")

        # logging.debug("--------------------- SELL ------------------------")
        # logging.debug("User has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Sold for: " + str(self.rocketswap.sell(contract="con_reflecttau", token_amount=100000)) + " TAU")
        # logging.debug("User now has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Contract now has: " + str(self.currency.balance_of(account="con_reflecttau")) + " TAU")
        # logging.debug("Contract has TAU RESERVED VARIABLE: " + str(self.mintorburn_v2.metadata["tau_pool"]) + " TAU")


        # logging.debug("--------------------- SELL ------------------------")
        # logging.debug("User has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Sold for: " + str(self.rocketswap.sell(contract="con_reflecttau", token_amount=100000)) + " TAU")
        # logging.debug("User now has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Contract now has: " + str(self.currency.balance_of(account="con_reflecttau")) + " TAU")
        # logging.debug("Contract has TAU RESERVED VARIABLE: " + str(self.mintorburn_v2.metadata["tau_pool"]) + " TAU")


        # logging.debug("--------------------- SELL ------------------------")
        # logging.debug("User has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Sold for: " + str(self.rocketswap.sell(contract="con_reflecttau", token_amount=100000)) + " TAU")
        # logging.debug("User now has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Contract now has: " + str(self.currency.balance_of(account="con_reflecttau")) + " TAU")
        # logging.debug("Contract has TAU RESERVED VARIABLE: " + str(self.mintorburn_v2.metadata["tau_pool"]) + " TAU")

        # logging.debug("--------------------- BUY ------------------------")
        # logging.debug("User has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Purchased: " + str(self.rocketswap.buy(contract="con_reflecttau", currency_amount=4)) + " RTAU")
        # logging.debug("User now has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Contract now has: " + str(self.currency.balance_of(account="con_reflecttau")) + " TAU")
        # logging.debug("Contract has TAU RESERVED VARIABLE: " + str(self.mintorburn_v2.metadata["tau_pool"]) + " TAU")

        # logging.debug("--------------------- SELL ------------------------")
        # logging.debug("User has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Sold for: " + str(self.rocketswap.sell(contract="con_reflecttau", token_amount=100000)) + " TAU")
        # logging.debug("User now has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Contract now has: " + str(self.currency.balance_of(account="con_reflecttau")) + " TAU")
        # logging.debug("Contract has TAU RESERVED VARIABLE: " + str(self.mintorburn_v2.metadata["tau_pool"]) + " TAU")

        # logging.debug("--------------------- SELL ------------------------")
        # logging.debug("User has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Sold for: " + str(self.rocketswap.sell(contract="con_reflecttau", token_amount=100000)) + " TAU")
        # logging.debug("User now has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Contract now has: " + str(self.currency.balance_of(account="con_reflecttau")) + " TAU")
        # logging.debug("Contract has TAU RESERVED VARIABLE: " + str(self.mintorburn_v2.metadata["tau_pool"]) + " TAU")

        # logging.debug("--------------------- BUY ------------------------")
        # logging.debug("User has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Purchased: " + str(self.rocketswap.buy(contract="con_reflecttau", currency_amount=4)) + " RTAU")
        # logging.debug("User now has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Contract now has: " + str(self.currency.balance_of(account="con_reflecttau")) + " TAU")
        # logging.debug("Contract has TAU RESERVED VARIABLE: " + str(self.mintorburn_v2.metadata["tau_pool"]) + " TAU")


        # self.mintorburn_v2.approve(amount=111111,to="con_rocketswap_official_v1_1")        
        # self.currency.approve(amount=2000000,to="con_rocketswap_official_v1_1")

        

        # self.mintorburn_v2.approve(amount=111111,to="con_rocketswap_official_v1_1")        
        # self.currency.approve(amount=2000000,to="con_rocketswap_official_v1_1")


        

        # logging.debug("--------------------- BUY ------------------------")
        # logging.debug("hax has: " + str(self.mintorburn_v2.balance_of(address="hax" )) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Purchased: " + str(self.rocketswap.buy(contract="con_reflecttau", currency_amount=4,signer="hax")) + " RTAU")
        # logging.debug("User now has: " + str(self.mintorburn_v2.balance_of(address="hax")) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        # logging.debug("Contract now has: " + str(self.currency.balance_of(account="con_reflecttau")) + " TAU")
        # logging.debug("Contract has TAU RESERVED VARIABLE: " + str(self.mintorburn_v2.metadata["tau_pool"]) + " TAU")


        
        # logging.debug(self.mintorburn_v2.forward_holders_index.all())
        # logging.debug(self.mintorburn_v2.reverse_holders_index.all())
        # logging.debug(self.mintorburn_v2.holders_amount.get())
        
        
        # logging.debug("--------------------- REDISTRIBUTE TAU ------------------------")
        # logging.debug("User has " + str(self.currency.balance_of(account="hax")) + " TAU before REDISTRIBUTE")
        # self.mintorburn_v2.redistribute_tau(start=0, end=3)
        
        # logging.debug(self.mintorburn_v2.reflections.all()[0])
        # self.mintorburn_v2.claim_tau(signer="hax")
        # logging.debug("User has " + str(self.currency.balance_of(account="hax")) + " TAU after REDISTRIBUTE")

        #logging.debug("--------------------- BUY ------------------------")
        #logging.debug("User has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        #logging.debug("Purchased: " + str(self.rocketswap.buy(contract="con_mintorburn_v2", currency_amount=4)) + " RTAU")
        #logging.debug("User now has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        #logging.debug("Contract now has: " + str(self.currency.balance_of(account="con_mintorburn_v2")) + " TAU")
        #logging.debug("Contract has TAU RESERVED VARIABLE: " + str(self.mintorburn_v2.metadata["tau_pool"]) + " TAU")

        #logging.debug("--------------------- BUY ------------------------")
        #logging.debug("User has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        #logging.debug("Purchased: " + str(self.rocketswap.buy(contract="con_mintorburn_v2", currency_amount=100)) + " RTAU")
        #logging.debug("User now has: " + str(self.mintorburn_v2.balance_of(address=self.c.signer)) + " RTAU and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        #logging.debug("Contract now has: " + str(self.currency.balance_of(account="con_mintorburn_v2")) + " TAU")
        #logging.debug("Contract has TAU RESERVED VARIABLE: " + str(self.mintorburn_v2.metadata["tau_pool"]) + " TAU")
        

if __name__ == "__main__":
    log = logging.getLogger("Tests")
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    unittest.main()