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
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFees() + 1000})
    lottery.enter({"from": account, "value": lottery.getEntranceFees() + 1000})
    lottery.enter({"from": account, "value": lottery.getEntranceFees() + 1000})
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    time.sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
