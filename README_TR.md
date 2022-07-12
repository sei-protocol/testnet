# Validatör Olmak
**Sei Testnnet'te validatör olmanız için yapmanız gerekenler**
*Sei Testnet-1 (sei-testnet-1)*

> Genesis [Published](https://github.com/sei-protocol/testnet/blob/main/sei-testnet-1/genesis.json)

> Peers [Published](https://github.com/sei-protocol/testnet/blob/main/sei-testnet-1/addrbook.json)

## Sistem Gereksinimleri
**En Düşük**
* 8 GB RAM
* 100 GB NVME SSD
* 3.2 GHz x4 CPU

**Tavsiye edilen**
* 16 GB RAM
* 500 GB NVME SSD
* 4.2 GHz x6 CPU 

## İşletim Sistemi

> Linux (x86_64) or Linux (amd64) Arch Linux Tavsiye edilir
Ubuntu 20.04 ve üstü versiyonlara kurulumu rahatlıkla yapabilirsiniz

**Gerekli Eklentiler**
> Ön Gereksinim: go1.18+ required.
* Arch Linux: `pacman -S go`
* Ubuntu: `sudo snap install go --classic`

> Ön Gereksinim: git. 
* Arch Linux: `pacman -S git`
* Ubuntu: `sudo apt-get install git`

> Opsiyonel Gereksinimler: GNU make. 
* Arch Linux: `pacman -S make`
* Ubuntu: `sudo apt-get install make`

## Sei (Seid) Kurulum Adımları

**Özellikle eğer Google Cloud Kullanıyorsanz root dizinine geçiniz** 
```bash
sudo su 
cd
```
**Ubuntu güncellemeleri** 

```bash
sudo apt-get update
sudo apt-get upgrade
```

**Kurulum öncesi gerekli bazı paketlerin yüklenmesi**

```bash
sudo apt install make clang pkg-config libssl-dev git jq bsdmainutils screen build-essential -y < "/dev/null"

```
**GO Kurulumun Yapılması**

(ver= kısmını GO'nun güncel versiyona göre değiştirebilirsiniz)
```bash
ver="18.1.3"
wget -O go$ver.linux-amd64.tar.gz https://golang.org/dl/go$ver.linux-amd64.tar.gz
rm -rf /usr/local/go
tar -C /usr/local -xzf go1.18.1.linux-amd64.tar.gz
echo 'export GOROOT=/usr/local/go' >> $HOME/.bash_profile
echo 'export GOPATH=$HOME/go' >> $HOME/.bash_profile
echo 'export GO111MODULE=on' >> $HOME/.bash_profile
echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> $HOME/.bash_profile && . $HOME/.bash_profile
go version
```

go version komutunda belirttiğiniz versiyonda go kurulumun yüklü olduğuna dair bir geri dönüş almalısınız

**Gerekli node dosyalarını indirme ve yükleme**

```bash
git clone https://github.com/sei-protocol/sei-chain
cd sei-chain
git checkout origin/1.0.1beta-upgrade
make install
mv $HOME/go/bin/seid /usr/bin/
```
**Moniker init etme**
isterseniz MONIKER olarak bir dağişken yaratarak 

moniker="MONIKER_ISMI"

şeklinde belirleyebilir ve aşağıdaki kodu direk kullanabilirsiniz veya $MONIKER yerine istediğiniz ismi direk yazabilirsiniz

```bash
seid init $MONIKER --chain-id sei-testnet-2 -o
```

**Genesis ve Addressbook dosyası indirme**

```bash
wget -qO $HOME/.sei/config/genesis.json "https://raw.githubusercontent.com/sei-protocol/testnet/main/sei-testnet-2/genesis.json"
wget -qO $HOME/.sei/config/addrbook.json "https://raw.githubusercontent.com/sei-protocol/testnet/main/sei-testnet-2/addrbook.json"
```
**Eğer harddisk boyutunuz çok fazla değilse pruning yapabilirsiniz**

```bash
pruning="custom"
pruning_keep_recent="100"
pruning_keep_every="0"
pruning_interval="10"


sed -i -e "s/^pruning *=.*/pruning = \"$pruning\"/" $HOME/.sei/config/app.toml
sed -i -e "s/^pruning-keep-recent *=.*/pruning-keep-recent = \"$pruning_keep_recent\"/" $HOME/.sei/config/app.toml
sed -i -e "s/^pruning-keep-every *=.*/pruning-keep-every = \"$pruning_keep_every\"/" $HOME/.sei/config/app.toml
sed -i -e "s/^pruning-interval *=.*/pruning-interval = \"$pruning_interval\"/" $HOME/.sei/config/app.toml
```
**Servis Dosyası Oluşturma**
tek bir komut olarak girebilirsiniz

```bash
tee $HOME/seid.service > /dev/null <<EOF
[Unit]
Description=seid
After=network.target
[Service]
Type=simple
User=$USER
ExecStart=$(which seid) start
Restart=on-failure
RestartSec=10
LimitNOFILE=65535
[Install]
WantedBy=multi-user.target
EOF
```
**Servis Dosyasını taşıma**

```bash
mv $HOME/seid.service /etc/systemd/system/
```
**Servis dosyasını aktive edebilmek için systemctl güncelleme**
```bash
sudo systemctl daemon-reload
```

**Servis dosyasını aktive etme**
```bash
sudo systemctl enable seid
```

**Servis dosyasını başlatma**
```bash
sudo systemctl start seid
```

**Servis durumunu kontrol etme**
```bash
sudo systemctl status seid
```

**Cüzdan oluşturma**

* Sıfırdan cüzdan oluşturma. Cüzdanı oluşturduktan sonra mnemonicleri kaydetmeyi unutmayın

```bash
seid keys add CUZDANISMI
```

* Daha önce oluşturulmuş bir cüzdanı geri getirme

```bash
seid keys add CUZDANISMI --recover
```
bu kod ardında mnemoniclerinizi girmeniz gerekecektir.


* Ledger ile cüzdan oluşturma
```bash
seid keys add CUZDANISMI --ledger
```


## Validator oluşturma

* Kurulum tamamlandıktan sonra validatör kurmak için güncel bloğu yakalamanız gerekmektedir.
```bash
seid status | jq .SyncInfo
```
bu komutta en alttaki değer "true"'dan "false"'a dönene kadar bekleyin 

Validatör oluşturma kodu
CUZDANADI VE MONIKERADI kısımlarını kendinize göre değiştirin

```bash
seid tx staking create-validator \
--from CUZDANADI \
--chain-id="sei-testnet-2"  \
--moniker=MONIKERADI \
--commission-max-change-rate=0.01 \
--commission-max-rate=0.2 \
--commission-rate=0.05 \
--pubkey $(seid tendermint show-validator) \
--min-self-delegation="1" \
--amount 900000usei \
```



## Logları takip etme
```bash
journalctl -u seid -f`
```
## Logları takip etmek için ayrı bir screen oluşturabilirsiniz##

```bash
screen -S sei
journalctl -u seid -f`
```

ctrl + a + d ile screenden çıkabilirsiniz

