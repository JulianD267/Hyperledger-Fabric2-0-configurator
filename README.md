# [](#hyperledger-fabric-v20-tutorial)Hyperledger Fabric V2.0 - Create a Development Business Network on any Unix Machine

This article is a tutorial that guides you on how to create a Hyperledger Fabric v.2.x business network on any Unix machine using the development tools that are found in the Hyperledger Fabric repository. Please `git clone` this repository to your Desktop for example. It was primarily used for my Performance Evaluation within my Paper [Performance analysis of Hyperledger Fabric 2.0 Blockchain Platform](https://dl.acm.org/doi/10.1145/3417310.3431398). Though, i noticed that its potential is manifold. Feel free to fork the project on your own! Never hesitate to contact me via Github or Mail for any details. 

## TL;DR
Just execute the following command after downloading all the prerequisites down below.
```
python3 generate.py
```
and follow the instructions. A new Hyperledger Fabric network will be started!

We will go through the process of setting up the Hyperledger Fabric prerequisites and later on we define and start an example Hyperledger Fabric admin network with three organizations.

[Hyperledger Fabric V2.0 - Create a Development Business Network on any Unix Machine](#hyperledger-fabric-v20---create-a-development-business-network-on-any-unix-machine)
  - [TL;DR](#tldr)
  - [Recommended Reading](#recommended-reading)
  - [Setup Your Environment](#setup-your-environment)
    - [Docker](#docker)
    - [Docker Compose](#docker-compose)
    - [Java](#java)
    - [Python](#python)
  - [Retrieve Artifacts from Hyperledger Fabric Repositories](#retrieve-artifacts-from-hyperledger-fabric-repositories)
  - [Create Hyperledger Fabric Business Network](#create-hyperledger-fabric-business-network)
    - [What does generator.py do?](#what-does-generatorpy-do)
      - [Execution](#execution)
    - [What does Merlin do?](#what-does-merlin-do)
      - [Generate Peer and Orderer Certificates](#generate-peer-and-orderer-certificates)
      - [Create ```channel.tx``` and the Genesis Block Using the configtxgen Tool](#create-channeltx-and-the-genesis-block-using-the-configtxgen-tool)
      - [Take a look at the  `configtx.yaml`](#take-a-look-at-the--configtxyaml)
      - [Executing the configtxgen Tool](#executing-the-configtxgen-tool)
      - [Generate Anchor Peer for each Organization.](#generate-anchor-peer-for-each-organization)
    - [Start the Hyperledger Fabric network](#start-the-hyperledger-fabric-network)
      - [Modifying the `docker-compose.yaml` file](#modifying-the-docker-composeyaml-file)
      - [ Start the Docker Containers](#-start-the-docker-containers)
      - [ Setup the channel](#-setup-the-channel)
      - [ Create the channel](#-create-the-channel)
      - [ Join channel](#-join-channel)
      - [ Update anchor peers](#-update-anchor-peers)
    - [ Prepare chaincode](#-prepare-chaincode)
    - [ Install chaincode](#-install-chaincode)
      - [Approve the Chaincode](#approve-the-chaincode)
      - [ Check Commit Readiness](#-check-commit-readiness)
    - [ Instantiate/Commit chaincode](#-instantiatecommit-chaincode)
      - [ Invoke](#invoke)
      - [ Query](#query)
    - [ Connect to IBM Blockchain Platform](#-ibm-blockchain-platform)

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

### [](#java-language)Java
In this tutorial, we use java as the basis of the chaincodes in Hyperledger Fabric. For Hyperledger Fabric, jdk 8 is required.

To install the Java in the system (Ubuntu 16.04 LTS in this example), please follow the below instructions:

 1. Perform a system update.
	```
	$ sudo apt-get update
	```
 2. Install the OpenJDK 8
	```
	$ sudo apt-get install openjdk-8-jdk
	```
 3. Create the "JAVA_HOME" Variable. The JDK is default in `/usr/lib/jvm/java-8-openjdk-amd64. Please **verify** this!`

	Inside "~/.bashrc" file set the following commands:

	```
	# JAVA_HOME
	export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
	```
	Then run the command `source ~/.bashrc` to build the environment variables in the **.bashrc** file

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
Now we download and install  **Hyperledger Fabric binaries**  specific to your platform. This includes downloading of  `cryptogen`,  `configtxgen`,  `configtxlator`,  `fabric-ca-client`,  `get-docker-images.sh`,  `orderer`  and  `peer`  tools and placing them into  `bin`  directory in the directory of your choice. Besides, the script will download Hyperlerdger Docker images into your local Docker registry. This script is provided by the Hyperledger Dev Team and can be reviewed [here](https://hyperledger-fabric.readthedocs.io/en/release-2.0/install.html).

Execute the following command to download Hyperledger Fabric binaries and Docker images. Make sure that your current working directory is safe to work in, e.g. Desktop:

```
$ curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.0.1 1.4.6 0.4.18
```

**Explanation**
```
curl -sSL https://bit.ly/2ysbOFE | bash -s -- <fabric_version> <fabric-ca_version> <thirdparty_version>
```

After running the command above, it will create the required binaries for the Fabric tools.Then we can see the binary files and shell script file in the `${PWD}/fabric-samples/bin` directory. 

```
admin@ubuntu:~/fabric-samples/bin$ ls -al
total 206892
drwxr-xr-x  2 admin admin     4096 Feb 25 22:56 ./
drwxrwxr-x 17 admin admin     4096 Mar 18 08:07 ../
-rwxr-xr-x  1 admin admin 20999000 Feb 26 22:05 configtxgen*
-rwxr-xr-x  1 admin admin 17448272 Feb 26 22:05 configtxlator*
-rwxr-xr-x  1 admin admin 13344644 Feb 26 22:05 cryptogen*
-rwxr-xr-x  1 admin admin 19116716 Feb 26 22:05 discover*
-rwxr-xr-x  1 admin admin 20702242 Feb 25 22:56 fabric-ca-client*
-rwxr-xr-x  1 admin admin 24603190 Feb 25 22:56 fabric-ca-server*
-rwxr-xr-x  1 admin admin 12352844 Feb 26 22:05 idemixgen*
-rwxr-xr-x  1 admin admin 32764776 Feb 26 22:05 orderer*
-rwxr-xr-x  1 admin admin 50501032 Feb 26 22:05 peer*
```
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
This repository provides basically two files **merlin.sh** and **generator.py**. Let me first describe what those are.
For a Hyperledger Fabric Network to operate, it depends on the following files:

-   `core.yaml` (Describes the default behavior of the nodes within the network)
-   `configtx.yaml` (Describes how the transactions are verified, performed and committed)
-   `crypto-config.yaml` (Crypto configuration for all network members)
-   `docker-compose.yaml` (Defines all the services and the network itself)
-   `.env` (Needed by the docker-compose.yaml to set a crucial variable)

These files are utterly large and offer a large scale of possible customizations. The most common use case of a fabric network is
to scale it, and set it up easily by providing the number of "orderers", "peers", "organization" etc. This is not easily possible if you were to
edit the above mentioned files on your own. Therefore the **generator.py** will do all of that for you!

### [](#generator)What does generator.py do?
Using the ```requirements.txt``` file, you can easily install all the necessary dependencies for your python environment. Just setup a virtual environment or use the global installation. 
```
$ pip3 install -r requirements.txt
```
You may review the help of the generator.py
```
$ python3 generator.py -h
usage: generator.py [-h] [-o ORDERERS] [-O ORGS] [-p PEERS] [-k KAFKA]
                    [-d DOMAIN] [-c CONSORTIUM]

Automated Hyperledger Fabic Network Generator.

optional arguments:
  -h, --help     show this help message and exit
  -o ORDERERS    Number of Orderers
  -O ORGS        Number of Organizations
  -p PEERS       Number of Peers per Organization
  -k KAFKA       Number of Kafka Brokers. NOTE: If you set this, Kafka Ordering will be enabled instead of Raft!
  -d DOMAIN      The Domain that will be used
  -c CONSORTIUM  The Consortium that will be used
  -bs BLOCKSIZE  The max amount of transactions per block
  -t TIMEOUT     The timeout value in seconds until a block gets committed, if it is not filled to its blocksize
```
With the optional parameters at hand, a developer can easily customize his own Fabric Network. If **no** parameters are provided, the script will generate the following network:
- Domain "dredev.de"
- Consortium "WebConsortium"
- 2 Organizations
  - Org1MSP
  - Org2MSP
- 2 Peers per Organization with a CouchDB instance
  - Org1
    - peer0.org1.dredev.de  + CouchDB
    - peer1.org1.dredev.de  + CouchDB
  - Org2
    - peer0.org2.dredev.de  + CouchDB
    - peer1.org2.dredev.de  + CouchDB
- 4 Orderers with Raft Ordering

#### [](pyexec)Execution 
```
$ python3 generator.py
```
1. When you first start the ```generator.py``` it will first stop all running fabric containers, if there are any.
2. It will then ask you, which chaincodes should be installed onto the network using the following promt:
```
[*] Please Specify your Chaincode that you want to install. We assume that it is a Java Packet within the folder "chaincodes/java/".
Name of the folder: 
```
You can specify any arbitrary number of chaincodes, just follow along. It expects the chaincode source code to be located within the ```${PWD}/chaincode/java``` directory.

3. After specifying all the chaincodes the script will generate all the necessary files, listed above. You may review the output, as it is very verbose. You can see in detail, which configuration has been created. Note that the script will create some env variables, which are necessary for the following execution of ```merlin.sh```. This means, that you can only start ```merlin.sh``` via the generator script reliably. For your convenience, the script will also dump all the env variables for you, so you can apply them on your own. This process overall should barely take any time. In the end it will ask you the following:
```
Start Merlin now? [y/n]
Do you want Debug output? [y/n]
```

### [](merlin)What does Merlin do?
What is that all about? Well, Merlin will automatically setup, build and start the previously generated network and will also install the provided chaincodes onto it.

You can also tell Merlin to be a little more quiet by saying "n" to the previous debug output question. At the end of this tutorial, you will have constructed a running instance of Hyperledger Fabric business network, as well as installed, instantiated, and executed chaincode. Though, Merlin is more than that. Describing its whole potential, would break the bank so to say. Let me motivate that for you by giving a tutorial on how to **manually** setup a Fabric network. Then you will see that Merlin will take all of that from you!

For our tutorial we will make use of the default network, so no parameters provided.
#### [](#generate-peer-and-orderer-certificates)Generate Peer and Orderer Certificates

Nodes (such as peers and orderers) are permitted to access business networks using a membership service provider, which is typically in the form of a certificate authority. In this example, we use the development tool named  `cryptogen`  to generate the required certificates. We use a local MSP to store the certs, which are essentially a local directory structure, for each peer and orderer. In production environments, you can exploit the  `fabric-ca`  toolset introducing full-featured certificate authorities to generate the certificates.

The `cryptogen` tool uses a  `yaml`  configuration file as its configuration - based on the content of this file, the required certificates are generated. generator.py is going to create a `crypto-config.yaml`  file for our configuration. It is going to define two organizations of peers and four orderer organization.

Reference: **Hyperledger Fabric Samples**  [crypto-config.yaml](https://github.com/hyperledger/fabric-samples/blob/master/first-network/crypto-config.yaml)
Here is the listing of our  `crypto-config.yaml`  configuration file (for the purpose of simplicity, all comments are removed from this listing):
```
OrdererOrgs:
- Name: Orderer
  Domain: dredev.de
  EnableNodeOUs: true
  Specs:
  - Hostname: orderer1
  - Hostname: orderer2
  - Hostname: orderer3
  - Hostname: orderer4
  - SANS:
    - localhost
    - 127.0.0.1
PeerOrgs:
- Name: Org1
  Domain: org1.dredev.de
  EnableNodeOUs: true
  Template:
    Count: 2
    SANS:
    - localhost
    - 127.0.0.1
  Users:
    Count: 1
- Name: Org2
  Domain: org2.dredev.de
  EnableNodeOUs: true
  Template:
    Count: 2
    SANS:
    - localhost
    - 127.0.0.1
  Users:
    Count: 1
```
Note that the ```SANS``` option is really important for the TLS to work! This file is processed within Merlin in the "generateCryptoStuff" method:
```
$ cryptogen generate --config=./crypto-config.yaml
```
After running of crytogen tool you should see the following output in console:
```
>>> Generating Crypto Material
org1.dredev.de
org2.dredev.de
```
In addition, the new `crypto-config` directory has been created and contains various certificates and keys for **orderers** and **peers**.

First, let's check content under  `orderOrganizations`:
```
$ cd crypto-config/ordererOrganizations
/crypto-config/ordererOrganizations$ tree
.
└── dredev.de
    ├── ca
    │   ├── ca.dredev.de-cert.pem
    │   └── priv_sk
    ├── msp
    │   ├── admincerts
    │   │   └── Admin@dredev.de-cert.pem
    │   ├── cacerts
    │   │   └── ca.dredev.de-cert.pem
    │   └── tlscacerts
    │       └── tlsca.dredev.de-cert.pem
    ├── orderers
    │   ├── orderer1.dredev.de
    │   │   ├── msp
    │   │   │   ├── admincerts
    │   │   │   │   └── Admin@dredev.de-cert.pem
    │   │   │   ├── cacerts
    │   │   │   │   └── ca.dredev.de-cert.pem
    │   │   │   ├── keystore
    │   │   │   │   └── priv_sk
    │   │   │   ├── signcerts
    │   │   │   │   └── orderer1.dredev.de-cert.pem
    │   │   │   └── tlscacerts
    │   │   │       └── tlsca.dredev.de-cert.pem
    │   │   └── tls
    │   │       ├── ca.crt
    │   │       ├── server.crt
    │   │       └── server.key
    │   ├── orderer2.dredev.de
    │   │   ├── msp
    │   │   │   ├── admincerts
    │   │   │   │   └── Admin@dredev.de-cert.pem
    │   │   │   ├── cacerts
    │   │   │   │   └── ca.dredev.de-cert.pem
    │   │   │   ├── keystore
    │   │   │   │   └── priv_sk
    │   │   │   ├── signcerts
    │   │   │   │   └── orderer2.dredev.de-cert.pem
    │   │   │   └── tlscacerts
    │   │   │       └── tlsca.dredev.de-cert.pem
    │   │   └── tls
    │   │       ├── ca.crt
    │   │       ├── server.crt
    │   │       └── server.key
    │   ├── orderer3.dredev.de
    │   │   ├── msp
    │   │   │   ├── admincerts
    │   │   │   │   └── Admin@dredev.de-cert.pem
    │   │   │   ├── cacerts
    │   │   │   │   └── ca.dredev.de-cert.pem
    │   │   │   ├── keystore
    │   │   │   │   └── priv_sk
    │   │   │   ├── signcerts
    │   │   │   │   └── orderer3.dredev.de-cert.pem
    │   │   │   └── tlscacerts
    │   │   │       └── tlsca.dredev.de-cert.pem
    │   │   └── tls
    │   │       ├── ca.crt
    │   │       ├── server.crt
    │   │       └── server.key
    │   └── orderer4.dredev.de
    │       ├── msp
    │       │   ├── admincerts
    │       │   │   └── Admin@dredev.de-cert.pem
    │       │   ├── cacerts
    │       │   │   └── ca.dredev.de-cert.pem
    │       │   ├── keystore
    │       │   │   └── priv_sk
    │       │   ├── signcerts
    │       │   │   └── orderer4.dredev.de-cert.pem
    │       │   └── tlscacerts
    │       │       └── tlsca.dredev.de-cert.pem
    │       └── tls
    │           ├── ca.crt
    │           ├── server.crt
    │           └── server.key
    ├── tlsca
    │   ├── priv_sk
    │   └── tlsca.dredev.de-cert.pem
    └── users
        └── Admin@dredev.de
            ├── msp
            │   ├── admincerts
            │   │   └── Admin@dredev.de-cert.pem
            │   ├── cacerts
            │   │   └── ca.dredev.de-cert.pem
            │   ├── keystore
            │   │   └── priv_sk
            │   ├── signcerts
            │   │   └── Admin@dredev.de-cert.pem
            │   └── tlscacerts
            │       └── tlsca.dredev.de-cert.pem
            └── tls
                ├── ca.crt
                ├── client.crt
                └── client.key

49 directories, 47 files
```
Second, let's check content under `peerOrganizations`:
```
cd crypto-conig/peerOrganizations
/crypto-config/peerOrganizations$ tree
.
├── org1.dredev.de
│   ├── ca
│   │   ├── ca.org1.dredev.de-cert.pem
│   │   └── priv_sk
│   ├── msp
│   │   ├── admincerts
│   │   │   └── Admin@org1.dredev.de-cert.pem
│   │   ├── cacerts
│   │   │   └── ca.org1.dredev.de-cert.pem
│   │   └── tlscacerts
│   │       └── tlsca.org1.dredev.de-cert.pem
│   ├── peers
│   │   ├── peer0.org1.dredev.de
│   │   │   ├── msp
│   │   │   │   ├── admincerts
│   │   │   │   │   └── Admin@org1.dredev.de-cert.pem
│   │   │   │   ├── cacerts
│   │   │   │   │   └── ca.org1.dredev.de-cert.pem
│   │   │   │   ├── keystore
│   │   │   │   │   └── priv_sk
│   │   │   │   ├── signcerts
│   │   │   │   │   └── peer0.org1.dredev.de-cert.pem
│   │   │   │   └── tlscacerts
│   │   │   │       └── tlsca.org1.dredev.de-cert.pem
│   │   │   └── tls
│   │   │       ├── ca.crt
│   │   │       ├── server.crt
│   │   │       └── server.key
│   │   └── peer1.org1.dredev.de
│   │       ├── msp
│   │       │   ├── admincerts
│   │       │   │   └── Admin@org1.dredev.de-cert.pem
│   │       │   ├── cacerts
│   │       │   │   └── ca.org1.dredev.de-cert.pem
│   │       │   ├── keystore
│   │       │   │   └── priv_sk
│   │       │   ├── signcerts
│   │       │   │   └── peer1.org1.dredev.de-cert.pem
│   │       │   └── tlscacerts
│   │       │       └── tlsca.org1.dredev.de-cert.pem
│   │       └── tls
│   │           ├── ca.crt
│   │           ├── server.crt
│   │           └── server.key
│   ├── tlsca
│   │   ├── priv_sk
│   │   └── tlsca.org1.dredev.de-cert.pem
│   └── users
│       ├── Admin@org1.dredev.de
│       │   ├── msp
│       │   │   ├── admincerts
│       │   │   │   └── Admin@org1.dredev.de-cert.pem
│       │   │   ├── cacerts
│       │   │   │   └── ca.org1.dredev.de-cert.pem
│       │   │   ├── keystore
│       │   │   │   └── priv_sk
│       │   │   ├── signcerts
│       │   │   │   └── Admin@org1.dredev.de-cert.pem
│       │   │   └── tlscacerts
│       │   │       └── tlsca.org1.dredev.de-cert.pem
│       │   └── tls
│       │       ├── ca.crt
│       │       ├── client.crt
│       │       └── client.key
│       └── User1@org1.dredev.de
│           ├── msp
│           │   ├── admincerts
│           │   │   └── User1@org1.dredev.de-cert.pem
│           │   ├── cacerts
│           │   │   └── ca.org1.dredev.de-cert.pem
│           │   ├── keystore
│           │   │   └── priv_sk
│           │   ├── signcerts
│           │   │   └── User1@org1.dredev.de-cert.pem
│           │   └── tlscacerts
│           │       └── tlsca.org1.dredev.de-cert.pem
│           └── tls
│               ├── ca.crt
│               ├── client.crt
│               └── client.key
└── org2.dredev.de
    ├── ca
    │   ├── ca.org2.dredev.de-cert.pem
    │   └── priv_sk
    ├── msp
    │   ├── admincerts
    │   │   └── Admin@org2.dredev.de-cert.pem
    │   ├── cacerts
    │   │   └── ca.org2.dredev.de-cert.pem
    │   └── tlscacerts
    │       └── tlsca.org2.dredev.de-cert.pem
    ├── peers
    │   ├── peer0.org2.dredev.de
    │   │   ├── msp
    │   │   │   ├── admincerts
    │   │   │   │   └── Admin@org2.dredev.de-cert.pem
    │   │   │   ├── cacerts
    │   │   │   │   └── ca.org2.dredev.de-cert.pem
    │   │   │   ├── keystore
    │   │   │   │   └── priv_sk
    │   │   │   ├── signcerts
    │   │   │   │   └── peer0.org2.dredev.de-cert.pem
    │   │   │   └── tlscacerts
    │   │   │       └── tlsca.org2.dredev.de-cert.pem
    │   │   └── tls
    │   │       ├── ca.crt
    │   │       ├── server.crt
    │   │       └── server.key
    │   └── peer1.org2.dredev.de
    │       ├── msp
    │       │   ├── admincerts
    │       │   │   └── Admin@org2.dredev.de-cert.pem
    │       │   ├── cacerts
    │       │   │   └── ca.org2.dredev.de-cert.pem
    │       │   ├── keystore
    │       │   │   └── priv_sk
    │       │   ├── signcerts
    │       │   │   └── peer1.org2.dredev.de-cert.pem
    │       │   └── tlscacerts
    │       │       └── tlsca.org2.dredev.de-cert.pem
    │       └── tls
    │           ├── ca.crt
    │           ├── server.crt
    │           └── server.key
    ├── tlsca
    │   ├── priv_sk
    │   └── tlsca.org2.dredev.de-cert.pem
    └── users
        ├── Admin@org2.dredev.de
        │   ├── msp
        │   │   ├── admincerts
        │   │   │   └── Admin@org2.dredev.de-cert.pem
        │   │   ├── cacerts
        │   │   │   └── ca.org2.dredev.de-cert.pem
        │   │   ├── keystore
        │   │   │   └── priv_sk
        │   │   ├── signcerts
        │   │   │   └── Admin@org2.dredev.de-cert.pem
        │   │   └── tlscacerts
        │   │       └── tlsca.org2.dredev.de-cert.pem
        │   └── tls
        │       ├── ca.crt
        │       ├── client.crt
        │       └── client.key
        └── User1@org2.dredev.de
            ├── msp
            │   ├── admincerts
            │   │   └── User1@org2.dredev.de-cert.pem
            │   ├── cacerts
            │   │   └── ca.org2.dredev.de-cert.pem
            │   ├── keystore
            │   │   └── priv_sk
            │   ├── signcerts
            │   │   └── User1@org2.dredev.de-cert.pem
            │   └── tlscacerts
            │       └── tlsca.org2.dredev.de-cert.pem
            └── tls
                ├── ca.crt
                ├── client.crt
                └── client.key

82 directories, 78 files
```
#### [](#create-channeltx-and-the-genesis-block-using-the-configtxgen-tool)Create ```channel.tx``` and the Genesis Block Using the configtxgen Tool

Now we generated the certificates and keys, we can now use the generated `configtx.yaml`  file. This yaml file serves as input to the  `configtxgen`  tool and generates the following important artifacts such as:

-   **channel.tx**

The channel creation transaction. This transaction lets you create the Hyperledger Fabric channel. The channel is the location where the ledger exists and the mechanism that lets peers join business networks.

-   **Genesis Block**

The Genesis block is the first block in our admin. It is used to bootstrap the ordering service and holds the channel configuration.

-   **Anchor peers transactions**

The anchor peer transactions specify each Org's Anchor Peer on this channel for communicating from one organization to other one.

#### [](#creatingmodifying-configtxyaml)Take a look at the  `configtx.yaml`

The  `configtx.yaml`  file is broken into several sections, lets have a look:

`Profile`: Profiles describe the organization structure of your network.

`Organization`: The details regarding individual organizations.

`Orderer`: The details regarding the Orderer parameters.

`Application`: Application defaults - not needed for this tutorial.

Here is the listing of our  `configtx.yaml`  configuration file (for the purpose of simplicity, all comments are removed from this listing):

Reference: **Hyperledger Fabric Samples**  [configtx.yaml](https://github.com/hyperledger/fabric/blob/release-2.0/sampleconfig/configtx.yaml)
```
Organizations:
- &id006
  Name: OrdererMSP
  ID: OrdererMSP
  MSPDir: crypto-config/ordererOrganizations/dredev.de/msp
  Policies:
    Readers:
      Type: Signature
      Rule: "OR('OrdererMSP.member')"
    Writers:
      Type: Signature
      Rule: "OR('OrdererMSP.member')"
    Admins:
      Type: Signature
      Rule: "OR('OrdererMSP.admin')"
    Endorsement:
      Type: Signature
      Rule: "OR('OrdererMSP.member')"
- &id008
  Name: Org1MSP
  ID: Org1MSP
  MSPDir: crypto-config/peerOrganizations/org1.dredev.de/msp
  Policies:
    Readers:
      Type: Signature
      Rule: "OR('Org1MSP.member')"
    Writers:
      Type: Signature
      Rule: "OR('Org1MSP.member')"
    Admins:
      Type: Signature
      Rule: "OR('Org1MSP.admin')"
    Endorsement:
      Type: Signature
      Rule: "OR('Org1MSP.member')"
  AnchorPeers:
  - Host: peer0.org1.dredev.de
    Port: 7051
- &id009
  Name: Org2MSP
  ID: Org2MSP
  MSPDir: crypto-config/peerOrganizations/org2.dredev.de/msp
  Policies:
    Readers:
      Type: Signature
      Rule: "OR('Org2MSP.member')"
    Writers:
      Type: Signature
      Rule: "OR('Org2MSP.member')"
    Admins:
      Type: Signature
      Rule: "OR('Org2MSP.admin')"
    Endorsement:
      Type: Signature
      Rule: "OR('Org2MSP.member')"
  AnchorPeers:
  - Host: peer0.org2.dredev.de
    Port: 7051
Capabilities:
  Channel: &id003
    V2_0: true
  Orderer: &id002
    V2_0: true
  Application: &id001
    V2_0: true
Application: &id010
  ACLs:
    _lifecycle/CheckCommitReadiness: /Channel/Application/Writers
    _lifecycle/CommitChaincodeDefinition: /Channel/Application/Writers
    _lifecycle/QueryChaincodeDefinition: /Channel/Application/Readers
    _lifecycle/QueryChaincodeDefinitions: /Channel/Application/Readers
    lscc/ChaincodeExists: /Channel/Application/Readers
    lscc/GetDeploymentSpec: /Channel/Application/Readers
    lscc/GetChaincodeData: /Channel/Application/Readers
    lscc/GetInstantiatedChaincodes: /Channel/Application/Readers
    qscc/GetChainInfo: /Channel/Application/Readers
    qscc/GetBlockByNumber: /Channel/Application/Readers
    qscc/GetBlockByHash: /Channel/Application/Readers
    qscc/GetTransactionByID: /Channel/Application/Readers
    qscc/GetBlockByTxID: /Channel/Application/Readers
    cscc/GetConfigBlock: /Channel/Application/Readers
    cscc/GetConfigTree: /Channel/Application/Readers
    cscc/SimulateConfigTreeUpdate: /Channel/Application/Readers
    peer/Propose: /Channel/Application/Writers
    peer/ChaincodeToChaincode: /Channel/Application/Readers
    event/Block: /Channel/Application/Readers
    event/FilteredBlock: /Channel/Application/Readers
  Organizations:
  Policies:
    LifecycleEndorsement:
      Type: ImplicitMeta
      Rule: "MAJORITY Endorsement"
    Endorsement:
      Type: ImplicitMeta
      Rule: "MAJORITY Endorsement"
    Readers:
      Type: ImplicitMeta
      Rule: "ANY Readers"
    Writers:
      Type: ImplicitMeta
      Rule: "ANY Writers"
    Admins:
      Type: ImplicitMeta
      Rule: "MAJORITY Admins"
  Capabilities:
    <<: *id001
Orderer: &id005
  Addresses:
  - orderer1.dredev.de:7050
  - orderer2.dredev.de:7050
  - orderer3.dredev.de:7050
  - orderer4.dredev.de:7050
  BatchTimeout: 1s
  BatchSize:
    MaxMessageCount: 10
    AbsoluteMaxBytes: 10 MB
    PreferredMaxBytes: 2 MB
  MaxChannels: 0
  Organizations:
  Policies:
    Readers:
      Type: ImplicitMeta
      Rule: "ANY Readers"
    Writers:
      Type: ImplicitMeta
      Rule: "ANY Writers"
    Admins:
      Type: ImplicitMeta
      Rule: "MAJORITY Admins"
    BlockValidation:
      Type: ImplicitMeta
      Rule: "ANY Writers"
  Capabilities:
    <<: *id002
  OrdererType: etcdraft
  EtcdRaft: &id007
    Consenters:
    - Host: orderer1.dredev.de
      Port: 7050
      ClientTLSCert: crypto-config/ordererOrganizations/dredev.de/orderers/orderer1.dredev.de/tls/server.crt
      ServerTLSCert: crypto-config/ordererOrganizations/dredev.de/orderers/orderer1.dredev.de/tls/server.crt
    - Host: orderer2.dredev.de
      Port: 7050
      ClientTLSCert: crypto-config/ordererOrganizations/dredev.de/orderers/orderer2.dredev.de/tls/server.crt
      ServerTLSCert: crypto-config/ordererOrganizations/dredev.de/orderers/orderer2.dredev.de/tls/server.crt
    - Host: orderer3.dredev.de
      Port: 7050
      ClientTLSCert: crypto-config/ordererOrganizations/dredev.de/orderers/orderer3.dredev.de/tls/server.crt
      ServerTLSCert: crypto-config/ordererOrganizations/dredev.de/orderers/orderer3.dredev.de/tls/server.crt
    - Host: orderer4.dredev.de
      Port: 7050
      ClientTLSCert: crypto-config/ordererOrganizations/dredev.de/orderers/orderer4.dredev.de/tls/server.crt
      ServerTLSCert: crypto-config/ordererOrganizations/dredev.de/orderers/orderer4.dredev.de/tls/server.crt
Channel: &id004
  Policies:
    Readers:
      Type: ImplicitMeta
      Rule: "ANY Readers"
    Writers:
      Type: ImplicitMeta
      Rule: "ANY Writers"
    Admins:
      Type: ImplicitMeta
      Rule: "MAJORITY Admins"
  Capabilities:
    <<: *id003
Profiles:
  OrdererDefault:
    <<: *id004
    Capabilities:
      <<: *id003
    Orderer:
      <<: *id005
      Addresses:
      - orderer1.dredev.de:7050
      - orderer2.dredev.de:7050
      - orderer3.dredev.de:7050
      - orderer4.dredev.de:7050
      Organizations:
      - *id006
      Capabilities:
        <<: *id002
      OrdererType: etcdraft
      EtcdRaft: *id007
    Consortiums:
      WebConsortium:
        Organizations:
        - *id008
        - *id009
  MainChannel:
    <<: *id004
    Consortium: WebConsortium
    Application:
      <<: *id010
      Organizations:
      - *id008
      - *id009
    Capabilities:
      <<: *id001
```
You can review the file or can modify it as necessary. However, the following items are key modifications:

-   The organizations that we specified in the profiles section are named exactly as we named them in the  `cryptogen`  tool and its  `crypto-config.yaml`  configuration file.
-   We modified the ID and Name fields to append MSP for the peers.
-   We modified the MSPDir to point to the output directories from the  `cryptogen tool`.
-   The amount of orderers and Consortium names are defined

#### [](#exec-configtxgen)Executing the configtxgen Tool

You need to set the `FABRIC_CFG_PATH` to point to the `configtx.yaml` first. This is done within Merlin automatically:
```
export FABRIC_CFG_PATH=$PWD
```
Note:  `$PWD=~/Desktop/Hyperledger-Fabric2-0-configurator/`

To create orderer genesis block, Merlin runs the following commands. This is done within the ordererchannel:
```
# Generate the Genesis Block
# ORDERERPROFILE is 'OrdererDefault'
$ configtxgen -profile $ORDERERPROFILE -outputBlock ./config/genesis.block -channelID ordererchannel
```
Output:
```
$ configtxgen -profile $ORDERERPROFILE -outputBlock ./config/genesis.block -channelID ordererchannel
[*] Generating channel.tx, genesis.block, anchor peers 
2021-02-04 11:08:14.530 CET [common.tools.configtxgen] main -> INFO 001 Loading configuration
2021-02-04 11:08:14.559 CET [common.tools.configtxgen.localconfig] completeInitialization -> INFO 002 orderer type: etcdraft
2021-02-04 11:08:14.560 CET [common.tools.configtxgen.localconfig] completeInitialization -> INFO 003 Orderer.EtcdRaft.Options unset, setting to tick_interval:"500ms" election_tick:10 heartbeat_tick:1 max_inflight_blocks:5 snapshot_interval_size:16777216 
2021-02-04 11:08:14.560 CET [common.tools.configtxgen.localconfig] Load -> INFO 004 Loaded configuration: configtx.yaml
2021-02-04 11:08:14.562 CET [common.tools.configtxgen] doOutputBlock -> INFO 005 Generating genesis block
2021-02-04 11:08:14.562 CET [common.tools.configtxgen] doOutputBlock -> INFO 006 Writing genesis block
		[+] genesis.block created 
```
After we created the orderer genesis block it is a time to create channel configuration transaction.
```
# Generate channel configuration transaction
# MAINPROFILE is 'MainChannel'
$ configtxgen -profile $MAINPROFILE -outputCreateChannelTx ./config/channel.tx -channelID mychannel
```
Output:
```
$ configtxgen -profile $MAINPROFILE -outputCreateChannelTx ./config/channel.tx -channelID mychannel
2021-02-04 11:08:14.584 CET [common.tools.configtxgen] main -> INFO 001 Loading configuration
2021-02-04 11:08:14.605 CET [common.tools.configtxgen.localconfig] Load -> INFO 002 Loaded configuration: configtx.yaml
2021-02-04 11:08:14.605 CET [common.tools.configtxgen] doOutputChannelCreateTx -> INFO 003 Generating new channel configtx
2021-02-04 11:08:14.607 CET [common.tools.configtxgen] doOutputChannelCreateTx -> INFO 004 Writing new channel tx
		[+] channel.tx created
```
The last operation we are going to perform with  `configtxgen`  is the definition of anchor peers for our organizations. This is especially important if there are more peers belonging to a single organization.

Merlin runs the following two commands to define anchor peers for **each organization**. Note that the  `asOrg`  parameter refers to the MSP ID definitions in  `configtx.yaml`. Every Organization is named "Org{Nr}MSP", with Nr being an incrementing integer beginning with 1.

#### [](#anchor-peer-generate)Generate Anchor Peer for each Organization.
```
# Generate anchor peer transaction for Org1
$ configtxgen -profile $MAINPROFILE -outputAnchorPeersUpdate ./config/Org${i}MSPanchors.tx -channelID ${CHANNEL_ID} -asOrg Org${i}MSP
```
Output:
```
$ configtxgen -profile $MAINPROFILE -outputAnchorPeersUpdate ./config/Org${i}MSPanchors.tx -channelID ${CHANNEL_ID} -asOrg Org${i}MSP
2021-02-04 11:08:14.629 CET [common.tools.configtxgen] main -> INFO 001 Loading configuration
2021-02-04 11:08:14.650 CET [common.tools.configtxgen.localconfig] Load -> INFO 002 Loaded configuration: configtx.yaml
2021-02-04 11:08:14.650 CET [common.tools.configtxgen] doOutputAnchorPeersUpdate -> INFO 003 Generating anchor peer update
2021-02-04 11:08:14.652 CET [common.tools.configtxgen] doOutputAnchorPeersUpdate -> INFO 004 Writing anchor peer update
		[+] anchor peers for Org1MSP created 
2021-02-04 11:08:14.673 CET [common.tools.configtxgen] main -> INFO 001 Loading configuration
2021-02-04 11:08:14.695 CET [common.tools.configtxgen.localconfig] Load -> INFO 002 Loaded configuration: configtx.yaml
2021-02-04 11:08:14.695 CET [common.tools.configtxgen] doOutputAnchorPeersUpdate -> INFO 003 Generating anchor peer update
2021-02-04 11:08:14.696 CET [common.tools.configtxgen] doOutputAnchorPeersUpdate -> INFO 004 Writing anchor peer update
		[+] anchor peers for Org2MSP created
```
List files generated by `configtxgen` inside `config` folder.
```
$ ls -al config
total 32
drwxr-x---   6 admin  staff   192B  1 Apr 12:19 ./
drwxr-xr-x  20 admin  staff   640B  1 Apr 12:19 ../
-rw-r-----   1 admin  staff   310B  1 Apr 12:19 Org1MSPanchors.tx
-rw-r-----   1 admin  staff   310B  1 Apr 12:19 Org2MSPanchors.tx
-rw-r-----   1 admin  staff   1,6K  1 Apr 12:19 channel.tx
-rw-r-----   1 admin  staff   9,3K  1 Apr 12:19 genesis.block
```
### [](#start-the-hyperledger-fabric-admin-network)Start the Hyperledger Fabric network
Now everything is essentially ready to start. Now to start our network we will use  `docker-compose`  tool. Based on its configuration, we launch containers based on the Docker images we downloaded in the beginning. Merlin is doing that automatically for you!

#### [](#modifying-the-docker-compose-yaml-files)Modifying the `docker-compose.yaml` file

`docker-compose`  tools is using yaml configuration files where various aspects of the containers and their network connection are defined. You can start with configuration yaml file from scratch or leverage yaml configuration from the "first-network" example.

The ```generator.py``` creates the `.env` file in current directory. There are many environment variables for using with the Docker Compose file.

Inside `.env` file set the following variable.
```
COMPOSE_PROJECT_NAME=net
```
The `docker-compose.yaml` content showed by the following (some servicess omitted):

Reference: **Hyperledger Fabric Samples**  [docker-compose-ca.yaml](https://github.com/hyperledger/fabric-samples/blob/release-1.4/first-network/docker-compose-ca.yaml) and other compose files.
```
version: '2'
networks:
  byfn:
services:
  ca.org1.dredev.de:
    image: hyperledger/fabric-ca:1.4
    environment:
    - FABRIC_CA_HOME=/etc/hyperledger/fabric-ca-server
    - FABRIC_CA_SERVER_CA_NAME=ca.org1.dredev.de
    - FABRIC_CA_SERVER_CA_CERTFILE=/etc/hyperledger/fabric-ca-server-config/ca.org1.dredev.de-cert.pem
    - FABRIC_CA_SERVER_CA_KEYFILE=/etc/hyperledger/fabric-ca-server-config/priv_sk
    - FABRIC_CA_SERVER_TLS_ENABLED=true
    - FABRIC_CA_SERVER_TLS_CERTFILE=/etc/hyperledger/fabric-ca-server-config/ca.org1.dredev.de-cert.pem
    - FABRIC_CA_SERVER_TLS_KEYFILE=/etc/hyperledger/fabric-ca-server-config/priv_sk
    ports:
    - 7054:7054
    command: sh -c 'fabric-ca-server start --ca.certfile /etc/hyperledger/fabric-ca-server-config/ca.org1.dredev.de-cert.pem
      --ca.keyfile /etc/hyperledger/fabric-ca-server-config/priv_sk -b admin:adminpw
      -d'
    volumes:
    - ./crypto-config/peerOrganizations/org1.dredev.de/ca/:/etc/hyperledger/fabric-ca-server-config
    container_name: ca.org1.dredev.de
    networks:
    - byfn
  [...]
  orderer1.dredev.de:
    container_name: orderer1.dredev.de
    image: hyperledger/fabric-orderer:2.0
    environment:
    - ORDERER_HOST=orderer1.dredev.de
    - ORDERER_GENERAL_LOGLEVEL=debug
    - ORDERER_GENERAL_LISTENADDRESS=0.0.0.0
    - ORDERER_GENERAL_LISTENPORT=7050
    - ORDERER_GENERAL_GENESISMETHOD=file
    - ORDERER_GENERAL_GENESISFILE=/etc/hyperledger/configtx/genesis.block
    - ORDERER_GENERAL_LOCALMSPID=OrdererMSP
    - ORDERER_GENERAL_LOCALMSPDIR=/etc/hyperledger/msp/orderer/msp
    - CONFIGTX_ORDERER_BATCHTIMEOUT=1s
    - ORDERER_GENERAL_CLUSTER_CLIENTCERTIFICATE=/etc/hyperledger/orderer/tls/server.crt
    - ORDERER_GENERAL_CLUSTER_CLIENTPRIVATEKEY=/etc/hyperledger/orderer/tls/server.key
    - ORDERER_GENERAL_CLUSTER_ROOTCAS=[/etc/hyperledger/orderer/tls/ca.crt]
    - ORDERER_ABSOLUTEMAXBYTES=10 MB
    - ORDERER_PREFERREDMAXBYTES=512 KB
    - ORDERER_GENERAL_TLS_ENABLED=true
    - ORDERER_GENERAL_TLS_PRIVATEKEY=/etc/hyperledger/orderer/tls/server.key
    - ORDERER_GENERAL_TLS_CERTIFICATE=/etc/hyperledger/orderer/tls/server.crt
    - ORDERER_GENERAL_TLS_ROOTCAS=[/etc/hyperledger/orderer/tls/ca.crt]
    - CONFIGTX_ORDERER_ORDERERTYPE=etcdraft
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric/orderer
    command: orderer
    ports:
    - 7050:7050
    volumes:
    - ./config/:/etc/hyperledger/configtx
    - ./config/genesis.block:/etc/hyperledger/orderer/orderer.genesis.block
    - ./crypto-config/ordererOrganizations/dredev.de/orderers/orderer1.dredev.de/:/etc/hyperledger/msp/orderer
    - ./crypto-config/ordererOrganizations/dredev.de/orderers/orderer1.dredev.de/msp:/etc/hyperledger/orderer/msp
    - ./crypto-config/ordererOrganizations/dredev.de/orderers/orderer1.dredev.de/tls/:/etc/hyperledger/orderer/tls
    networks:
    - byfn
  [...]
  peer0.org1.dredev.de:
    container_name: peer0.org1.dredev.de
    image: hyperledger/fabric-peer:2.0
    environment:
    - CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock
    - CORE_LOGGING_PEER=debug
    - CORE_CHAINCODE_LOGGING_LEVEL=DEBUG
    - CORE_PEER_ID=peer0.org1.dredev.de
    - CORE_PEER_ADDRESS=peer0.org1.dredev.de:7051
    - CORE_PEER_LOCALMSPID=Org1MSP
    - CORE_PEER_CHAINCODEADDRESS=peer0.org1.dredev.de:7052
    - CORE_PEER_CHAINCODELISTENADDRESS=0.0.0.0:7052
    - CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/peer/
    - CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=${COMPOSE_PROJECT_NAME}_byfn
    - CORE_LEDGER_STATE_STATEDATABASE=CouchDB
    - CORE_LEDGER_STATE_COUCHDBCONFIG_COUCHDBADDRESS=couchdb0.org1.dredev.de:5984
    - CORE_LEDGER_STATE_COUCHDBCONFIG_USERNAME=
    - CORE_LEDGER_STATE_COUCHDBCONFIG_PASSWORD=
    - CORE_PEER_TLS_ENABLED=true
    - CORE_PEER_GOSSIP_USELEADERELECTION=true
    - CORE_PEER_GOSSIP_ORGLEADER=false
    - CORE_PEER_GOSSIP_BOOTSTRAP=peer0.org1.dredev.de:7051
    - CORE_PEER_GOSSIP_EXTERNALENDPOINT=peer0.org1.dredev.de:7051
    - CORE_PEER_PROFILE_ENABLED=true
    - CORE_PEER_TLS_CERT_FILE=/etc/hyperledger/fabric/tls/server.crt
    - CORE_PEER_TLS_KEY_FILE=/etc/hyperledger/fabric/tls/server.key
    - CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric
    command: peer node start
    ports:
    - 7051:7051
    volumes:
    - /var/run/:/host/var/run/
    - ./crypto-config/peerOrganizations/org1.dredev.de/peers/peer0.org1.dredev.de/msp:/etc/hyperledger/msp/peer
    - ./crypto-config/peerOrganizations/org1.dredev.de/peers/peer0.org1.dredev.de/tls:/etc/hyperledger/fabric/tls
    - ./crypto-config/peerOrganizations/org1.dredev.de/users:/etc/hyperledger/msp/users
    - ./config:/etc/hyperledger/configtx
    depends_on:
    - couchdb0.org1.dredev.de
    networks:
    - byfn
  couchdb0.org1.dredev.de:
    container_name: couchdb0.org1.dredev.de
    image: hyperledger/fabric-couchdb
    environment:
    - COUCHDB_USER=
    - COUCHDB_PASSWORD=
    ports:
    - 5984:5984
    networks:
    - byfn
  [...]
  cli:
    container_name: cli
    image: hyperledger/fabric-tools
    tty: true
    environment:
    - GOPATH=/opt/gopath
    - CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock
    - FABRIC_LOGGING_SPEC=DEBUG
    - CORE_PEER_ID=cli
    - CORE_PEER_ADDRESS=peer0.org1.dredev.de:7051
    - CORE_PEER_LOCALMSPID=Org1MSP
    - CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dredev.de/users/Admin@org1.dredev.de/msp
    - CORE_PEER_TLS_ENABLED=true
    - CORE_PEER_TLS_CERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dredev.de/peers/peer0.org1.dredev.de/tls/server.crt
    - CORE_PEER_TLS_KEY_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dredev.de/peers/peer0.org1.dredev.de/tls/server.key
    - CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dredev.de/peers/peer0.org1.dredev.de/tls/ca.crt
    - CORE_CHAINCODE_KEEPALIVE=10
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric/peer
    command: /bin/bash
    volumes:
    - /var/run/:/host/var/run/
    - ./chaincodes/java:/opt/gopath/src/github.com/chaincodes/java
    - ./crypto-config:/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/
    - ./config:/etc/hyperledger/configtx
    networks:
    - byfn
    depends_on:
    - orderer1.dredev.de
    - orderer2.dredev.de
    - orderer3.dredev.de
    - orderer4.dredev.de
    - peer0.org1.dredev.de
    - couchdb0.org1.dredev.de
    - peer1.org1.dredev.de
    - couchdb1.org1.dredev.de
    - peer0.org2.dredev.de
    - couchdb0.org2.dredev.de
    - peer1.org2.dredev.de
    - couchdb1.org2.dredev.de

```

This yaml file is generated by generator.py. It makes some assumptions though. The default ports for the Containers are fixed and COULD be modified. This may or may not work, no guarantee for that! The Network name is "byfn". This can definitely be changed within the generator.py! The Ports, which are exposed to the main host, are determined by some simple maths. Assuming the id (an integer >=1) of the organization is stored in "org" and the peer number (an integer), beginning with 0 is stored in "peer", the port of the peer is determined in the following way:
```
port=$(( 7051+1000*(($NO_PEERS*($org -1))+$peer) ))
```
You can look at the results within the docker-compose.yaml. No ports should overlap with this!

#### [](#start-containers) Start the Docker Containers

After we have generated the certificates, the genesis block, the channel transaction configuration, and created or modified the appropriate yaml files, we are read to start our network. Use the following command to start the network.

```
# Or the Default file of the docker-compose is docker-compose.yaml so we don't need to specify the file name
$ docker-compose up -d
```
Merlin Output:
```
>>> I will now start all the containers! Docker do your thing!
Creating network "net_byfn" with the default driver
Creating orderer3.dredev.de      ... done
Creating couchdb1.org2.dredev.de ... done
Creating orderer2.dredev.de      ... done
Creating orderer1.dredev.de      ... done
Creating orderer4.dredev.de      ... done
Creating ca.org1.dredev.de       ... done
Creating ca.org2.dredev.de       ... done
Creating couchdb0.org1.dredev.de ... done
Creating couchdb0.org2.dredev.de ... done
Creating couchdb1.org1.dredev.de ... done
Creating peer1.org2.dredev.de    ... done
Creating peer0.org1.dredev.de    ... done
Creating peer0.org2.dredev.de    ... done
Creating peer1.org1.dredev.de    ... done
Creating cli                     ... done
>>> Now please give the containers a short amount of time to start. Some Seconds should be enough
```

You can use `docker ps` command to list the running containers. In our case, you should see the following containers running:
-   2 peers in each organization
-   1 couchDB in each peer
-   4 orderer nodes
-   1 CA for each Org
-   1 CLI

#### [](#the-channel) Setup the channel

After the Docker containers started, we can use the  **Command Line Interface (CLI)** ,  **Fabric SDK** or the good old **Terminal** to interact with the admin network. In this tutorial we use the  **Terminal**  to interact with the admin network. Note that all the necessary tools need to be within the PATH variable!

You can interact with the other peers by prefixing our peer commands with the appropriate environment variables. Usually, this means pointing to the certificates for that peer. You need to do that whenever you want to change the peer. Merlin has an integrated method to perform this change called "changeOrg".

Here is the list of environment variables that **need to be used as the prefix** for peer commands when interacting with peer0 of Org1, peer1 of Org1, peer0 of Org2 and peer1 of Org2 organization respectively. After setting these variables, you sort of "imitate" to be that peer. Then you can interact with the network. Merlin does that automagically

**Peer0 of Org1**
```
# Peer0 of Org1 organization
CORE_PEER_LOCALMSPID=Org1MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org1.dredev.de/users/Admin@org1.dredev.de/msp
CORE_PEER_TLS_ENABLED=true
CORE_PEER_ADDRESS=localhost:7051
CORE_PEER_TLS_ROOTCERT_FILE=/./crypto-config/peerOrganizations/org1.dredev.de/peers/peer0.org1.dredev.de/tls/ca.crt
```
**Peer1 of Org2**
```
# Peer1 of Org2 organization
CORE_PEER_LOCALMSPID=Org2MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org2.dredev.de/users/Admin@org2.dredev.de/msp
CORE_PEER_TLS_ENABLED=true
CORE_PEER_TLS_ROOTCERT_FILE=/./crypto-config/peerOrganizations/org2.dredev.de/peers/peer1.org2.dredev.de/tls/ca.crt
CORE_PEER_ADDRESS=localhost:10051
```
... you get it?

#### [](#create-channel) Create the channel

The first command that we issue is the  `peer create channel`  command. This command targets one of the orderers (where the channels must be created) and uses the  `channel.tx`  and the channel name that is created using the  `configtxgen`  tool. To create the channel, run the following command to create the channel called `mychannel`. Note that TLS needs to be enabled:
```
# peer channel create \
   -o localhost:7050 --tls --ordererTLSHostnameOverride orderer1.dredev.de --cafile=./crypto-config/ordererOrganizations/dredev.de/orderers/orderer1.dredev.de/msp/tlscacerts/tlsca.dredev.de-cert.pem \
   -c mychannel \
   -f ./configtx/channel.tx
```
Merlin Output:
```
22021-02-04 11:08:34.936 CET [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2021-02-04 11:08:34.987 CET [cli.common] readBlock -> INFO 002 Expect block, but got status: &{SERVICE_UNAVAILABLE}
2021-02-04 11:08:34.990 CET [channelCmd] InitCmdFactory -> INFO 003 Endorser and orderer connections initialized
2021-02-04 11:08:35.192 CET [cli.common] readBlock -> INFO 004 Expect block, but got status: &{SERVICE_UNAVAILABLE}
2021-02-04 11:08:35.195 CET [channelCmd] InitCmdFactory -> INFO 005 Endorser and orderer connections initialized
2021-02-04 11:08:35.396 CET [cli.common] readBlock -> INFO 006 Expect block, but got status: &{SERVICE_UNAVAILABLE}
2021-02-04 11:08:35.399 CET [channelCmd] InitCmdFactory -> INFO 007 Endorser and orderer connections initialized
2021-02-04 11:08:35.605 CET [cli.common] readBlock -> INFO 008 Expect block, but got status: &{SERVICE_UNAVAILABLE}
2021-02-04 11:08:35.608 CET [channelCmd] InitCmdFactory -> INFO 009 Endorser and orderer connections initialized
2021-02-04 11:08:35.812 CET [cli.common] readBlock -> INFO 00a Expect block, but got status: &{SERVICE_UNAVAILABLE}
2021-02-04 11:08:35.815 CET [channelCmd] InitCmdFactory -> INFO 00b Endorser and orderer connections initialized
2021-02-04 11:08:36.023 CET [cli.common] readBlock -> INFO 00c Received block: 0
>>> Is the block there?
[+] Yes it is, mychannel.block
```
The `peer channel create` command returns a `genesis block` which will be used to join the channel. Merlin automatically checks, whether this block exists. In the above case, everything worked fine!

#### [](#join-channel) Join channel

After the orderer creates the channel, the peers have to join the channel. Each peer has to execute the following command, using the above mentioned "change" of env variables for the peer.
```
# To join the channel.
peer channel join --tls -b mychannel.block
```
Merlin Output:
```
>>> Joining Channel mychannel on each Peer 
[*] Start Joining of Channel mychannel 
		[*] Attempting Channel join for peer0.org1.dredev.de 
2021-02-04 11:08:37.710 CET [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2021-02-04 11:08:37.812 CET [channelCmd] executeJoin -> INFO 002 Successfully submitted proposal to join channel
		[+] Channel join succeeded on peer0.org1.dredev.de 
		[*] Attempting Channel join for peer1.org1.dredev.de 
2021-02-04 11:08:37.851 CET [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2021-02-04 11:08:38.459 CET [channelCmd] executeJoin -> INFO 002 Successfully submitted proposal to join channel
		[+] Channel join succeeded on peer1.org1.dredev.de 
		[*] Attempting Channel join for peer0.org2.dredev.de 
2021-02-04 11:08:38.498 CET [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2021-02-04 11:08:38.605 CET [channelCmd] executeJoin -> INFO 002 Successfully submitted proposal to join channel
		[+] Channel join succeeded on peer0.org2.dredev.de 
		[*] Attempting Channel join for peer1.org2.dredev.de 
2021-02-04 11:08:38.642 CET [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2021-02-04 11:08:38.748 CET [channelCmd] executeJoin -> INFO 002 Successfully submitted proposal to join channel
		[+] Channel join succeeded on peer1.org2.dredev.de 
[+] Joining succeeded 
```

#### [](#update-anchor-peers) Update anchor peers
Now we need to update the anchor peers of each organization, so for both org1 and org2. Note that the Anchor peers per default are the "peer0" peers of each organization.
To update Anchor Peer for Org1 Organization.
```
# Set Environment Variable to Peer0 in Org1 Organization
CORE_PEER_LOCALMSPID=Org1MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org1.dredev.de/users/Admin@org1.dredev.de/msp
CORE_PEER_TLS_ENABLED=true
CORE_PEER_ADDRESS=localhost:7051
CORE_PEER_TLS_ROOTCERT_FILE=/./crypto-config/peerOrganizations/org1.dredev.de/peers/peer0.org1.dredev.de/tls/ca.crt

# To update the Anchor Peer
peer channel update \
    -o localhost:7050 --tls --ordererTLSHostnameOverride orderer1.dredev.de --cafile=./crypto-config/ordererOrganizations/dredev.de/orderers/orderer1.dredev.de/msp/tlscacerts/tlsca.dredev.de-cert.pem \
    -c ${CHANNEL_ID} \
    -f ./config/Org1MSPanchors.tx
```
Merlin Output:
```
[*] Attempting Anchor Update for peer0.org1.dredev.de 
Org1MSP Hyperledger-Fabric2-0-configurator/crypto-config/peerOrganizations/org1.dredev.de/users/Admin@org1.dredev.de/msp localhost:7051
2021-02-04 11:08:39.787 CET [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2021-02-04 11:08:39.811 CET [channelCmd] update -> INFO 002 Successfully submitted channel update
[+] Anchor Update succeeded on peer0.org1.dredev.de 
```
Repeat the same steps for the Anchor Peer of Org2 Organization by setting the env vars and execute the same customized command for anchor peer update.

### [](#prepare-chaincode) Prepare chaincode
With Fabric 2.0, the Chaincode needs to be packaged within a ```tar.gz``` archive before deployment. Therefore the code needs to be compiled first. Merlin does that automatically for us. Though, there is a little incompatibility problem here. Due to some misconfigurations of gradle and other fabric versions, some build pattens for the ```.jar``` generation require the ```install``` pattern, more modern chaincodes require the ```shadowJar``` pattern. So, to cope for that, Merlin will try both!
```
pushd chaincodes/<chaincode>
./gradlew clean build installDist // For java
# Or
./gradlew clean build shadowJar
popd
```

Now the Code needs to be packaged with the help of the `peer lifecycle chaincode package` command. First though, we need to set the source path for the chaincode and the package name.
Replace <chaincodename> with the appropriate name of the chaincode, e.g. fabric-authtoken.
```
export CC_SRC_PATH=<path to Chaincode dir>
export VERSION=1
export PKG_FILE=<chaincodename>.tar.gz
peer lifecycle chaincode package ${PKG_FILE} --path ${CC_SRC_PATH} --lang ${CC_RUNTIME_LANGUAGE} --label <chaincodename>_${VERSION}
```
Now a new tar File called has been created within the current directory. This can now be installed onto the peers of the network.
Merlin Output:
```
>>> The Chaincodes now get packaged. This is done with the new lifecycle management.
[*] Start building using gradle
	[*] Build fabric-default
  ~/Desktop/Hyperledger-Fabric2-0-configurator/chaincodes/java/fabric-default ~/Desktop/Hyperledger-Fabric2-0-configurator

BUILD SUCCESSFUL in 1s
6 actionable tasks: 6 executed
		[+] Gradle succeeded now 
~/Desktop/Hyperledger-Fabric2-0-configurator
    [+] Build fabric-default finished
[+] Build finished 
~/Desktop/test-network/chaincodes/java/fabric-orionACL ~/Desktop/test-network
[*] Start packaging... 
	[*] Attempting packing of fabric-default Chaincode
		[+] Packing of fabric-default Chaincode succeeded 
[+] Packing complete! 
```

### [](#install-chaincode) Install chaincode
With Fabric 2.0, chaincode needs to be installed on every peer using the new Lifecycle Management. For each peer, the command `peer lifecycle chaincode install <chaincodename>.tar.gz` needs to be executed. To achieve this, remember to change the env vars according to each peer!
```
# Peer0 - Org1
CORE_PEER_LOCALMSPID=Org1MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org1.dredev.de/users/Admin@org1.dredev.de/msp
CORE_PEER_TLS_ENABLED=true
CORE_PEER_ADDRESS=localhost:7051
CORE_PEER_TLS_ROOTCERT_FILE=/./crypto-config/peerOrganizations/org1.dredev.de/peers/peer0.org1.dredev.de/tls/ca.crt
$ peer lifecycle chaincode install ${PKG_FILE}
[... repeat for each peer ...]
```
Merlin Output (omitted):
```
  [*] Attempting install on peer0.org1.dredev.de
[*] Attempting install on peer0.org1.dredev.de 
2021-02-04 11:08:49.282 CET [cli.lifecycle.chaincode] submitInstallProposal -> INFO 001 Installed remotely: response:<status:200 payload:"\nQfabric-default_1:3721039871b8d6df7e35fb8d2ae7bbfa3ff46e2f7fc11576572f6fc47c474c86\022\020fabric-default_1" > 
2021-02-04 11:08:49.283 CET [cli.lifecycle.chaincode] submitInstallProposal -> INFO 002 Chaincode code package identifier: fabric-default_1:3721039871b8d6df7e35fb8d2ae7bbfa3ff46e2f7fc11576572f6fc47c474c86
	[+] Install on peer0.org1.dredev.de  finished 
  ...
```
The Output of the above commands should result in a Package ID: ...
The following text can be extracted using ```sed```. Merlin does that for you.
The identifier is now being used to verify the installed chaincode:
```
$ peer lifecycle chaincode queryinstalled
Installed chaincodes on peer:
Package ID: fabric-default_1:3721039871b8d6df7e35fb8d2ae7bbfa3ff46e2f7fc11576572f6fc47c474c86, Label: fabric-default_1
```
Merlin is automatically extracting the id and storing it in an appropriate variable for later use. This is a quite involved process.

#### [](#approve-the-chaincode)Approve the Chaincode
With the chaincode being installed onto each peer, we need to approve the installation
of the chaincode with the organizations and the orderers. So this needs to be executed for every organization!
```
<change env here>
$ peer lifecycle chaincode approveformyorg 
                    -o localhost:7050 --tls --ordererTLSHostnameOverride orderer1.dredev.de --cafile=./crypto-config/ordererOrganizations/dredev.de/orderers/orderer1.dredev.de/msp/tlscacerts/tlsca.dredev.de-cert.pem \
                    --channelID mychannel
                    --name fabric-default
                    --version 1 
                    --package-id $(sed -n "/${chaincode}_1/{s/^Package ID: //; s/, Label:.*$//; p;}" log.txt) 
                    --sequence 1 
                    --waitForEvent
# repeat for Org2
```
The output should indicate a success with status (VALID) in both cases! Like this:
```
[[*] Start approving... 
		[*] Org1 is approving ... 
2021-02-04 11:08:54.572 CET [chaincodeCmd] ClientWait -> INFO 001 txid [ba69727ca8c154cb6557d2776238c855fe148f145a3b4be0214588cdf5e54377] committed with status (VALID) at 
		[*] Org2 is approving ... 
2021-02-04 11:08:55.761 CET [chaincodeCmd] ClientWait -> INFO 001 txid [403f9d84f67c76b46f2d45af2a693e3ffda6b2da012cbbd62a23fa89884c51be] committed with status (VALID) at 
[+] Approving complete. 
```

#### [](#check-commit-readiness) Check Commit Readiness
If both Organizations approve the Chaincode, we can now check, whether they are ready for the chaincode to be committed. The command `peer lifecycle chaincode checkcommitreadiness --channelID mychannel --name <chaincodename> --version 1 --sequence 1 --output json` code should return the following:
```
$ peer lifecycle chaincode checkcommitreadiness --channelID mychannel --name fabcar --version 1 --sequence 1 --output json --init-required
[*] Checking commit readiness for fabric-default... 
{
	"approvals": {
		"Org1MSP": true,
		"Org2MSP": true
	}
}
>>> JSON with true everywhere? 
```
Both Orgs approved the Chaincode! There should not be a "false"!

### [](#instantiate-chaincode) Instantiate/Commit chaincode
With Fabric 2.0, there has been a change to the Instantiation Paradigm. The Chaincode now needs to be committed to the Channel first,
then it is being invoked. The following code is expecting the `PEER_CON_PARAMS` to be set! Refer to the Merlin script for an in-detail description. Generally this variable includes the necessary connection information of the peers within the network.
```
$ peer lifecycle chaincode commit -o localhost:7050 
                                  --tls           
                                  --ordererTLSHostnameOverride orderer1.dredev.de --cafile=./crypto-config/ordererOrganizations/dredev.de/orderers/orderer1.dredev.de/msp/tlscacerts/tlsca.dredev.de-cert.pem \
                                  --channelID mychannel\
                                  --name fabric-default\
                                  $PEER_CON_PARAMS\
                                  --version 1\
```
Merlin Output:
```
[*] Start committing... 
	[*] Commit fabric-default... 
2021-02-04 11:08:59.061 CET [chaincodeCmd] ClientWait -> INFO 001 txid [0a84051989e5181c4db56968e32da29614267226c40a095844b353d1c600fb01] committed with status (VALID) at localhost:8051
2021-02-04 11:08:59.071 CET [chaincodeCmd] ClientWait -> INFO 002 txid [0a84051989e5181c4db56968e32da29614267226c40a095844b353d1c600fb01] committed with status (VALID) at localhost:7051
2021-02-04 11:08:59.074 CET [chaincodeCmd] ClientWait -> INFO 003 txid [0a84051989e5181c4db56968e32da29614267226c40a095844b353d1c600fb01] committed with status (VALID) at localhost:9051
2021-02-04 11:08:59.116 CET [chaincodeCmd] ClientWait -> INFO 004 txid [0a84051989e5181c4db56968e32da29614267226c40a095844b353d1c600fb01] committed with status (VALID) at localhost:10051
	[+] Committing complete!
```


We can now see whether the CC has been committed to the ledger:
```
$ peer lifecycle chaincode querycommitted --channelID mychannel --name <chaincodename>
```
Merlin Output:
```
 =<=<=<=<=<=<=<=<=<=<=<=<=<=<= Chaincodes <=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=

Committed chaincode definition for chaincode 'fabric-default' on channel 'mychannel':
Version: 1, Sequence: 1, Endorsement Plugin: escc, Validation Plugin: vscc, Approvals: [Org1MSP: true, Org2MSP: true]

 =<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=
```
**That's it!** You got your own network to work with. Merlin will execute a few test transactions then:

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

## [](#-ibm-blockchain-platform)Connecting to IBM Blockchain Platform

This repository offers a convenient feature: It allows you to easily connect to the [IBM Blockchain Platform](https://github.com/IBM-Blockchain/blockchain-vscode-extension) VS Code extension. It gives you quick development access to your new Fabric network!

First of all, the extension allows you to connect to an IBM Blockchain. **BUT** it also offers to connect to a ```any other Fabric network```. For that you will need the following:
- A wallet containing all the MSP Admin identities
- A Node JSON file, containing all Nodes within the network
- A ```connection-profile.yaml``` file for the gateway connection

Conveniently, this script generates all of that for you! you will find the ```nodes.json``` file within the ```nodes/``` directory, the wallet identities within the ```wallet/``` directory and the ```connection-profile.yaml``` file within the root directory after generation. These can be imported directly. 

1. Add the Wallet within the IBM Blockchain Platform extension 
- ```Fabric-Wallets->Specify an existing File System Wallet ``` and pick the ```wallets``` folder
2. Add the network nodes
- ```Fabric-Environments->Add any other Fabric network``` give it a name and pick the ```nodes/nodes.json``` file.
3. Add the gateway
- ```Fabric-Gateways->Createa a gateway from a connection profile``` give it a name and pick ```connection-profile.yaml```

Finally, you can click on the Gateway and the network and interact with it! Happy interacting