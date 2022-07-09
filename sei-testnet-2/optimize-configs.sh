#!/bin/bash
if [ ! -z "$1" ]; then
  CONFIG_PATH="$1"
else
  CONFIG_PATH="$HOME/.sei/config/config.toml"
fi

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  sed -i 's/max_num_inbound_peers =.*/max_num_inbound_peers = 150/g' $CONFIG_PATH
  sed -i 's/max_num_outbound_peers =.*/max_num_outbound_peers = 150/g' $CONFIG_PATH
  sed -i 's/max_packet_msg_payload_size =.*/max_packet_msg_payload_size = 10240/g' $CONFIG_PATH
  sed -i 's/send_rate =.*/send_rate = 20480000/g' $CONFIG_PATH
  sed -i 's/recv_rate =.*/recv_rate = 20480000/g' $CONFIG_PATH
  sed -i 's/max_txs_bytes =.*/max_txs_bytes = 10737418240/g' $CONFIG_PATH
  sed -i 's/^size =.*/size = 5000/g' $CONFIG_PATH
  sed -i 's/max_tx_bytes =.*/max_tx_bytes = 2048576/g' $CONFIG_PATH
  sed -i 's/timeout_prevote =.*/timeout_prevote = "100ms"/g' $CONFIG_PATH
  sed -i 's/timeout_precommit =.*/timeout_precommit = "100ms"/g' $CONFIG_PATH
  sed -i 's/timeout_commit =.*/timeout_commit = "100ms"/g' $CONFIG_PATH
  sed -i 's/skip_timeout_commit =.*/skip_timeout_commit = true/g' $CONFIG_PATH
elif [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' 's/max_num_inbound_peers =.*/max_num_inbound_peers = 150/g' $CONFIG_PATH
  sed -i '' 's/max_num_outbound_peers =.*/max_num_outbound_peers = 150/g' $CONFIG_PATH
  sed -i '' 's/max_packet_msg_payload_size =.*/max_packet_msg_payload_size = 10240/g' $CONFIG_PATH
  sed -i '' 's/send_rate =.*/send_rate = 20480000/g' $CONFIG_PATH
  sed -i '' 's/recv_rate =.*/recv_rate = 20480000/g' $CONFIG_PATH
  sed -i '' 's/max_txs_bytes =.*/max_txs_bytes = 10737418240/g' $CONFIG_PATH
  sed -i '' 's/^size =.*/size = 5000/g' $CONFIG_PATH
  sed -i '' 's/max_tx_bytes =.*/max_tx_bytes = 2048576/g' $CONFIG_PATH
  sed -i '' 's/timeout_prevote =.*/timeout_prevote = "100ms"/g' $CONFIG_PATH
  sed -i '' 's/timeout_precommit =.*/timeout_precommit = "100ms"/g' $CONFIG_PATH
  sed -i '' 's/timeout_commit =.*/timeout_commit = "100ms"/g' $CONFIG_PATH
  sed -i '' 's/skip_timeout_commit =.*/skip_timeout_commit = true/g' $CONFIG_PATH
else
  printf "Platform not supported, please ensure that the following values are set in your config.toml:\n"
  printf "###          Mempool Configuration Option          ###\n"
  printf "\t size = 5000\n"
  printf "\t max_txs_bytes = 10737418240\n"
  printf "\t max_tx_bytes = 2048576\n"
  printf "###           P2P Configuration Options             ###\n"
  printf "\t max_num_inbound_peers = 150\n"
  printf "\t max_num_outbound_peers = 150\n"
  printf "\t max_packet_msg_payload_size = 10240\n"
  printf "\t send_rate = 20480000\n"
  printf "\t recv_rate = 20480000\n"
  printf "###         Consensus Configuration Options         ###\n"
  printf "\t timeout_prevote = \"100ms\"\n"
  printf "\t timeout_precommit = \"100ms\"\n"
  printf "\t timeout_commit = \"100ms\"\n"
  printf "\t skip_timeout_commit = true\n"
  exit 1
fi

