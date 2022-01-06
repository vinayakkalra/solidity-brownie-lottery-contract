from toolz.itertoolz import get
from brownie import Lottery, MockV3Aggregator, config, accounts, network, exceptions
from scripts.helpful_scripts import (
    fund_with_link,
    get_account,
    deploy_mocks,
    LOCAL_BLOCKCHAIN_ENV,
    get_contract,
)
from web3 import Web3
from scripts.deploy import deploy_lottery
import pytest


def test_get_entrance_fee():
    if network.show_active not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    entrance_fee = lottery.getEntranceFees()

    expected_entrance_fee = Web3.toWei(0.025, "ether")
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    if network.show_active not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFees()})


def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFees()})
    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFees()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFees()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFees()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFees()})
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    requestId = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        requestId, STATIC_RNG, lottery.address, {"from": account}
    )
    starting_balance_of_account = account.balance()
    lottery_balance = lottery.balance()
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + lottery_balance
