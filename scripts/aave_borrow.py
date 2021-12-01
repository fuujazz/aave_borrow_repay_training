from scripts.helpful_scripts import get_account
from brownie import config, network, interface
from scripts.get_weth import get_weth
from web3 import Web3

# 0.1
amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()].get("weth_token")

    if network.show_active() in ["mainnet-fork"]:
        get_weth()

    #   ABI
    #   ADDRESS

    lending_pool = get_lending_pool()
    #   approve sending out erc20 tokens

    print("Depositing...")
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )  #       referral code doesnt work anymore so always pass 0 for it
    tx.wait(1)
    print("Depositing is succesful!")

    # how much can i borrow ? "getAccountData"

    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Borrow DAI!")
    #   DAI in terms of ETH

    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()].get("dai_eth_price_feed")
    )

    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    #   borrowable_eth ---> borrowable_dai * 95%
    print(f"We are going to borrow {amount_dai_to_borrow}")
    #   aave borrow
    dai_address = config["networks"][network.show_active()].get("dai_token")
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("Dai borrowed succesfully")
    get_borrowable_data(lending_pool, account)

    #   REPAY

    # repay_all(amount, lending_pool, account)

    print("deposited, borrowed and repayed with Aave, Brownie and Chainlink")


def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()].get("dai_token"),
        account,
    )

    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()].get("dai_token"),
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repayed!")


def get_asset_price(price_feed_address):
    #   ABI
    #   Address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_price = Web3.fromWei(latest_price, "ether")
    print(f"Dai / Eth price is {converted_price}")
    return float(converted_price)


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)

    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH Deposited")
    print(f"You have {total_debt_eth} worth of ETH Borrowed")
    print(f"You can borrow {available_borrow_eth} worth of ETH ")
    return (float(available_borrow_eth), float(total_debt_eth))


def approve_erc20(amount, spender, erc20_address, account):
    #   ABI
    #   Address
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx


def get_lending_pool():
    #   ABI

    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()].get("lending_pool_addresses_provider")
    )

    lending_pool_address = lending_pool_addresses_provider.getLendingPool()  #   Address

    lending_pool = interface.ILendingPool(lending_pool_address)

    return lending_pool
