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
    reflecttau_v2_reflection = None
    reflecttau_v2_treasury = None
    rocketswap = None
    rswp_token = None

    def reset(self):
        self.c= ContractingClient()
        self.c.flush()
        self.c.signer = "a5565739151e6f8d3fbb03ab605a31cc285e36a717a95002a60e6e4d4e4fa411"

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
            self.c.submit(code, name="con_reflecttau_v2", constructor_args={'name': 'con_reflecttau_v2'})

        with open("../con_reflecttau_v2_reflection.py") as f:
            code = f.read()
            self.c.submit(code, name="con_reflecttau_v2_reflection")

        with open("../con_reflecttau_v2_buyback.py") as f:
            code = f.read()
            self.c.submit(code, name="con_reflecttau_v2_buyback")

        with open("../con_reflecttau_v2_developer.py") as f:
            code = f.read()
            self.c.submit(code, name="con_reflecttau_v2_developer")
        
        with open("../con_reflecttau_v2_liquidity.py") as f:
            code = f.read()
            self.c.submit(code, name="con_reflecttau_v2_liquidity", constructor_args={'name': 'con_reflecttau_v2_liquidity'})
        
        with open("../con_reflecttau_v2_treasury.py") as f:
            code = f.read()
            self.c.submit(code, name="con_reflecttau_v2_treasury")


        self.currency = self.c.get_contract("currency")
        self.reflecttau = self.c.get_contract("con_reflecttau")
        self.basic = self.c.get_contract("con_doug_lst001")
        self.reflecttau_v2 = self.c.get_contract("con_reflecttau_v2")
        self.reflecttau_v2_reflection = self.c.get_contract("con_reflecttau_v2_reflection")
        self.reflecttau_v2_buyback = self.c.get_contract("con_reflecttau_v2_buyback")
        self.reflecttau_v2_developer = self.c.get_contract("con_reflecttau_v2_developer")
        self.reflecttau_v2_liquidity = self.c.get_contract("con_reflecttau_v2_liquidity")
        self.reflecttau_v2_treasury = self.c.get_contract("con_reflecttau_v2_treasury")
        self.rocketswap = self.c.get_contract("con_rocketswap_official_v1_1")
        self.rswp_token = self.c.get_contract("con_rswp_lst001")
        
        
    def test_flow(self):
        log = logging.getLogger("Tests")
        self.reset()
        logging.debug("\x1b[31;20mTEST RTAU V2 TOKEN\x1b[0m")
        logging.debug("\x1b[33;20m1. TEST SWAP BASIC TO RTAU V2 TOKEN\x1b[0m")
        logging.debug("Approving 1000 BASIC to con_reflecttau_v2")
        self.basic.approve(amount=1000000,to="con_reflecttau_v2")
        logging.debug("Swapped 10 BASIC to (RETURN VALUE) " + str(self.reflecttau_v2.swap_basic(basic_amount=1000000)) + "/ (REAL NEW ADDRESS BALANCE) "+ str(self.reflecttau_v2.balance_of(address=self.c.signer))+" RTAU V2")

        logging.debug("\x1b[33;20m2. TEST SWAP RTAU TO RTAU V2 TOKEN\x1b[0m-")
        logging.debug("Approving 1000 RTAU to con_reflecttau_v2")
        self.reflecttau.approve(amount=1000,to="con_reflecttau_v2")
        logging.debug("Swapped 10 RTAU to (RETURN VALUE) " + str(self.reflecttau_v2.swap_rtau(rtau_amount=1000)) + "/ (REAL NEW ADDRESS BALANCE) "+ str(self.reflecttau_v2.balance_of(address=self.c.signer))+" RTAU V2")

        logging.debug("\x1b[33;20m3. TEST TRANSFER (NORMAL - USER) RTAU V2\x1b[0m")
        logging.debug("Transfering 1 RTAU V2 to Address: hax")
        self.reflecttau_v2.transfer(amount=1, to="hax")
        logging.debug("Transfered 1 RTAU V2 to Address: hax with (REAL NEW RECEIVER ADDRESS BALANCE): "+ str(self.reflecttau_v2.balance_of(address="hax"))+" RTAU V2")

        logging.debug("\x1b[33;20m4. TEST TRANSFER_FROM (NORMAL - USER) RTAU V2\x1b[0m")
        logging.debug("Approving 1 RTAU to a5565739151e6f8d3fbb03ab605a31cc285e36a717a95002a60e6e4d4e4fa411")
        self.reflecttau_v2.approve(amount=1,to="a5565739151e6f8d3fbb03ab605a31cc285e36a717a95002a60e6e4d4e4fa411")
        logging.debug("Transfering 1 RTAU V2 to Address: hax where main_account is a5565739151e6f8d3fbb03ab605a31cc285e36a717a95002a60e6e4d4e4fa411")
        self.reflecttau_v2.transfer_from(amount=1, to="hax", main_account="a5565739151e6f8d3fbb03ab605a31cc285e36a717a95002a60e6e4d4e4fa411")
        logging.debug("Transfered 1 RTAU V2 to Address: hax with (REAL NEW RECEIVER ADDRESS BALANCE): "+ str(self.reflecttau_v2.balance_of(address="hax"))+" RTAU V2")

        

        
        logging.debug("\x1b[33;20m6. TEST CREATE PAIR RTAU V2\x1b[0m")
        self.reflecttau_v2.approve(amount=1000,to="con_rocketswap_official_v1_1")
        self.currency.approve(amount=201,to="con_rocketswap_official_v1_1")
        self.rswp_token.approve(amount=1,to="con_rocketswap_official_v1_1")
        logging.debug("Useless RSWP Pair created (Has to exist for Rocketswap to work): " + str(self.rocketswap.create_market(contract="con_rswp_lst001",currency_amount=1,token_amount=1)))
        

        self.reflecttau_v2.approve(amount=1000,to="con_reflecttau_v2_liquidity")
        self.currency.approve(amount=201,to="con_reflecttau_v2_liquidity")
        logging.debug("Depositing RTAU to Liq contract " + str(self.reflecttau_v2_liquidity.deposit_rtau(amount=1000)))
        logging.debug("Depositing TAU to Liq contract " + str(self.reflecttau_v2_liquidity.deposit_tau(amount=200)))
        logging.debug("RTAU V2 Pair created: " + str(self.reflecttau_v2_liquidity.create_market(tau_amount=200,token_amount=1000)))
        logging.debug("Sync Liq State: " + str(self.reflecttau_v2_reflection.sync_initial_liq_state()))
        

        logging.debug("\x1b[33;20m7. TEST BUY RTAU V2\x1b[0m")
        self.currency.approve(amount=10000,to="con_rocketswap_official_v1_1")
        logging.debug("Purchased: " + str(self.rocketswap.buy(contract="con_reflecttau_v2", currency_amount=10000)) + " RTAU V2")
        logging.debug("User now has: " + str(self.reflecttau_v2.balance_of(address=self.c.signer)) + " RTAU V2 and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        
        logging.debug("Buyback Contract now: " + str(self.currency.balance_of(account="con_reflecttau_v2_buyback")) + " TAU")
        logging.debug("Liquidity Contract now: " + str(self.currency.balance_of(account="con_reflecttau_v2_liquidity")) + " TAU")
        logging.debug("Develop Contract now: " + str(self.currency.balance_of(account="con_reflecttau_v2_developer")) + " TAU")
        logging.debug("Reflection Contract now has: " + str(self.currency.balance_of(account="con_reflecttau_v2_reflection")) + " TAU")
        logging.debug("Reflection Contract now has (metadata['tau_pool']): " + str(self.reflecttau_v2_reflection.metadata["tau_pool"]) + " TAU")

        logging.debug("\x1b[33;20m8. TEST SELL RTAU V2\x1b[0m")
        self.reflecttau_v2.approve(amount=1,to="con_rocketswap_official_v1_1")
        logging.debug("Sold for: " + str(self.rocketswap.sell(contract="con_reflecttau_v2", token_amount=1)) + " TAU")
        logging.debug("User now has: " + str(self.reflecttau_v2.balance_of(address=self.c.signer)) + " RTAU V2 and " + str(self.currency.balance_of(account=self.c.signer)) + " TAU")
        
        logging.debug("Buyback Contract now: " + str(self.currency.balance_of(account="con_reflecttau_v2_buyback")) + " TAU")
        logging.debug("Liquidity Contract now: " + str(self.currency.balance_of(account="con_reflecttau_v2_liquidity")) + " TAU")
        logging.debug("Develop Contract now: " + str(self.currency.balance_of(account="con_reflecttau_v2_developer")) + " TAU")
        logging.debug("Reflection Contract now has: " + str(self.currency.balance_of(account="con_reflecttau_v2_reflection")) + " TAU")
        logging.debug("Reflection Contract now has (metadata['tau_pool']): " + str(self.reflecttau_v2_reflection.metadata["tau_pool"]) + " TAU")

        logging.debug("\x1b[33;20mINFO RTAU V2\x1b[0m")
        logging.debug("\x1b[33;20m FORWARD INDEX RTAU V2\x1b[0m")
        logging.debug(self.reflecttau_v2_reflection.forward_holders_index.all())
        logging.debug("\x1b[33;20m REVERSE INDEX RTAU V2\x1b[0m")
        logging.debug(self.reflecttau_v2_reflection.reverse_holders_index.all())
        logging.debug("\x1b[33;20m HOLDERS AMOUNT RTAU V2\x1b[0m")
        logging.debug(self.reflecttau_v2_reflection.holders_amount.get())
        logging.debug("\x1b[33;20m TAU POOL RTAU V2\x1b[0m")
        logging.debug(self.reflecttau_v2_reflection.metadata['tau_pool'])

        logging.debug("\x1b[33;20m9. REDISTRIBUTE RTAU V2\x1b[0m")
        logging.debug("User has " + str(self.currency.balance_of(account=self.c.signer)) + " TAU before REDISTRIBUTE")
        self.reflecttau_v2_reflection.redistribute_tau()
        
        logging.debug("\x1b[33;20m REFLECTION HASH RTAU V2\x1b[0m")
        logging.debug(self.reflecttau_v2_reflection.reflections.all())
        self.reflecttau_v2_reflection.claim_tau()
        logging.debug("User has " + str(self.currency.balance_of(account=self.c.signer)) + " TAU after REDISTRIBUTE AND CLAIM")
        logging.debug("\x1b[33;20m TAU POOL RTAU V2\x1b[0m")
        logging.debug(self.reflecttau_v2_reflection.metadata['tau_pool'])



        logging.debug("\x1b[33;20m11. TRANSFER RTAU AND GO UNDER REWARD LIMIT V2\x1b[0m")
        logging.debug("User has " + str(self.reflecttau_v2.balance_of(address=self.c.signer)) + " RTAU")
        logging.debug("Transfering all balance out")
        self.reflecttau_v2.transfer(amount=8000, to="hax")
        logging.debug("User has " + str(self.reflecttau_v2.balance_of(address=self.c.signer)) + " RTAU")
        logging.debug("\x1b[33;20m FORWARD INDEX RTAU V2\x1b[0m")
        logging.debug(self.reflecttau_v2_reflection.forward_holders_index.all())
        logging.debug("\x1b[33;20m REVERSE INDEX RTAU V2\x1b[0m")
        logging.debug(self.reflecttau_v2_reflection.reverse_holders_index.all())
        logging.debug("\x1b[33;20m12. AUTO LIQ RTAU V2\x1b[0m")
        logging.debug("Added: " + str(self.reflecttau_v2_liquidity.add_liquidity()))
        logging.debug("\x1b[33;20m13. BUYBACK RTAU V2\x1b[0m")
        logging.debug("Bought back and burned: " + str(self.reflecttau_v2.external_call(action="action_buyback",payload="")))

        logging.debug("\x1b[33;20m14. MULTISIG V2\x1b[0m")
        logging.debug("Modifying Liq Contract")

        
        logging.debug("Address a5565739151e6f8d3fbb03ab605a31cc285e36a717a95002a60e6e4d4e4fa411 signed (RETURN VAL: " + str(self.reflecttau_v2.change_metadata(key="con_reflecttau_v2_liquidity",value="con_new_contract_name",signer="a5565739151e6f8d3fbb03ab605a31cc285e36a717a95002a60e6e4d4e4fa411")) + ")")
        logging.debug("Address 025169da812b5db222e0ce57fbc2b5f949a59ac10a1a65a77fa4ab67c492fbad signed (RETURN VAL: " + str(self.reflecttau_v2.change_metadata(key="con_reflecttau_v2_liquidity",value="con_new_contract_name",signer="025169da812b5db222e0ce57fbc2b5f949a59ac10a1a65a77fa4ab67c492fbad")) + ")")
        logging.debug("Address 6351a80d32cbb3c173e490b093a95b15bcf4f6190251863669202d7fe2257af3 signed (RETURN VAL: " + str(self.reflecttau_v2.change_metadata(key="con_reflecttau_v2_liquidity",value="con_new_contract_name",signer="6351a80d32cbb3c173e490b093a95b15bcf4f6190251863669202d7fe2257af3")) + ")")
        try:
            logging.debug("Verifying signature reset. Signature = con_reflecttau_v2_liquidity:a5565739151e6f8d3fbb03ab605a31cc285e36a717a95002a60e6e4d4e4fa411 = " + str(self.reflecttau_v2.metadata["con_reflecttau_v2_liquidity"]["a5565739151e6f8d3fbb03ab605a31cc285e36a717a95002a60e6e4d4e4fa411"]))
        except:
            logging.debug("Verifying signature reset. Signature = con_reflecttau_v2_liquidity:a5565739151e6f8d3fbb03ab605a31cc285e36a717a95002a60e6e4d4e4fa411 = None")

        logging.debug("Removing 50 (Points) Liquidity from Rocketswap")
        logging.debug("LIQ BEFORE: " + str(self.rocketswap.liquidity_balance_of(contract="con_reflecttau_v2",account="con_reflecttau_v2_liquidity")))
        logging.debug("Address a5565739151e6f8d3fbb03ab605a31cc285e36a717a95002a60e6e4d4e4fa411 signed (RETURN VAL: " + str(self.reflecttau_v2.change_metadata(key="con_reflecttau_v2_liquidity",value="remove_liquidity:5",signer="a5565739151e6f8d3fbb03ab605a31cc285e36a717a95002a60e6e4d4e4fa411")) + ")")
        logging.debug("Address 025169da812b5db222e0ce57fbc2b5f949a59ac10a1a65a77fa4ab67c492fbad signed (RETURN VAL: " + str(self.reflecttau_v2.change_metadata(key="con_reflecttau_v2_liquidity",value="remove_liquidity:5",signer="025169da812b5db222e0ce57fbc2b5f949a59ac10a1a65a77fa4ab67c492fbad")) + ")")
        logging.debug("Address 6351a80d32cbb3c173e490b093a95b15bcf4f6190251863669202d7fe2257af3 signed (RETURN VAL: " + str(self.reflecttau_v2.change_metadata(key="con_reflecttau_v2_liquidity",value="remove_liquidity:5",signer="6351a80d32cbb3c173e490b093a95b15bcf4f6190251863669202d7fe2257af3")) + ")")
        logging.debug("Executing Removal" + self.reflecttau_v2.external_call(action="action_liquidity",payload="remove_liquidity:5"))
        logging.debug("LIQ AFTER : " + str(self.rocketswap.liquidity_balance_of(contract="con_reflecttau_v2",account="con_reflecttau_v2_liquidity")))


if __name__ == "__main__":
    log = logging.getLogger("Tests")
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    unittest.main()