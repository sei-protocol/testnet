## Here are instructions to setup TMKMS as a validator security for SEI Network
#### Tendermint Key Management System
The official documentation is [[here](https://github.com/iqlusioninc/tmkms#tendermint-kms-)]  
In this article, we will configure `tmkms` on a separate server for the double-signing protection of SEI' validators.

Advantage of this method instead of basic installation: 
1) double-signing protection 
2) having the validator keys in separated server.  
## Use Case
If you already run a validator node. It's not too late to set up tmkms. Follow the instructions below.
## Analogue
To prevent double-signing protection, as an analogue, you can use [[horcrux](https://github.com/strangelove-ventures/horcrux)]. 
## Overview
- [Setting up a Validator node](https://github.com/AlexToTheSun/testnet/blob/turetskiy2/validator-security-tmkms.md#setting-up-a-validator-node)
  - [Firewall configuration](https://github.com/AlexToTheSun/testnet/blob/turetskiy2/validator-security-tmkms.md#firewall-configuration)
  - [Edit config.toml](https://github.com/AlexToTheSun/testnet/blob/turetskiy2/validator-security-tmkms.md#edit-configtoml)
- [Setting up a tmkms server](https://github.com/AlexToTheSun/testnet/blob/turetskiy2/validator-security-tmkms.md#setting-up-a-tmkms-server)
  - [Install tmkms](https://github.com/AlexToTheSun/testnet/blob/turetskiy2/validator-security-tmkms.md#install-tmkms)
  - [Firewall configuration](https://github.com/AlexToTheSun/testnet/blob/turetskiy2/validator-security-tmkms.md#firewall-configuration-1)
  - [Init tmkms](https://github.com/AlexToTheSun/testnet/blob/turetskiy2/validator-security-tmkms.md#init-tmkms)
  - [Copy priv_validator_key.json from validator node](https://github.com/AlexToTheSun/testnet/blob/turetskiy2/validator-security-tmkms.md#copy-priv_validator_keyjson-from-validator-node)
  - [Edit tmkms.toml](https://github.com/AlexToTheSun/testnet/blob/turetskiy2/validator-security-tmkms.md#edit-tmkmstoml)
- [Restert both validator and tmkms](https://github.com/AlexToTheSun/testnet/blob/turetskiy2/validator-security-tmkms.md#restert-both-validator-and-tmkms)

## Setting up a Validator node
We already  [[run](https://github.com/AlexToTheSun/Validator_Activity/blob/main/Testnet-guides/SEI-testnet-devnet/SEI_atlantic-1.md)] a validator node in `atlantic-1` testnet.

### Firewall configuration
Allow access to port 26658 of validator's node for the tmkms server:
```
sudo ufw allow from <ip_tmkms> to any port 26658
```
### Edit config.toml
Open `config.toml` by `nano`:
```
nano $HOME/.sei/config/config.toml
```
Edit the line `priv_validator_laddr = ""` like this:
```
priv_validator_laddr = "tcp://<ip_VAL>:26658"
```
where `<ip_VAL>` - ip of the validator' server.  

Or you can enter this value: `priv_validator_laddr = "tcp://<nodeid_VAL>@<ip_VAL>:26658"`. To find out node_id you should type `seid tendermint show-node-id'`

**DON'T RESTART validator' service file!!!** Until you have configured the tmkms server.

## Setting up a tmkms server
This server does not require the SEI Network node. **tmkms** only.  
The official documentation is [[here](https://github.com/iqlusioninc/tmkms#tendermint-kms-)]
### Install tmkms
Update & upgrade
```
sudo apt update && sudo apt upgrade -y
```
THen you will need the following prerequisites:
```
sudo apt-get install -y gcc clang pkg-config libusb-1.0-0-dev
```
And also package:
```
sudo apt-get install -y \
make \
build-essential \
libssl-dev \
jq \
curl \
ncdu \
git \
g++ \
make \
mc \
nano
```
Then install rustup  https://rustup.rs/
```
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
cp $HOME/.cargo/bin/* /usr/bin/
rustup version
```
Configure RUSTFLAGS environment variable (x86_64 only):
```
echo 'export RUSTFLAGS=-Ctarget-feature=+aes,+ssse3' >> $HOME/.bash_profile
. $HOME/.bash_profile
```
Compiling `tmkms` from source code. In our case, we use the flag `--features=softsign`
```
git clone https://github.com/iqlusioninc/tmkms.git && cd tmkms
cargo build --release --features=softsign
cp /root/tmkms/target/release/tmkms /usr/bin/
tmkms version
```
### Firewall configuration
Installing and configuration ufw
```
sudo apt ufw install -y
sudo ufw allow 22
sudo ufw allow ssh
sudo ufw allow 26658
sudo ufw enable
sudo ufw status
ss -tulpn
```
You should change the SSH port. Click [[here](https://github.com/AlexToTheSun/Validator_Activity/blob/main/Mainnet-Guides/Minimum-server-protection.md#change-the-ssh-port)]  
### Init tmkms
```
tmkms init $HOME/.tmkms/sei
```
### Copy `priv_validator_key.json` from validator node
Use [WinSCP](https://winscp.net/download/WinSCP-5.19.5-Setup.exe) to copy the `priv_validator_key.json` from the validator's node. And put it in the `$HOME/.tmkms/sei` folder.
Then type the command below to import information from `priv_validator_key.json` to `cosmoshub-3-consensus.key`:
```
tmkms softsign import $HOME/.tmkms/sei/priv_validator_key.json $HOME/.tmkms/sei/secrets/cosmoshub-3-consensus.key
rm $HOME/.tmkms/sei/priv_validator_key.json
```
### Edit tmkms.toml
Open `tmkms.toml` in `nano`
```
nano $HOME/.tmkms/sei/tmkms.toml
```
Edit the file like this:
```
# Example Tendermint KMS configuration file
## Chain Configuration
[[chain]]
id = "atlantic-1"
key_format = { type = "bech32", account_key_prefix = "seipub", consensus_key_prefix = "seivalconspub" }
state_file = "$HOME/.tmkms/sei/state/cosmoshub-3-consensus.json"
## Signing Provider Configuration
### Software-based Signer Configuration
[[providers.softsign]]
chain_ids = ["atlantic-1"]
key_type = "consensus"
path = "$HOME/.tmkms/sei/secrets/cosmoshub-3-consensus.key"
## Validator Configuration
[[validator]]
chain_id = "atlantic-1"
addr = "tcp://<ip_VAL>:26658"
secret_key = "$HOME/.tmkms/sei/home/secrets/kms-identity.key"
protocol_version = "v0.34"
reconnect = true
```
- `addr` - the validator' server address. Shoud match the `priv_validator_laddr` in sei' `config.toml`.
- `protocol_version` - find out `seid tendermint version`
## Restert both validator and tmkms
### Start tmkms
Try start on tmkms server
```
tmkms start -c $HOME/.tmkms/sei/tmkms.toml
```
If everything is alright then start tmkms as service file.  
**Create the file**
```
sudo tee <<EOF >/dev/null /etc/systemd/system/tmkmsei.service
[Unit]  
Description=tmkms SEI Network service  
After=network.target  
StartLimitIntervalSec=0
[Service]
Type=simple  
Restart=always  
RestartSec=10  
User=root
ExecStart=/usr/bin/tmkms start -c $HOME/.tmkms/sei/tmkms.toml  
LimitNOFILE=1024
[Install]  
WantedBy=multi-user.target
EOF
```
Start tmkmsei
```
sudo systemctl enable tmkmsei
sudo systemctl daemon-reload
sudo systemctl restart tmkmsei
journalctl -u tmkmsei -f
```
### Restart `seid` service on the server of the validator
```
sudo systemctl restart seid
journalctl -u seid -f --output cat
```
### Restart tmkms service
```
sudo systemctl restart tmkmsei
journalctl -u tmkmsei -f
```
Now all should work. Check logs:
```
journalctl -u tmkmsei -f --output cat
journalctl -u seid -f --output cat
```
Don't forget **to backup and delete** the `priv_validator_key.json` file from the validator node. Now you won't need it. Keep it in a secure place, such as a flash drive.

