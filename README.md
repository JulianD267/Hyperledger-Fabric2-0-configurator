# [](#hyperledger-fabric-v20-tutorial)Hyperledger Fabric V2.1 - Create a Development Business Network on an ARM64 based Platform (Raspberry Pi 4)

This project is intended to give an introduction into (partially) setting up a Hyperledger Business Network on a Raspberry Pi 4. The idea is to setup a proper HLF 2.0 Network on your local Server/PC and later outsource one peer to a Raspberry Pi node. The whole process involves multiple steps. Feel free to jump to the corresponding ToC markers.
### Disclaimer
Please read the README in the **master branch** for a deeper understanding of merlin and the generator.

[Hyperledger Fabric V2.1 - Create a Development Business Network on an ARM64 based Platform (Raspberry Pi 4)](#hyperledger-fabric-v21---create-a-development-business-network-on-an-arm64-based-platform-raspberry-pi-4)
  - [Disclaimer](#disclaimer)
  - [Recommended Reading](#recommended-reading)
  - [Setup Your Environment](#setup-your-environment)
    - [Docker](#docker)
    - [Docker Compose](#docker-compose)
    - [Golang](#golang)
    - [Python](#python)
  - [Retrieve Artifacts from Hyperledger Fabric Repositories](#retrieve-artifacts-from-hyperledger-fabric-repositories)
  - [Create Hyperledger Fabric Business Network](#create-hyperledger-fabric-business-network)
    - [1. Download proper Docker images to the Raspberry Pi](#1-download-proper-docker-images-to-the-raspberry-pi)
    - [2. Edit the /etc/hosts file](#2-edit-the-etchosts-file)
    - [3. Start the generator](#3-start-the-generator)
    - [4. Copy all Crypto files to the Pi and start the container](#4-copy-all-crypto-files-to-the-pi-and-start-the-container)
    - [5. Go on on your host](#5-go-on-on-your-host)
    - [Final Note](#final-note)
      - [ Invoke](#-invoke)
      - [ Query](#-query)

## [](#recommended-reading)Recommended Reading

Before you start this tutorial, you may want to get familiar with the basic concepts of Hyperledger Fabric. Official Hyperledger Fabric documentation provides a comprehensive source of information related to Hyperledger Fabric configuration, modes of operation and prerequisites. I recommend to read the following articles and use them as the reference when going through this tutorial.

-   Hyperledger Fabric Glossary -  [http://hyperledger-fabric.readthedocs.io/en/latest/glossary.html](http://hyperledger-fabric.readthedocs.io/en/latest/glossary.html)
-   Hyperledger Fabric Model -  [http://hyperledger-fabric.readthedocs.io/en/latest/fabric_model.html](http://hyperledger-fabric.readthedocs.io/en/latest/fabric_model.html)
-   Hyperledger Fabric Prerequisities -  [http://hyperledger-fabric.readthedocs.io/en/latest/prereqs.html](http://hyperledger-fabric.readthedocs.io/en/latest/prereqs.html)
-   Hyperledger Fabric Samples -  [https://github.com/hyperledger/fabric-samples](https://github.com/hyperledger/fabric-samples)
-   Building Your First Network -  [http://hyperledger-fabric.readthedocs.io/en/latest/build_network.html](http://hyperledger-fabric.readthedocs.io/en/latest/build_network.html)


## [](setup-your-environment)Setup Your Environment

Let's talk about the things you will need for this tutorial

### [](#docker)Docker

Docker is a tool for deploying, executing, and managing containers. Hyperledger Fabric is by default packaged as a set of Docker images and it is ready to be run as Docker container.

To install the Docker, we can go to  [Docker website](https://docs.docker.com/install/linux/docker-ce/ubuntu/):

**SETUP THE REPOSITORY**

 1. Update the `apt` package index:
	```
	$ sudo apt-get update
	```
 2. Install packages to allow `apt` to use a repository over HTTPS:
	```
	$ sudo apt-get install \
	    apt-transport-https \
	    ca-certificates \
	    curl \
	    gnupg-agent \
	    software-properties-common
	```
 3. Add Docker’s official GPG key:
	```
	$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
	```
	Verify that you now have the key with the fingerprint `9DC8 5822 9FC7 DD38 854A E2D8 8D81 803C 0EBF CD88`, by searching for the last 8 characters of the fingerprint.
	```
	$ sudo apt-key fingerprint 0EBFCD88


	pub   rsa4096 2017-02-22 [SCEA]
	      9DC8 5822 9FC7 DD38 854A  E2D8 8D81 803C 0EBF CD88
	uid           [ unknown] Docker Release (CE deb) <docker@docker.com>
	sub   rsa4096 2017-02-22 [S]
	```
 4. Use the following command to set up the  **stable**  repository.
	 ```
	 $ sudo add-apt-repository \
	    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
	    $(lsb_release -cs) \
	    stable"
	 ```

**INSTALL DOCKER ENGINE - COMMUNITY**
1.  Update the  `apt`  package index.
    ```
    $ sudo apt-get update
    ```
2.  Install the  _latest version_  of Docker Engine - Community and containerd, or go to the next step to install a specific version:
    ```
    $ sudo apt-get install docker-ce docker-ce-cli containerd.io
    ```
	 Adding your user to the “docker” group
	```
	$ sudo usermod -aG docker $USER
	```
	**After adding docker to current user group, please logout and login again.**

### [](#docker-compose)Docker Compose
Docker Compose is a tool for defining and running multi-container Docker applications. This is the case of the Hyperledger Fabric default setup.

Docker Compose is typically installed as a part of your Docker installation. If not, it is necessary to install it separately. Run  `docker-compose --version`  command to find out if Docker Compose is present on your system.

To install Docker Compose on your Ubuntu 16.04 LTS system, please follow the instructions describe below or  [follow the instruction how to install the docker compose in docker website](https://docs.docker.com/compose/install/#install-compose):

 1. Run this command to download the current stable release of Docker Compose:
	```
	$ sudo curl -L "https://github.com/docker/compose/releases/download/1.25.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
	```

2. Apply executable permissions to the binary:
	```
	$ sudo chmod +x /usr/local/bin/docker-compose
	```
	Check the docker-compose version:
	```
	$ docker-compose --version
	docker-compose version 1.25.4, build 8d51620a
	```

### [](#go-language)Golang
Since the Java Chaincode Images are not curated for ARM64 (yet), we will use Golang for our chaincodes! 

The Installation is dependent on your local system, thus please search for how to install 
```
golang-1.16.6 
```
or later. 

### [](#python-language)Python
This Tutorial makes use of a python3 script. Therefore you need to have a working python3 installation. Please refer to the official installation instructions:
- Mac OS X: [here](https://www.python.org/downloads/mac-osx/)
- Unix: [here](http://ubuntuhandbook.org/index.php/2017/07/install-python-3-6-1-in-ubuntu-16-04-lts/)
- (Windows): [here](https://www.python.org/downloads/windows/)

If python and pip are installed, you need to download one single dependency:
```
$ pip3 install ruamel.yaml
```
`ruamel.yaml` is needed to generate yaml files. That's all!

## [](#retrieve-artifacts-from-hyperledger-fabric-repositories)Retrieve Artifacts from Hyperledger Fabric Repositories
We have our first problem here. The different binaries of HLF are not available for ARM64 by default. Thus we need to resort to a cross compiled version, maintained by busan15! 

I added these binaries to the releases page of this Github Repo. You need these! Download them to a known binary place like `/usr/local/`.

For your convenience, you can add this directory with Hyperledger Fabric binaries to your **PATH** environment variables `~/.bashrc` file.
```
$ vim ~/.bashrc
```
Inside `~/.bashrc` file set the following commands:
```
export PATH=$PATH:$HOME/fabric-samples/bin
```
And then run the command `source ~/.bashrc` to rebuild the export **PATH** environment variables.

## [](#create-hyperledger-fabric-business-network)Create Hyperledger Fabric Business Network

Again, please read the README file in the master branch for more details. The following section will explain the steps necessary, to setup a HLF network on the Raspberry Pi.

### [](#download)1. Download proper Docker images to the Raspberry Pi
We need to provide ARM64 images for the Pi to run them. I added the required ARM64 images to my dockerhub repository. Feel free to pull them all: 
https://hub.docker.com/u/juliandreyer

You can also use the convenience script `pull_images_and_tag.sh`. It will perform the following steps automaticalls:
1. Pull all images
2. Tag them as `hyperleder/fabric-<image>:2.1`
3. Show them

If you want to do it manually, pull all the images and tag them via
```
docker tag juliandreyer/fabric-<image>:2.1 hyperledger/fabric-<image>:2.1
```

Verify the correct checksums via `docker images`! This is important. The Pi shall never pull the original HLF images. This is done because the merlin script and the containers will always ask for the hyperledger/ images... stupid behaviour i guess but this works.

I assume that you have the original HLF images on your host machine! Version 2.1.
### [](#edit-host)2. Edit the /etc/hosts file
We need to edit the hosts file in order to add DNS resolve to the configurator. Do the steps on your Pi and your Host machine accordingly. This assumes that you only outsource `peer1.org1` to the Pi.
**Host**
```
127.0.0.1     ca.org1.dredev.de
127.0.0.1     orderer1.dredev.de
127.0.0.1     peer0.org1.dredev.de
IP.Of.Your.Pi peer1.org1.dredev.de
```

**Pi**
```
IP.Of.Your.Host    ca.org1.dredev.de
IP.Of.Your.Host    orderer1.dredev.de
127.0.0.1          peer1.org1.dredev.de
IP.Of.Your.Host    peer0.org1.dredev.de
```
### [](#generator)3. Start the generator
If you now start the `generator.py` script on your host machine, it will (as usual) create the crypto config for you. Please specify the **Golang** chaincode when asked for it.

In the end, it will start Merlin for Channel creation and docker startup. The script will stop then! 
**! IMPORTANT !** 
The generator automatically stops the containers `peer1.org1.`and `couchdb1.org1` since these will be outsourced. You my verify that.

The output will then be something like:
```
>>> Is the block there?
[+] Yes it is, mychannel.block

>>> Done for now

>>> STOPPING PEER1 and COUCHDB1
couchdb1.org1.dredev.de
peer1.org1.dredev.de
Now go ahead an start the docker-compose file on your Pi
Ready? Press any Key to continue
```

**DO NOT** press any key yet!

### [](#copy)4. Copy all Crypto files to the Pi and start the container
This is the most cumbersome step. You have to copy over all the crypto files to the Pi. Personally, i always `scp`ed the whole `Hyperledger-Fabric2-0-configurator` folder over to the pi. Please report any issues here! 

Note that `generator.py` created a `docker-compose-pi.yaml` file, specially suited for the pi and only containing the two needed containers. Do the following after `scp`:
```
$ cd Hyperledger-Fabric2-0-configurator
$ docker-compose --file docker-compose-pi.yaml up -d
Creating network "net_byfn" with the default driver
Creating couchdb1.org1.dredev.de ... done
Creating peer1.org1.dredev.de    ... done
```
to start the containers. All done. Don't touch the Pi again!

### [](#go-on)5. Go on on your host
Now let the magic happen. Start `merlin_cont.sh` by pressing any key in the above terminal!
Merlin will continue its algorithm as usual but now it will connect to the Pi atomatically! Install and Commit may take a moment to complete.

The procedure is exactly as before. Additionally, the script will create an `invoke-pi` and `query-pi` script. These shall be copied over to the pi as well. With them, you can conveniently invoke and query the ledger from the pi!

### [](#final-note)Final Note
This is utterly unstable! This is purely experimental and not officially supported! Nevertheless i got it to work using a RPi 4 with 4GB RAM. Feel free to contact me for any issues.

I am also eager to know if there is a chance to install java chaincode on the RPi. I havent been able to get it to work unfortunately. Let me know!
#### [](#invoke) Invoke
Merlin will create a comfortable script for you which sets all of the necessary parameters for the invoke call for you. The fundamental command behind that is the following:
```
# ORDERERS stores all the tls and orderer parameters e.g. "-o localhost:7050 --tls ..."
$ peer chaincode invoke $ORDERERS -C $CHANNEL_ID -n fabric-default $PEER_CON_PARAMS -c '{"function": "createDefaultAsset", "Args":["test"]}'

2021-02-04 16:14:20.847 CET [chaincodeCmd] chaincodeInvokeOrQuery -> INFO 001 Chaincode invoke successful. result: status:200 payload:"true"
```
You can replace this call by using the generated ```invoke``` script in the following analogous way:
```
./invoke fabric-default createDefaultAsset [\"test\"]
```
(Note this only works with bash and escaped quotes)

#### [](#query) Query
Merlin will also create a comfortable script for you which sets all of the necessary parameters for the query call for you. The fundamental command behind that is the following:
```
//Query
$ export CORE_PEER_TLS_ROOTCERT_FILE=...
$ peer chaincode query -C $CHANNEL_ID -n fabric-default -c ' "function":"readDefaultAsset", "Args":["test"]}'
{"value":"test"}
```
You can replace this call by using the generated ```invoke``` script in the following analogous way:
```
./query fabric-default readDefaultAsset [\"test\"]
```
(Note this only works with bash and escaped quotes)

Now you can do your thing! Enjoy
