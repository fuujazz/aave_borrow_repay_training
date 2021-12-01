from scripts.helpful_scripts import get_account
from brownie import interface, network, config


def main():
    get_weth()


def get_weth():
    """
    Mints WETH by depositing ETH
    """
    #   ABI
    #   Address
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()].get("weth_token"))
    tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
    tx.wait(1)
    print(f"Received 0.1 ETH")
    return tx
