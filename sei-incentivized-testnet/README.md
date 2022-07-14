# Becoming A Validator on atlantic-1

## Quick Links

Genesis: [Published](https://github.com/sei-protocol/testnet/raw/main/sei-incentivized-testnet/genesis.json)

Initial addrbook: [Published](https://github.com/sei-protocol/testnet/raw/main/sei-incentivized-testnet/addrbook.json)

Seed node: `df1f6617ff5acdc85d9daa890300a57a9d956e5e@sei-atlantic-1.seed.rhinostake.com:16660`

| Additional documentation is available on the [seinetwork.io website](https://docs.seinetwork.io/nodes-and-validators/seinami-incentivized-testnet/joining-incentivized-testnet).

## Hardware / Software Requirements

### Minimum

- 3.2 GHz 4 Core CPU
- 8 GB RAM
- 240 GB NVME SSD

### Recommended

- 4.2 GHz 8 Core CPU
- 32 GB RAM
- 512 GB NVME SSD

### Operating System

- Linux (x86_64) or Linux (amd64)
- Recommended Arch Linux, but any modern distribution will work.

### Dependencies

> Prerequisite: go1.18+ required.

- Arch Linux: `pacman -S go`
- Ubuntu: `sudo snap install go --classic`
- Source: `wget https://go.dev/dl/go1.18.4.linux-amd64.tar.gz && sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.18.4.linux-amd64.tar.gz`. Be sure to also add `export PATH=$PATH:/usr/local/go/bin` to your .bashrc/.zshrc file.

> Prerequisite: git.

- Arch Linux: `pacman -S git`
- Ubuntu: `sudo apt-get install git` (should be installed by default)

> Optional requirement: GNU make.

- Arch Linux: `pacman -S make`
- Ubuntu: `sudo apt-get install make` or `sudo apt-get build-essential`

## Seid Installation Steps

### Clone git repository

```bash
git clone https://github.com/sei-protocol/sei-chain
cd sei-chain
git checkout <tag-name>
# Current testnet tag is 1.0.6beta
make install
```

## Generate Keys

- `seid keys add [key_name]`

- `seid keys add [key_name] --recover` to regenerate keys with your mnemonic

- `seid keys add [key_name] --ledger` to generate keys with ledger device

## Validator Setup Instructions

- Install seid binary
- Initialize node: `seid init <moniker> --chain-id=atlantic-1`
- Download the Genesis file: `curl -s https://github.com/sei-protocol/testnet/raw/main/sei-incentivized-testnet/genesis.json > $HOME/.sei/config/genesis.json`
- Set the seed address: `sed -i 's/seeds = ""/seeds = "df1f6617ff5acdc85d9daa890300a57a9d956e5e@sei-atlantic-1.seed.rhinostake.com:16660"/g' $HOME/.sei/config/config.toml`
- Experienced operators will tweak other settings such as pruning, indexing, etc.
- Start seid by creating a systemd service to run the node in the background
  `nano /etc/systemd/system/seid.service`
     > Copy and paste the following text into your service file. Be sure to edit as you see fit.

```bash
[Unit]
Description=Sei-Network Node
After=network.target

[Service]
Type=simple
User=<username>
WorkingDirectory=/<username>/.sei
ExecStart=/<username>/go/bin/seid start
Restart=on-failure
StartLimitInterval=0
RestartSec=3
LimitNOFILE=65535
LimitMEMLOCK=209715200

[Install]
WantedBy=multi-user.target
```

## Start The Node

- Reload the service files: `sudo systemctl daemon-reload`
- Create the symlinlk: `sudo systemctl enable seid.service`
- Start the node sudo: `systemctl start seid && journalctl -u seid -f`

## Create Validator Transaction

After starting the node above, you can check the status of the sync by running `curl -s localhost:26657/status` and inspecting the `"catching_up"` key. If `false`, then the node has synced successfully.

After the node has synced to the top of the chain, you will be able to run the `create-validator` command. You will need sei tokens in your wallet to do so.

```bash
seid tx staking create-validator \
--from {{KEY_NAME}} \
--chain-id="atlantic-1"  \
--moniker="<VALIDATOR_NAME>" \
--commission-max-change-rate=0.01 \
--commission-max-rate=1.0 \
--commission-rate=0.05 \
--details="<description>" \
--security-contact="<contact_information>" \
--website="<your_website>" \
--pubkey $(seid tendermint show-validator) \
--min-self-delegation="1" \
--amount <token delegation>usei
```
