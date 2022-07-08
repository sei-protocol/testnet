from operator import ge
import argparse
import os
import json
import shutil
from pathlib import Path

'''
Resets the genesis.json file to the default values & clears all balances / accounts
Then will generate all the commands to add balances for all gentxs
Assumes you've already run confirm-gen-txs.py
'''

EXP_SEND = [{"denom": "usei","enabled": True}]

def main(chain_id, home_dir, initial_balance):
    reset_genesis_file(chain_id, home_dir)
    create_genesis_account_cmds(initial_balance)
    copy_gentx_folder(chain_id, home_dir)

def reset_genesis_file(chain_id, home_dir):
    genesis_file = home_dir + "/config/genesis.json" 
    # load genesis.json & remove all values for accounts & supply
    with open(genesis_file) as f:
        genesis = json.load(f)
        genesis["chain_id"] = str(chain_id)

        genesis["app_state"]['auth']["accounts"] = []
        genesis["app_state"]['bank']["balances"] = []
        genesis["app_state"]['bank']["supply"] = []
        genesis["app_state"]['bank']["params"]["send_enabled"] = EXP_SEND

        genesis["app_state"]['genutil']["gen_txs"] = []

    # save genesis.json
    with open(genesis_file, 'w') as f:
        json.dump(genesis, f, indent=4)
    print(f"# RESET: {genesis_file}\n")


def create_genesis_account_cmds(initial_balance):
    print("-- Run the following commands to create genesis accounts --")
    with open('gentx-output.csv') as f:
        for line in f:
            validator_address = line.split(',')[0]
            print(f"seid add-genesis-account {validator_address} {initial_balance}")

    print("--- Run the following commands to create genesis accounts ---")

def copy_gentx_folder(chain_id, home_dir):
    shutil.copytree(chain_id + "/gentx", home_dir + "/config/gentx")
    print(f"gentx folder copied to {home_dir}/config/gentx")
    print("--- Run the following command to create validators ---")
    print("seid collect-gentxs")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--chain-id', type=str)
    parser.add_argument('--home-dir', type=str)
    parser.add_argument('--initial-balance', type=str)
    args = parser.parse_args()
    assert (args.initial_balance[-4:] == 'usei')
    main(args.chain_id, args.home_dir, args.initial_balance)