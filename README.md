# [](#hyperledger-fabric-v20-tutorial)Hyperledger Fabric V2.0 - Create a Development Business Network on any Unix Machine

This article is a tutorial that guides you on how to create a Hyperledger Fabric v.2.0 business network on any Unix machine using the development tools that are found in the Hyperledger Fabric repository. Please `git clone` this repository to your Desktop for example.

## TL;DR
Just execute the following command
```
python3 generate.py
```
and follow the instructions. A new Hyperledger Fabric network will be started!

We will go through the process of setting up the Hyperledger Fabric prerequisites and later on we define and start an example Hyperledger Fabric blockchain network with three organizations.

-  [Hyperledger Fabric V2.0 - Create a Development Business Network on any Unix Machine](#hyperledger-fabric-v20-tutorial)
	 - [Recommended Reading](#recommended-reading)
-   [Setup Your Environment](#setup-your-environment)
    -   [Docker](#docker)
    -   [Docker Compose](#docker-compose)
    -   [Java](#java)
    -   [Python](#python)
-   [Retrieve Artifacts from Hyperledger Fabric Repsitories](#retrieve-artifacts-from-hyperledger-fabric-repositories)
-   [Create Hyperledger Fabric Business Network](#create-hyperledger-fabric-business-network)
    -   [Execute generator.py](#execute-generatorpy)
    -   [Generate Peer and Orderer Certificates](#generate-peer-and-orderer-certificates)
    -   [Create channel.tx and the Genesis Block Using the configtxgen Tool](#create-channeltx-and-the-genesis-block-using-the-configtxgen-tool)
        -   [Take a look at the `configtx.yaml`](#take-a-look-at-the--configtxyaml)
        -   [Executing the configtxgen Tool](#executing-the-configtxgen-tool)
        -   [Generate Anchor Peers](#generate-anchor-peer-for-each-organization)
-   [Start the Hyperledger Fabric blockchain network](#start-the-hyperledger-fabric-blockchain-network)
    -   [Modifying the docker-compose yaml Files](#modifying-the-docker-composeyaml-file)
    -   [Start the docker Containers](#-start-the-docker-containers)
    -   [The channel](#-the-channel)
        -   [Create the channel](#-create-the-channel)
        -   [Join channel](#-join-channel)
        -   [Update anchor peers](#-update-anchor-peers)
    -   [Prepare chaincode](#-prepare-chaincode)
    -   [Install chaincode](#-install-chaincode)
    -   [Instantiate/Commit chaincode](#-instantiatecommit-chaincode)
        -   [Invoke chaincode](#-invoke)
        -   [Query chaincode](#-query)


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
````

After running the command above, it will show like this:
```
Clone hyperledger/fabric-samples repo

===> Cloning hyperledger/fabric-samples repo and checkout v2.0.1
Cloning into 'fabric-samples'...
remote: Enumerating objects: 4, done.
remote: Counting objects: 100% (4/4), done.
remote: Compressing objects: 100% (4/4), done.
remote: Total 4820 (delta 0), reused 0 (delta 0), pack-reused 4816
Receiving objects: 100% (4820/4820), 1.71 MiB | 456.00 KiB/s, done.
Resolving deltas: 100% (2428/2428), done.
Checking connectivity... done.
error: pathspec 'v2.0.1' did not match any file(s) known to git.

Pull Hyperledger Fabric binaries

===> Downloading version 2.0.1 platform specific fabric binaries
===> Downloading:  https://github.com/hyperledger/fabric/releases/download/v2.0.1/hyperledger-fabric-linux-amd64-2.0.1.tar.gz
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   633  100   633    0     0   1240      0 --:--:-- --:--:-- --:--:--  1241
100 72.7M  100 72.7M    0     0   979k      0  0:01:16  0:01:16 --:--:-- 5113k
==> Done.
===> Downloading version 1.4.6 platform specific fabric-ca-client binary
===> Downloading:  https://github.com/hyperledger/fabric-ca/releases/download/v1.4.6/hyperledger-fabric-ca-linux-amd64-1.4.6.tar.gz
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   636  100   636    0     0   1363      0 --:--:-- --:--:-- --:--:--  1364
100 19.7M  100 19.7M    0     0   811k      0  0:00:24  0:00:24 --:--:-- 2225k
==> Done.

Pull Hyperledger Fabric docker images
.
.
.
===> List out hyperledger docker images
hyperledger/fabric-javaenv     2.0                 bb3837bf990f        12 days ago         505MB
hyperledger/fabric-javaenv     2.0.1               bb3837bf990f        12 days ago         505MB
hyperledger/fabric-javaenv     latest              bb3837bf990f        12 days ago         505MB
hyperledger/fabric-tools       2.0                 5c9a03790913        2 weeks ago         512MB
hyperledger/fabric-tools       2.0.1               5c9a03790913        2 weeks ago         512MB
hyperledger/fabric-tools       latest              5c9a03790913        2 weeks ago         512MB
hyperledger/fabric-peer        2.0                 5c7e5946f3dc        2 weeks ago         57.2MB
hyperledger/fabric-peer        2.0.1               5c7e5946f3dc        2 weeks ago         57.2MB
hyperledger/fabric-peer        latest              5c7e5946f3dc        2 weeks ago         57.2MB
hyperledger/fabric-orderer     2.0                 92bd220edcdd        2 weeks ago         39.7MB
hyperledger/fabric-orderer     2.0.1               92bd220edcdd        2 weeks ago         39.7MB
hyperledger/fabric-orderer     latest              92bd220edcdd        2 weeks ago         39.7MB
hyperledger/fabric-ccenv       2.0                 800087268d9b        2 weeks ago         529MB
hyperledger/fabric-ccenv       2.0.1               800087268d9b        2 weeks ago         529MB
hyperledger/fabric-ccenv       latest              800087268d9b        2 weeks ago         529MB
hyperledger/fabric-baseos      2.0                 74ff718f6f67        2 weeks ago         6.9MB
hyperledger/fabric-baseos      2.0.1               74ff718f6f67        2 weeks ago         6.9MB
hyperledger/fabric-baseos      latest              74ff718f6f67        2 weeks ago         6.9MB
hyperledger/fabric-ca          1.4                 3b96a893c1e4        3 weeks ago         150MB
hyperledger/fabric-ca          1.4.6               3b96a893c1e4        3 weeks ago         150MB
hyperledger/fabric-ca          latest              3b96a893c1e4        3 weeks ago         150MB
hyperledger/fabric-zookeeper   0.4                 ede9389347db        4 months ago        276MB
hyperledger/fabric-zookeeper   0.4.18              ede9389347db        4 months ago        276MB
hyperledger/fabric-zookeeper   latest              ede9389347db        4 months ago        276MB
hyperledger/fabric-kafka       0.4                 caaae0474ef2        4 months ago        270MB
hyperledger/fabric-kafka       0.4.18              caaae0474ef2        4 months ago        270MB
hyperledger/fabric-kafka       latest              caaae0474ef2        4 months ago        270MB
hyperledger/fabric-couchdb     0.4                 d369d4eaa0fd        4 months ago        261MB
hyperledger/fabric-couchdb     0.4.18              d369d4eaa0fd        4 months ago        261MB
hyperledger/fabric-couchdb     latest              d369d4eaa0fd        4 months ago        261MB
```
Then we can see the binary files and shell script file in the bin `~/fabric-samples/bin` directory.

```
blockchain@blockchain-make-doc:~/fabric-samples/bin$ ls -al
total 206892
drwxr-xr-x  2 blockchain blockchain     4096 Feb 25 22:56 ./
drwxrwxr-x 17 blockchain blockchain     4096 Mar 18 08:07 ../
-rwxr-xr-x  1 blockchain blockchain 20999000 Feb 26 22:05 configtxgen*
-rwxr-xr-x  1 blockchain blockchain 17448272 Feb 26 22:05 configtxlator*
-rwxr-xr-x  1 blockchain blockchain 13344644 Feb 26 22:05 cryptogen*
-rwxr-xr-x  1 blockchain blockchain 19116716 Feb 26 22:05 discover*
-rwxr-xr-x  1 blockchain blockchain 20702242 Feb 25 22:56 fabric-ca-client*
-rwxr-xr-x  1 blockchain blockchain 24603190 Feb 25 22:56 fabric-ca-server*
-rwxr-xr-x  1 blockchain blockchain 12352844 Feb 26 22:05 idemixgen*
-rwxr-xr-x  1 blockchain blockchain 32764776 Feb 26 22:05 orderer*
-rwxr-xr-x  1 blockchain blockchain 50501032 Feb 26 22:05 peer*
```
For your convenience, you can add this directory with Hyperledger Fabric binaries to your **PATH** environment variables `~/.bashrc` file.
```
$ vim ~/.bashrc
```
Inside `~/.bashrc` file set the following commands:
```
# set Hyperledger Fabric
export PATH=$PATH:$HOME/fabric-samples/bin
```
And then run the command `source ~/.bashrc` to rebuild the export **PATH** environment variables.

## [](#create-hyperledger-fabric-business-network)Create Hyperledger Fabric Business Network
This repository provides basically two files **merlin.sh** and **generator.py**. Let me first describe what those are.
For a Hyperledger Fabric Network to operate, it depends on the following files:

-   `core.yaml` (Describes the default behavior of the nodes within the network)
-   `configtx.yaml` (Describes how the transactions are verified, performed and committed)
-   `docker-compose.yaml` (Defines all the services and the network itself)
-   `.env` (Needed by the docker-compose.yaml to set a crucial variable)

These files are utterly large and offer a large scale of possible customizations. The most common use case of a fabric network is
to scale it, and set it up easily by providing the number of "orderers", "peers", "organization" etc. This is not easily possible if you were to
edit the above mentioned files on your own. Therefore the **generator.py** will do all of that for you!

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
  -k KAFKA       Number of Kafka Brokers
  -d DOMAIN      The Domain that will be used
  -c CONSORTIUM  The Consortium that will be used
```
With the optional Parameters at hand, a developer can easily customize his own Fabric Network. If no Parameters are provided, the Script will generate the following network:
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
- 4 Orderers with Kafka Consensus
  - Kafka Cluster with 4 Nodes and 4 Zookeeper instances

If the script is executed, it will ask you the following:
```
Start Merlin now? [y/n]
Do you want Debug output? [y/n]
```
What is that all about? Well, Merlin will automatically setup, build and start the previously generated network and will also install the provided chaincodes onto it.
The provided chaincodes are the following:
- `fabric-authtoken`
- `fabric-orionACL`
- `fabric-transaction-log`
You can also tell Merlin to be a little more quiet by saying "n" to the debug output question.
At the end of this tutorial, you will have constructed a running instance of Hyperledger Fabric business network, as well as installed, instantiated, and executed chaincode.

For our tutorial we will make use of the default network, so no parameters provided.

### [](#execute-generator)Execute generator.py
```
$ python3 generator.py
```
First it will stop any existing docker-compose network that is up.
### [](#generate-peer-and-orderer-certificates)Generate Peer and Orderer Certificates

Nodes (such as peers and orderers) are permitted to access business networks using a membership service provider, which is typically in the form of a certificate authority. In this example, we use the development tool named  `cryptogen`  to generate the required certificates. We use a local MSP to store the certs, which are essentially a local directory structure, for each peer and orderer. In production environments, you can exploit the  `fabric ca`  toolset introducing full-featured certificate authorities to generate the certificates.

The `cryptogen` tool uses a  `yaml`  configuration file as its configuration - based on the content of this file, the required certificates are generated. generator.py is going to create a `crypto-config.yaml`  file for our configuration. It is going to define two organizations of peers and four orderer organization.

Reference: **Hyperledger Fabric Samples**  [crypto-config.yaml](https://github.com/hyperledger/fabric-samples/blob/master/first-network/crypto-config.yaml)
Here is the listing of our  `crypto-config.yaml`  configuration file (for the purpose of simplicity, all comments are removed from this listing):
```
OrdererOrgs:
- Name: Orderer
  Domain: dredev.de
  Specs:
  - Hostname: orderer1
  - Hostname: orderer2
  - Hostname: orderer3
  - Hostname: orderer4
PeerOrgs:
- Name: Org1
  Domain: org1.dredev.de
  Template:
    Count: 2      # Two Peers per org
  Users:
    Count: 1      # One User per org
- Name: Org2
  Domain: org2.dredev.de
  Template:
    Count: 2
  Users:
    Count: 1

```
This file is processed within Merlin in the "generateCryptoStuff" method:
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
### [](#create-channeltx-and-the-genesis-block-using-the-configtxgen-tool)Create channel.tx and the Genesis Block Using the configtxgen Tool

Now we generated the certificates and keys, we can now use the generated `configtx.yaml`  file. This yaml file serves as input to the  `configtxgen`  tool and generates the following important artifacts such as:

-   **channel.tx**

The channel creation transaction. This transaction lets you create the Hyperledger Fabric channel. The channel is the location where the ledger exists and the mechanism that lets peers join business networks.

-   **Genesis Block**

The Genesis block is the first block in our blockchain. It is used to bootstrap the ordering service and holds the channel configuration.

-   **Anchor peers transactions**

The anchor peer transactions specify each Org's Anchor Peer on this channel for communicating from one organization to other one.

#### [](#creatingmodifying-configtxyaml)Take a look at the  `configtx.yaml`

The  `configtx.yaml`  file is broken into several sections, lets have a look:

`Profile`: Profiles describe the organization structure of your network.

`Organization`: The details regarding individual organizations.

`Orderer`: The details regarding the Orderer parameters.

`Application`: Application defaults - not needed for this tutorial.

Create `configtx.yaml` file:
```
$ vim configtx.yaml
```
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
- &id007
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
- &id008
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
Application: &id009
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
  OrdererType: kafka
  Addresses:
  - orderer1.dredev.de:7050       #   <- Variable
  - orderer2.dredev.de:7050
  - orderer3.dredev.de:7050
  - orderer4.dredev.de:7050
  BatchTimeout: 2s
  BatchSize:
    MaxMessageCount: 500
    AbsoluteMaxBytes: 10 MB
    PreferredMaxBytes: 2 MB
  MaxChannels: 0
  Kafka:
    Brokers:
    - kafka0:9092
    - kafka1:9092
    - kafka2:9092
    - kafka3:9092
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
  OrdererDefault:         #   <- Default uname
    <<: *id004
    Capabilities:
      <<: *id003
    Orderer:
      <<: *id005
      OrdererType: kafka
      Addresses:
      - orderer1.dredev.de:7050     #   <- Variable
      - orderer2.dredev.de:7050
      - orderer3.dredev.de:7050
      - orderer4.dredev.de:7050
      Organizations:
      - *id006
      Capabilities:
        <<: *id002
    Consortiums:
      WebConsortium:                #   <- Variable
        Organizations:
        - *id007
        - *id008
  MainChannel:
    <<: *id004
    Consortium: WebConsortium       #   <- Variable
    Application:
      <<: *id009
      Organizations:
      - *id007
      - *id008
    Capabilities:
      <<: *id001

```
You can review the file or can modify it as necessary. However, the following items are key modifications:

-   The organizations that we specified in the profiles section are named exactly as we named them in the  `cryptogen`  tool and its  `crypto-config.yaml`  configuration file.
-   We modified the ID and Name fields to append MSP for the peers.
-   We modified the MSPDir to point to the output directories from the  `cryptogen tool`.
-   The amount of orderers, kafka brokers and Consortium names are defined

#### [](#exec-configtxgen)Executing the configtxgen Tool

You need to set the `FABRIC_CFG_PATH` to point to the `configtx.yaml` first. This is done within Merlin automatically:
```
export FABRIC_CFG_PATH=$PWD
```
Note:  `$PWD=~/Desktop/test-network/`

To create orderer genesis block, Merlin runs the following commands. This is done within the ordererchannel:
```
# Generate the Genesis Block
# ORDERERPROFILE is 'OrdererDefault'
$ configtxgen -profile $ORDERERPROFILE -outputBlock ./config/genesis.block -channelID ordererchannel
```
Output:
```
$ configtxgen -profile $ORDERERPROFILE -outputBlock ./config/genesis.block -channelID ordererchannel
2020-04-01 12:19:20.579 CEST [common.tools.configtxgen] main -> INFO 001 Loading configuration
2020-04-01 12:19:20.601 CEST [common.tools.configtxgen.localconfig] completeInitialization -> INFO 002 orderer type: kafka
2020-04-01 12:19:20.601 CEST [common.tools.configtxgen.localconfig] Load -> INFO 003 Loaded configuration: ./configtx.yaml
2020-04-01 12:19:20.603 CEST [common.tools.configtxgen] doOutputBlock -> INFO 004 Generating genesis block
2020-04-01 12:19:20.604 CEST [common.tools.configtxgen] doOutputBlock -> INFO 005 Writing genesis block
		[+] genesis.block created

```
**After we created the orderer genesis block it is a time to create channel configuration transaction.**
```
# Generate channel configuration transaction
# MAINPROFILE is 'MainChannel'
$ configtxgen -profile $MAINPROFILE -outputCreateChannelTx ./config/channel.tx -channelID mychannel
```
Output:
```
$ configtxgen -profile $MAINPROFILE -outputCreateChannelTx ./config/channel.tx -channelID mychannel
2020-04-01 12:19:20.626 CEST [common.tools.configtxgen] main -> INFO 001 Loading configuration
2020-04-01 12:19:20.642 CEST [common.tools.configtxgen.localconfig] Load -> INFO 002 Loaded configuration: ./configtx.yaml
2020-04-01 12:19:20.642 CEST [common.tools.configtxgen] doOutputChannelCreateTx -> INFO 003 Generating new channel configtx
2020-04-01 12:19:20.644 CEST [common.tools.configtxgen] doOutputChannelCreateTx -> INFO 004 Writing new channel tx
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
2020-04-01 12:19:20.666 CEST [common.tools.configtxgen] main -> INFO 001 Loading configuration
2020-04-01 12:19:20.681 CEST [common.tools.configtxgen.localconfig] Load -> INFO 002 Loaded configuration: ./configtx.yaml
2020-04-01 12:19:20.681 CEST [common.tools.configtxgen] doOutputAnchorPeersUpdate -> INFO 003 Generating anchor peer update
2020-04-01 12:19:20.683 CEST [common.tools.configtxgen] doOutputAnchorPeersUpdate -> INFO 004 Writing anchor peer update
		[+] anchor peers for Org1MSP created
2020-04-01 12:19:20.704 CEST [common.tools.configtxgen] main -> INFO 001 Loading configuration
2020-04-01 12:19:20.720 CEST [common.tools.configtxgen.localconfig] Load -> INFO 002 Loaded configuration: ./configtx.yaml
2020-04-01 12:19:20.720 CEST [common.tools.configtxgen] doOutputAnchorPeersUpdate -> INFO 003 Generating anchor peer update
2020-04-01 12:19:20.721 CEST [common.tools.configtxgen] doOutputAnchorPeersUpdate -> INFO 004 Writing anchor peer update
		[+] anchor peers for Org2MSP created
```
List files generated by `configtxgen` inside `config` folder.
```
$ ls -al config
total 32
drwxr-x---   6 Julian  staff   192B  1 Apr 12:19 ./
drwxr-xr-x  20 Julian  staff   640B  1 Apr 12:19 ../
-rw-r-----   1 Julian  staff   310B  1 Apr 12:19 Org1MSPanchors.tx
-rw-r-----   1 Julian  staff   310B  1 Apr 12:19 Org2MSPanchors.tx
-rw-r-----   1 Julian  staff   1,6K  1 Apr 12:19 channel.tx
-rw-r-----   1 Julian  staff   9,3K  1 Apr 12:19 genesis.block
```
## [](#start-the-hyperledger-fabric-blockchain-network)Start the Hyperledger Fabric blockchain network
Now everything is essentially ready to start. Now to start our network we will use  `docker-compose`  tool. Based on its configuration, we launch containers based on the Docker images we downloaded in the beginning. Merlin is doing that automatically for you!

### [](#modifying-the-docker-compose-yaml-files)Modifying the `docker-compose.yaml` file

`docker-compose`  tools is using yaml configuration files where various aspects of the containers and their network connection are defined. You can start with configuration yaml file from scratch or leverage yaml configuration from the "first-network" example.

Merlin creates the `.env` file in current directory. There are many environment variables for using with the Docker Compose file.

Inside `.env` file set the following variable.
```
COMPOSE_PROJECT_NAME=net
```
The `docker-compose.yaml` content showed by the following:

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
  ca.org2.dredev.de:
    image: hyperledger/fabric-ca:1.4
    environment:
    - FABRIC_CA_HOME=/etc/hyperledger/fabric-ca-server
    - FABRIC_CA_SERVER_CA_NAME=ca.org2.dredev.de
    - FABRIC_CA_SERVER_CA_CERTFILE=/etc/hyperledger/fabric-ca-server-config/ca.org2.dredev.de-cert.pem
    - FABRIC_CA_SERVER_CA_KEYFILE=/etc/hyperledger/fabric-ca-server-config/priv_sk
    ports:
    - 8054:7054
    command: sh -c 'fabric-ca-server start --ca.certfile /etc/hyperledger/fabric-ca-server-config/ca.org2.dredev.de-cert.pem
      --ca.keyfile /etc/hyperledger/fabric-ca-server-config/priv_sk -b admin:adminpw
      -d'
    volumes:
    - ./crypto-config/peerOrganizations/org2.dredev.de/ca/:/etc/hyperledger/fabric-ca-server-config
    container_name: ca.org2.dredev.de
    networks:
    - byfn
  zookeeper1:
    image: hyperledger/fabric-zookeeper
    container_name: zookeeper1
    restart: always
    environment:
    - ZOO_MY_ID=1
    - ZOO_SERVERS=server.1=zookeeper1:2888:3888 server.2=zookeeper2:2888:3888 server.3=zookeeper3:2888:3888
      server.4=zookeeper4:2888:3888
    ports:
    - 2181
    - 2888
    - 3888
    networks:
    - byfn
  zookeeper2:
    image: hyperledger/fabric-zookeeper
    container_name: zookeeper2
    restart: always
    environment:
    - ZOO_MY_ID=2
    - ZOO_SERVERS=server.1=zookeeper1:2888:3888 server.2=zookeeper2:2888:3888 server.3=zookeeper3:2888:3888
      server.4=zookeeper4:2888:3888
    ports:
    - 2181
    - 2888
    - 3888
    networks:
    - byfn
  zookeeper3:
    image: hyperledger/fabric-zookeeper
    container_name: zookeeper3
    restart: always
    environment:
    - ZOO_MY_ID=3
    - ZOO_SERVERS=server.1=zookeeper1:2888:3888 server.2=zookeeper2:2888:3888 server.3=zookeeper3:2888:3888
      server.4=zookeeper4:2888:3888
    ports:
    - 2181
    - 2888
    - 3888
    networks:
    - byfn
  zookeeper4:
    image: hyperledger/fabric-zookeeper
    container_name: zookeeper4
    restart: always
    environment:
    - ZOO_MY_ID=4
    - ZOO_SERVERS=server.1=zookeeper1:2888:3888 server.2=zookeeper2:2888:3888 server.3=zookeeper3:2888:3888
      server.4=zookeeper4:2888:3888
    ports:
    - 2181
    - 2888
    - 3888
    networks:
    - byfn
  kafka0:
    image: hyperledger/fabric-kafka
    container_name: kafka0
    environment:
    - KAFKA_ADVERTISED_HOST_NAME=kafka0
    - KAFKA_ADVERTISED_PORT=9092
    - KAFKA_BROKER_ID=0
    - KAFKA_MESSAGE_MAX_BYTES=103809024
    - KAFKA_REPLICA_FETCH_MAX_BYTES=103809024
    - KAFKA_UNCLEAN_LEADER_ELECTION_ENABLE=false
    - KAFKA_NUM_REPLICA_FETCHERS=1
    - KAFKA_DEFAULT_REPLICATION_FACTOR=1
    - KAFKA_ZOOKEEPER_CONNECT=zookeeper1:2181,zookeeper2:2181,zookeeper3:2181,zookeeper4:2181
    ports:
    - 9092
    depends_on: &id001
    - zookeeper1
    - zookeeper2
    - zookeeper3
    - zookeeper4
    networks:
    - byfn
  kafka1:
    image: hyperledger/fabric-kafka
    container_name: kafka1
    environment:
    - KAFKA_ADVERTISED_HOST_NAME=kafka1
    - KAFKA_ADVERTISED_PORT=9092
    - KAFKA_BROKER_ID=1
    - KAFKA_MESSAGE_MAX_BYTES=103809024
    - KAFKA_REPLICA_FETCH_MAX_BYTES=103809024
    - KAFKA_UNCLEAN_LEADER_ELECTION_ENABLE=false
    - KAFKA_NUM_REPLICA_FETCHERS=1
    - KAFKA_DEFAULT_REPLICATION_FACTOR=2
    - KAFKA_ZOOKEEPER_CONNECT=zookeeper1:2181,zookeeper2:2181,zookeeper3:2181,zookeeper4:2181
    ports:
    - 9092
    depends_on: *id001
    networks:
    - byfn
  kafka2:
    image: hyperledger/fabric-kafka
    container_name: kafka2
    environment:
    - KAFKA_ADVERTISED_HOST_NAME=kafka2
    - KAFKA_ADVERTISED_PORT=9092
    - KAFKA_BROKER_ID=2
    - KAFKA_MESSAGE_MAX_BYTES=103809024
    - KAFKA_REPLICA_FETCH_MAX_BYTES=103809024
    - KAFKA_UNCLEAN_LEADER_ELECTION_ENABLE=false
    - KAFKA_NUM_REPLICA_FETCHERS=1
    - KAFKA_DEFAULT_REPLICATION_FACTOR=3
    - KAFKA_ZOOKEEPER_CONNECT=zookeeper1:2181,zookeeper2:2181,zookeeper3:2181,zookeeper4:2181
    ports:
    - 9092
    depends_on: *id001
    networks:
    - byfn
  kafka3:
    image: hyperledger/fabric-kafka
    container_name: kafka3
    environment:
    - KAFKA_ADVERTISED_HOST_NAME=kafka3
    - KAFKA_ADVERTISED_PORT=9092
    - KAFKA_BROKER_ID=3
    - KAFKA_MESSAGE_MAX_BYTES=103809024
    - KAFKA_REPLICA_FETCH_MAX_BYTES=103809024
    - KAFKA_UNCLEAN_LEADER_ELECTION_ENABLE=false
    - KAFKA_NUM_REPLICA_FETCHERS=1
    - KAFKA_DEFAULT_REPLICATION_FACTOR=4
    - KAFKA_ZOOKEEPER_CONNECT=zookeeper1:2181,zookeeper2:2181,zookeeper3:2181,zookeeper4:2181
    ports:
    - 9092
    depends_on: *id001
    networks:
    - byfn
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
    - CONFIGTX_ORDERER_ORDERERTYPE=kafka
    - CONFIGTX_ORDERER_KAFKA_BROKERS=[kafka0:9092,kafka1:9092,kafka2:9092,kafka3:9092]
    - ORDERER_KAFKA_RETRY_SHORTINTERVAL=1s
    - ORDERER_KAFKA_RETRY_SHORTTOTAL=30s
    - ORDERER_KAFKA_VERBOSE=true
    - ORDERER_ABSOLUTEMAXBYTES=10 MB
    - ORDERER_PREFERREDMAXBYTES=512 KB
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric/orderer
    command: orderer
    ports:
    - 7050:7050
    volumes:
    - ./config/:/etc/hyperledger/configtx
    - ./crypto-config/ordererOrganizations/dredev.de/orderers/orderer1.dredev.de/:/etc/hyperledger/msp/orderer
    networks:
    - byfn
    depends_on: &id002
    - kafka0
    - kafka1
    - kafka2
    - kafka3
  orderer2.dredev.de:
    container_name: orderer2.dredev.de
    image: hyperledger/fabric-orderer:2.0
    environment:
    - ORDERER_HOST=orderer2.dredev.de
    - ORDERER_GENERAL_LOGLEVEL=debug
    - ORDERER_GENERAL_LISTENADDRESS=0.0.0.0
    - ORDERER_GENERAL_LISTENPORT=7050
    - ORDERER_GENERAL_GENESISMETHOD=file
    - ORDERER_GENERAL_GENESISFILE=/etc/hyperledger/configtx/genesis.block
    - ORDERER_GENERAL_LOCALMSPID=OrdererMSP
    - ORDERER_GENERAL_LOCALMSPDIR=/etc/hyperledger/msp/orderer/msp
    - CONFIGTX_ORDERER_BATCHTIMEOUT=1s
    - CONFIGTX_ORDERER_ORDERERTYPE=kafka
    - CONFIGTX_ORDERER_KAFKA_BROKERS=[kafka0:9092,kafka1:9092,kafka2:9092,kafka3:9092]
    - ORDERER_KAFKA_RETRY_SHORTINTERVAL=1s
    - ORDERER_KAFKA_RETRY_SHORTTOTAL=30s
    - ORDERER_KAFKA_VERBOSE=true
    - ORDERER_ABSOLUTEMAXBYTES=10 MB
    - ORDERER_PREFERREDMAXBYTES=512 KB
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric/orderer
    command: orderer
    ports:
    - 8050:7050
    volumes:
    - ./config/:/etc/hyperledger/configtx
    - ./crypto-config/ordererOrganizations/dredev.de/orderers/orderer2.dredev.de/:/etc/hyperledger/msp/orderer
    networks:
    - byfn
    depends_on: *id002
  orderer3.dredev.de:
    container_name: orderer3.dredev.de
    image: hyperledger/fabric-orderer:2.0
    environment:
    - ORDERER_HOST=orderer3.dredev.de
    - ORDERER_GENERAL_LOGLEVEL=debug
    - ORDERER_GENERAL_LISTENADDRESS=0.0.0.0
    - ORDERER_GENERAL_LISTENPORT=7050
    - ORDERER_GENERAL_GENESISMETHOD=file
    - ORDERER_GENERAL_GENESISFILE=/etc/hyperledger/configtx/genesis.block
    - ORDERER_GENERAL_LOCALMSPID=OrdererMSP
    - ORDERER_GENERAL_LOCALMSPDIR=/etc/hyperledger/msp/orderer/msp
    - CONFIGTX_ORDERER_BATCHTIMEOUT=1s
    - CONFIGTX_ORDERER_ORDERERTYPE=kafka
    - CONFIGTX_ORDERER_KAFKA_BROKERS=[kafka0:9092,kafka1:9092,kafka2:9092,kafka3:9092]
    - ORDERER_KAFKA_RETRY_SHORTINTERVAL=1s
    - ORDERER_KAFKA_RETRY_SHORTTOTAL=30s
    - ORDERER_KAFKA_VERBOSE=true
    - ORDERER_ABSOLUTEMAXBYTES=10 MB
    - ORDERER_PREFERREDMAXBYTES=512 KB
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric/orderer
    command: orderer
    ports:
    - 9050:7050
    volumes:
    - ./config/:/etc/hyperledger/configtx
    - ./crypto-config/ordererOrganizations/dredev.de/orderers/orderer3.dredev.de/:/etc/hyperledger/msp/orderer
    networks:
    - byfn
    depends_on: *id002
  orderer4.dredev.de:
    container_name: orderer4.dredev.de
    image: hyperledger/fabric-orderer:2.0
    environment:
    - ORDERER_HOST=orderer4.dredev.de
    - ORDERER_GENERAL_LOGLEVEL=debug
    - ORDERER_GENERAL_LISTENADDRESS=0.0.0.0
    - ORDERER_GENERAL_LISTENPORT=7050
    - ORDERER_GENERAL_GENESISMETHOD=file
    - ORDERER_GENERAL_GENESISFILE=/etc/hyperledger/configtx/genesis.block
    - ORDERER_GENERAL_LOCALMSPID=OrdererMSP
    - ORDERER_GENERAL_LOCALMSPDIR=/etc/hyperledger/msp/orderer/msp
    - CONFIGTX_ORDERER_BATCHTIMEOUT=1s
    - CONFIGTX_ORDERER_ORDERERTYPE=kafka
    - CONFIGTX_ORDERER_KAFKA_BROKERS=[kafka0:9092,kafka1:9092,kafka2:9092,kafka3:9092]
    - ORDERER_KAFKA_RETRY_SHORTINTERVAL=1s
    - ORDERER_KAFKA_RETRY_SHORTTOTAL=30s
    - ORDERER_KAFKA_VERBOSE=true
    - ORDERER_ABSOLUTEMAXBYTES=10 MB
    - ORDERER_PREFERREDMAXBYTES=512 KB
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric/orderer
    command: orderer
    ports:
    - 10050:7050
    volumes:
    - ./config/:/etc/hyperledger/configtx
    - ./crypto-config/ordererOrganizations/dredev.de/orderers/orderer4.dredev.de/:/etc/hyperledger/msp/orderer
    networks:
    - byfn
    depends_on: *id002
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
    - CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/peer/
    - CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=${COMPOSE_PROJECT_NAME}_byfn
    - CORE_LEDGER_STATE_STATEDATABASE=CouchDB
    - CORE_LEDGER_STATE_COUCHDBCONFIG_COUCHDBADDRESS=couchdb0.org1.dredev.de:5984
    - CORE_LEDGER_STATE_COUCHDBCONFIG_USERNAME=
    - CORE_LEDGER_STATE_COUCHDBCONFIG_PASSWORD=
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric
    command: peer node start
    ports:
    - 7051:7051
    - 7052:7052
    - 7053:7053
    volumes:
    - /var/run/:/host/var/run/
    - ./crypto-config/peerOrganizations/org1.dredev.de/peers/peer0.org1.dredev.de/msp:/etc/hyperledger/msp/peer
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
  peer1.org1.dredev.de:
    container_name: peer1.org1.dredev.de
    image: hyperledger/fabric-peer:2.0
    environment:
    - CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock
    - CORE_LOGGING_PEER=debug
    - CORE_CHAINCODE_LOGGING_LEVEL=DEBUG
    - CORE_PEER_ID=peer1.org1.dredev.de
    - CORE_PEER_ADDRESS=peer1.org1.dredev.de:7051
    - CORE_PEER_LOCALMSPID=Org1MSP
    - CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/peer/
    - CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=${COMPOSE_PROJECT_NAME}_byfn
    - CORE_LEDGER_STATE_STATEDATABASE=CouchDB
    - CORE_LEDGER_STATE_COUCHDBCONFIG_COUCHDBADDRESS=couchdb1.org1.dredev.de:5984
    - CORE_LEDGER_STATE_COUCHDBCONFIG_USERNAME=
    - CORE_LEDGER_STATE_COUCHDBCONFIG_PASSWORD=
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric
    command: peer node start
    ports:
    - 8051:7051
    - 8052:7052
    - 8053:7053
    volumes:
    - /var/run/:/host/var/run/
    - ./crypto-config/peerOrganizations/org1.dredev.de/peers/peer1.org1.dredev.de/msp:/etc/hyperledger/msp/peer
    - ./crypto-config/peerOrganizations/org1.dredev.de/users:/etc/hyperledger/msp/users
    - ./config:/etc/hyperledger/configtx
    depends_on:
    - couchdb1.org1.dredev.de
    networks:
    - byfn
  couchdb1.org1.dredev.de:
    container_name: couchdb1.org1.dredev.de
    image: hyperledger/fabric-couchdb
    environment:
    - COUCHDB_USER=
    - COUCHDB_PASSWORD=
    ports:
    - 6984:5984
    networks:
    - byfn
  peer0.org2.dredev.de:
    container_name: peer0.org2.dredev.de
    image: hyperledger/fabric-peer:2.0
    environment:
    - CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock
    - CORE_LOGGING_PEER=debug
    - CORE_CHAINCODE_LOGGING_LEVEL=DEBUG
    - CORE_PEER_ID=peer0.org2.dredev.de
    - CORE_PEER_ADDRESS=peer0.org2.dredev.de:7051
    - CORE_PEER_LOCALMSPID=Org2MSP
    - CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/peer/
    - CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=${COMPOSE_PROJECT_NAME}_byfn
    - CORE_LEDGER_STATE_STATEDATABASE=CouchDB
    - CORE_LEDGER_STATE_COUCHDBCONFIG_COUCHDBADDRESS=couchdb0.org2.dredev.de:5984
    - CORE_LEDGER_STATE_COUCHDBCONFIG_USERNAME=
    - CORE_LEDGER_STATE_COUCHDBCONFIG_PASSWORD=
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric
    command: peer node start
    ports:
    - 9051:7051
    - 9052:7052
    - 9053:7053
    volumes:
    - /var/run/:/host/var/run/
    - ./crypto-config/peerOrganizations/org2.dredev.de/peers/peer0.org2.dredev.de/msp:/etc/hyperledger/msp/peer
    - ./crypto-config/peerOrganizations/org2.dredev.de/users:/etc/hyperledger/msp/users
    - ./config:/etc/hyperledger/configtx
    depends_on:
    - couchdb0.org2.dredev.de
    networks:
    - byfn
  couchdb0.org2.dredev.de:
    container_name: couchdb0.org2.dredev.de
    image: hyperledger/fabric-couchdb
    environment:
    - COUCHDB_USER=
    - COUCHDB_PASSWORD=
    ports:
    - 7984:5984
    networks:
    - byfn
  peer1.org2.dredev.de:
    container_name: peer1.org2.dredev.de
    image: hyperledger/fabric-peer:2.0
    environment:
    - CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock
    - CORE_LOGGING_PEER=debug
    - CORE_CHAINCODE_LOGGING_LEVEL=DEBUG
    - CORE_PEER_ID=peer1.org2.dredev.de
    - CORE_PEER_ADDRESS=peer1.org2.dredev.de:7051
    - CORE_PEER_LOCALMSPID=Org2MSP
    - CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/peer/
    - CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=${COMPOSE_PROJECT_NAME}_byfn
    - CORE_LEDGER_STATE_STATEDATABASE=CouchDB
    - CORE_LEDGER_STATE_COUCHDBCONFIG_COUCHDBADDRESS=couchdb1.org2.dredev.de:5984
    - CORE_LEDGER_STATE_COUCHDBCONFIG_USERNAME=
    - CORE_LEDGER_STATE_COUCHDBCONFIG_PASSWORD=
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric
    command: peer node start
    ports:
    - 10051:7051
    - 10052:7052
    - 10053:7053
    volumes:
    - /var/run/:/host/var/run/
    - ./crypto-config/peerOrganizations/org2.dredev.de/peers/peer1.org2.dredev.de/msp:/etc/hyperledger/msp/peer
    - ./crypto-config/peerOrganizations/org2.dredev.de/users:/etc/hyperledger/msp/users
    - ./config:/etc/hyperledger/configtx
    depends_on:
    - couchdb1.org2.dredev.de
    networks:
    - byfn
  couchdb1.org2.dredev.de:
    container_name: couchdb1.org2.dredev.de
    image: hyperledger/fabric-couchdb
    environment:
    - COUCHDB_USER=
    - COUCHDB_PASSWORD=
    ports:
    - 8984:5984
    networks:
    - byfn
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

This yaml file is generated by generator.py. It makes some assumptions though. The default ports for the Containers are fixed and COULD be modified. This may or may not work, no
guarantee for that! The Network name is "byfn". This can definitely be changed within the generator.py! The Ports, which are exposed to the main host, are determined with some simple
maths. Assuming the number of the Organization is stored in "org" and the Peer number, beginning with 0 is stored in "peer", the port of the peer is determined in the following way:
```
port=$(( 7051+1000*(($NO_PEERS*($org -1))+$peer) ))
```
You can look at the results within the docker-compose.yaml. No ports should overlap with this!

### [](#start-containers) Start the Docker Containers

After we have generated the certificates, the genesis block, the channel transaction configuration, and created or modified the appropriate yaml files, we are read to start our network. Use the following command to start the network.

```
# Or the Default file of the docker-compose is docker-compose.yaml so we don't need to specify the file name
$ docker-compose up -d
```
Merlin Output:
```
>>> I will now start all the containers! Docker do your thing!
Creating network "net_byfn" with the default driver
Creating couchdb1.org2.dredev.de ... done
Creating couchdb0.org2.dredev.de ... done
Creating ca.org1.dredev.de       ... done
Creating zookeeper4              ... done
Creating couchdb1.org1.dredev.de ... done
Creating zookeeper3              ... done
Creating zookeeper1              ... done
Creating zookeeper2              ... done
Creating couchdb0.org1.dredev.de ... done
Creating ca.org2.dredev.de       ... done
Creating peer0.org2.dredev.de    ... done
Creating peer0.org1.dredev.de    ... done
Creating peer1.org2.dredev.de    ... done
Creating peer1.org1.dredev.de    ... done
Creating kafka0                  ... done
Creating kafka3                  ... done
Creating kafka2                  ... done
Creating kafka1                  ... done
Creating orderer2.dredev.de      ... done
Creating orderer1.dredev.de      ... done
Creating orderer3.dredev.de      ... done
Creating orderer4.dredev.de      ... done
Creating cli                     ... done
>>> Now please give the containers a short amount of time to start. 10s should be enough
```

You can use `docker ps` command to list the running containers. In our case, you should see the following containers running:
-   2 peers in each organization
-   1 couchDB in each peer
-   4 orderer nodes
-   4 Kafka nodes
-   4 Zookeeper nodes
-   1 CA for each Org
-   1 CLI

After running `docker-compose` and `docker ps` you can expect output similar to the following:
```
$ docker ps
CONTAINER ID        IMAGE                            COMMAND        CREATED              STATUS              PORTS                  NAMES
a01798c6c7bd        hyperledger/fabric-tools        "/bin/bash"             About an hour ago   Up About an hour                                      cli
fe1ff77364c6        hyperledger/fabric-orderer:2.0  "orderer"               About an hour ago   Up About an hour    0.0.0.0:7050->7050/tcp            orderer1.dredev.de
06e0c70cb4a9        hyperledger/fabric-orderer:2.0  "orderer"               About an hour ago   Up About an hour    0.0.0.0:10050->7050/tcp           orderer4.dredev.de
8fc36d158544        hyperledger/fabric-orderer:2.0  "orderer"               About an hour ago   Up About an hour    0.0.0.0:8050->7050/tcp            orderer2.dredev.de
35bd10a9286a        hyperledger/fabric-orderer:2.0  "orderer"               About an hour ago   Up About an hour    0.0.0.0:9050->7050/tcp            orderer3.dredev.de
a9f2f65c6a73        hyperledger/fabric-kafka        "/docker-entrypoint.…"  About an hour ago   Up About an hour    9093/tcp, 0.0.0.0:32940->9092/tcp kafka1
161003ce7f89        hyperledger/fabric-kafka        "/docker-entrypoint.…"  About an hour ago   Up About an hour    9093/tcp, 0.0.0.0:32942->9092/tcp kafka3
cf216f0b48e0        hyperledger/fabric-kafka        "/docker-entrypoint.…"  About an hour ago   Up About an hour    9093/tcp, 0.0.0.0:32943->9092/tcp kafka2
f4c298c9970d        hyperledger/fabric-kafka        "/docker-entrypoint.…"  About an hour ago   Up About an hour    9093/tcp, 0.0.0.0:32941->9092/tcp kafka0
eb0177ae71b4        hyperledger/fabric-peer:2.0     "peer node start"       About an hour ago   Up About an hour    0.0.0.0:8051->7051/tcp, 0.0.0.0:8052->7052/tcp, 0.0.0.0:8053->7053/tcp      peer1.org1.dredev.de
8769bd4f35f8        hyperledger/fabric-peer:2.0     "peer node start"       About an hour ago   Up About an hour    0.0.0.0:10051->7051/tcp, 0.0.0.0:10052->7052/tcp, 0.0.0.0:10053->7053/tcp   peer1.org2.dredev.de
cab6e7b33ad7        hyperledger/fabric-peer:2.0     "peer node start"       About an hour ago   Up About an hour    0.0.0.0:7051-7053->7051-7053/tcp  peer0.org1.dredev.de
6bb3e8cac181        hyperledger/fabric-peer:2.0     "peer node start"       About an hour ago   Up About an hour    0.0.0.0:9051->7051/tcp, 0.0.0.0:9052->7052/tcp, 0.0.0.0:9053->7053/tcp      peer0.org2.dredev.de
fe703ed15766        hyperledger/fabric-ca:1.4       "sh -c 'fabric-ca-se…"  About an hour ago   Up About an hour    0.0.0.0:8054->7054/tcp            ca.org2.dredev.de
1d233f78712d        hyperledger/fabric-zookeeper    "/docker-entrypoint.…"  About an hour ago   Up About an hour    0.0.0.0:32939->2181/tcp, 0.0.0.0:32938->2888/tcp, 0.0.0.0:32936->3888/tcp   zookeeper2
c3940c2ddd60        hyperledger/fabric-couchdb      "tini -- /docker-ent…"  About an hour ago   Up About an hour    4369/tcp, 9100/tcp, 0.0.0.0:5984->5984/tcp   couchdb0.org1.dredev.de
61e5cd915989        hyperledger/fabric-zookeeper    "/docker-entrypoint.…"  About an hour ago   Up About an hour    0.0.0.0:32937->2181/tcp, 0.0.0.0:32935->2888/tcp, 0.0.0.0:32934->3888/tcp   zookeeper1
20bf6408718a        hyperledger/fabric-zookeeper    "/docker-entrypoint.…"  About an hour ago   Up About an hour    0.0.0.0:32933->2181/tcp, 0.0.0.0:32932->2888/tcp, 0.0.0.0:32931->3888/tcp   zookeeper3
243d31ddb3e5        hyperledger/fabric-couchdb      "tini -- /docker-ent…"  About an hour ago   Up About an hour    4369/tcp, 9100/tcp, 0.0.0.0:8984->5984/tcp   couchdb1.org2.dredev.de
a19003300e75        hyperledger/fabric-ca:1.4       "sh -c 'fabric-ca-se…"  About an hour ago   Up About an hour    0.0.0.0:7054->7054/tcp            ca.org1.dredev.de
db0f483e9476        hyperledger/fabric-couchdb      "tini -- /docker-ent…"  About an hour ago   Up About an hour    4369/tcp, 9100/tcp, 0.0.0.0:7984->5984/tcp    couchdb0.org2.dredev.de
9d88ab559821        hyperledger/fabric-couchdb      "tini -- /docker-ent…"  About an hour ago   Up About an hour    4369/tcp, 9100/tcp, 0.0.0.0:6984->5984/tcp    couchdb1.org1.dredev.de
32ef9b9ca7b8        hyperledger/fabric-zookeeper    "/docker-entrypoint.…"  About an hour ago   Up About an hour    0.0.0.0:32930->2181/tcp, 0.0.0.0:32929->2888/tcp, 0.0.0.0:32928->3888/tcp   zookeeper4

```
### [](#the-channel) The channel

After the Docker containers started, we can use the  **Command Line Interface (CLI)** ,  **Fabric SDK** or the good old **Terminal** to interact with the blockchain network. In this tutorial we use the  **Terminal**  to interact with the blockchain network. Note that all the necessary tools need to be within the PATH variable!

You can interact with the other peers by prefixing our peer commands with the appropriate environment variables. Usually, this means pointing to the certificates for that peer. You need to do that whenever you want to change the peer. Merlin has an integrated method to perform this change called "changeOrg".

Here is the list of environment variables that **need to be used as the prefix** for peer commands when interacting with peer0 of Org1, peer1 of Org1, peer0 of Org2 and peer1 of Org2 organization respectively. After setting these variables, you sort of "imitate" to be that peer. Then you can interact with the network. Merlin does that automagically

**Peer0 of Org1**
```
# Peer0 of Org1 organization
CORE_PEER_LOCALMSPID=Org1MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org1.dredev.de/users/Admin@org1.dredev.de/msp
CORE_PEER_ADDRESS=peer0.org1.dredev.de:7051
```
**Peer1 of Org1**
```
# Peer1 of Org1 organization
CORE_PEER_LOCALMSPID=Org1MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org1.dredev.de/users/Admin@org1.dredev.de/msp
CORE_PEER_ADDRESS=peer1.org1.dredev.de:8051
```
**Peer0 of Org2**
```
# Peer0 of Org2 organization
CORE_PEER_LOCALMSPID=Org2MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org2.dredev.de/users/Admin@org2.dredev.de/msp
CORE_PEER_ADDRESS=peer0.org2.dredev.de:9051
```
**Peer1 of Org2**
```
# Peer1 of Org2 organization
CORE_PEER_LOCALMSPID=Org2MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org2.dredev.de/users/Admin@org2.dredev.de/msp
CORE_PEER_ADDRESS=peer1.org2.dredev.de:10051
```

#### [](#create-channel) Create the channel

The first command that we issue is the  `peer create channel`  command. This command targets the orderers (where the channels must be created) and uses the  `channel.tx`  and the channel name that is created using the  `configtxgen`  tool. To create the channel, run the following command to create the channel called `mychannel`:
```
# peer channel create \
   -o orderer1.dredev.de:7050 -o orderer2.dredev.de:8050 -o orderer3.dredev.de:9050 -o orderer4.dredev.de:10050 \
   -c mychannel \
   -f /etc/hyperledger/configtx/channel.tx
```
Merlin Output:
```
2020-04-01 12:19:36.513 CEST [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2020-04-01 12:19:36.562 CEST [cli.common] readBlock -> INFO 002 Expect block, but got status: &{SERVICE_UNAVAILABLE}
2020-04-01 12:19:36.565 CEST [channelCmd] InitCmdFactory -> INFO 003 Endorser and orderer connections initialized
2020-04-01 12:19:36.768 CEST [cli.common] readBlock -> INFO 004 Expect block, but got status: &{SERVICE_UNAVAILABLE}
2020-04-01 12:19:36.769 CEST [channelCmd] InitCmdFactory -> INFO 005 Endorser and orderer connections initialized
2020-04-01 12:19:36.973 CEST [cli.common] readBlock -> INFO 006 Received block: 0
>>> Is the block there?
[+] Yes it is, mychannel.block
```
The `peer channel create` command returns a `genesis block` which will be used to join the channel. Merlin automatically checks, whether this block exists. In the above case, everything worked fine!

#### [](#join-channel) Join channel

After the orderer creates the channel, the peers have to join the channel:

Join  **peer0.dredev.de**  to the channel.
```
# Join peer0.dredev.de to the channel.
CORE_PEER_LOCALMSPID=Org1MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org1.dredev.de/users/Admin@org1.dredev.de/msp
CORE_PEER_ADDRESS=peer0.org1.dredev.de:7051

# To join the channel.
peer channel join -b mychannel.block
```
Merlin Output:
```
[*] Attempting Channel join for peer0.org1.dredev.de
2020-04-01 12:19:39.022 CEST [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2020-04-01 12:19:39.133 CEST [channelCmd] executeJoin -> INFO 002 Successfully submitted proposal to join channel
[+] Channel join succeeded on peer0.org1.dredev.de
```
Join **peer1.org1.dredev.de** to the channel.
```
# Join peer1.org1.dredev.de to the channel.
CORE_PEER_LOCALMSPID=Org1MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org1.dredev.de/users/Admin@org1.dredev.de/msp
CORE_PEER_ADDRESS=peer1.org1.dredev.de:8051

# To join the channel.
peer channel join -b mychannel.block
```
Merlin Output:
```
[*] Attempting Channel join for peer1.org1.dredev.de
2020-04-01 12:19:39.169 CEST [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2020-04-01 12:19:39.275 CEST [channelCmd] executeJoin -> INFO 002 Successfully submitted proposal to join channel
[+] Channel join succeeded on peer1.org1.dredev.de
```
Join **peer0.org2.dredev.de** to the channel.
```
# Join peer0.org2.dredev.de to the channel.
CORE_PEER_LOCALMSPID=Org2MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org2.dredev.de/users/Admin@org2.dredev.de/msp
CORE_PEER_ADDRESS=peer0.org2.dredev.de:9051

# To join the channel.
peer channel join -b mychannel.block
```
Merlin Output:
```
[*] Attempting Channel join for peer0.org2.dredev.de
2020-04-01 12:19:39.313 CEST [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2020-04-01 12:19:39.420 CEST [channelCmd] executeJoin -> INFO 002 Successfully submitted proposal to join channel
[+] Channel join succeeded on peer0.org2.dredev.de
```
Join **peer1.org2.dredev.de** to the channel.
```
# Join peer1.org2.dredev.de to the channel.
CORE_PEER_LOCALMSPID=Org2MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org2.dredev.de/users/Admin@org2.dredev.de/msp
CORE_PEER_ADDRESS=peer0.org2.dredev.de:10051

# To join the channel.
peer channel join -b mychannel.block
```
Merlin Output:
```
[*] Attempting Channel join for peer1.org2.dredev.de
2020-04-01 12:19:39.456 CEST [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2020-04-01 12:19:39.557 CEST [channelCmd] executeJoin -> INFO 002 Successfully submitted proposal to join channel
[+] Channel join succeeded on peer1.org2.dredev.de
```

#### [](#update-anchor-peers) Update anchor peers
Now we need to update the anchor peers of each organization, so for both org1 and org2. Note that the Anchor peers per default are the "peer0" peers of each organization.
To update Anchor Peer for Org1 Organization.
```
# Set Environment Variable to Peer0 in Org1 Organization
CORE_PEER_LOCALMSPID=Org1MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org1.dredev.de/users/Admin@org1.dredev.de/msp
CORE_PEER_ADDRESS=peer0.org1.dredev.de:7051

# To update the Anchor Peer
peer channel update -o orderer1.dredev.de:7050 -o orderer2.dredev.de:8050 -o orderer3.dredev.de:9050 -o orderer4.dredev.de:10050 -c mychannel -f /etc/hyperledger/configtx/Org1MSPanchors.tx
```
Merlin Output:
```
[*] Attempting Anchor Update for peer0.org1.dredev.de
2020-04-01 12:19:41.594 CEST [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2020-04-01 12:19:41.624 CEST [channelCmd] update -> INFO 002 Successfully submitted channel update
[+] Anchor Update succeeded on peer0.org1.dredev.de
```
To update Anchor Peer for Org2 Organization.
```
# Set Environment Variable to Peer0 in Org2 Organization
CORE_PEER_LOCALMSPID=Org2MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org2.dredev.de/users/Admin@org2.dredev.de/msp
CORE_PEER_ADDRESS=peer0.org1.dredev.de:9051

# update the Anchor Peer
peer channel update -o orderer1.dredev.de:7050 -o orderer2.dredev.de:8050 -o orderer3.dredev.de:9050 -o orderer4.dredev.de:10050 -c mychannel -f /etc/hyperledger/configtx/Org2MSPanchors.tx
```
Output:
```
[*] Attempting Anchor Update for peer0.org2.dredev.de
2020-04-01 12:19:41.659 CEST [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2020-04-01 12:19:41.684 CEST [channelCmd] update -> INFO 002 Successfully submitted channel update
[+] Anchor Update succeeded on peer0.org2.dredev.de
```

### [](#prepare-chaincode) Prepare chaincode
With fabric 2.0, the Chaincode needs to be packaged within a tar archive before deployment. Therefore the code needs to be compiled first. Merlin does that automatically for us.
```
pushd chaincodes/<chaincode>
./gradlew clean build installDist // For java
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
	[*] Build AuthToken
~/Desktop/test-network/chaincodes/java/fabric-authtoken ~/Desktop/test-network

BUILD SUCCESSFUL in 872ms
6 actionable tasks: 6 executed
~/Desktop/test-network
      [+] Build AuthToken finished
      [*] Build OrionACL
~/Desktop/test-network/chaincodes/java/fabric-orionACL ~/Desktop/test-network

BUILD SUCCESSFUL in 785ms
6 actionable tasks: 6 executed
~/Desktop/test-network
      [+] Build OrionACL finished
      [*] Build Transaction Log
~/Desktop/test-network/chaincodes/java/fabric-transaction-log ~/Desktop/test-network

BUILD SUCCESSFUL in 707ms
6 actionable tasks: 6 executed
~/Desktop/test-network
      [+] Build AuthToken finished
[+] Build finished

[*] Start packaging...
	[*] Attempting packing of AuthToken Chaincode
		[+] Packing of AuthToken Chaincode succeeded

	[*] Attempting packing of OrionACL Chaincode
		[+] Packing of OrionACL Chaincode succeeded

	[*] Attempting packing of Transaction-Log Chaincode
		[+] Packing of OrionACL Chaincode succeeded
[+] Packing complete!
```

### [](#install-chaincode) Install chaincode
With Fabric 2.0, chaincode needs to be installed on every peer using the new Lifecycle Management. For each peer, the command `peer lifecycle chaincode install <chaincodename>.tar.gz` needs to be executed.
```
# Peer0 - Org1
CORE_PEER_LOCALMSPID=Org1MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org1.dredev.de/users/Admin@org1.dredev.de/msp
CORE_PEER_ADDRESS=peer0.org1.dredev.de:7051
$ peer lifecycle chaincode install ${PKG_FILE}

# Peer1 - Org1
CORE_PEER_LOCALMSPID=Org1MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org1.dredev.de/users/Admin@org1.dredev.de/msp
CORE_PEER_ADDRESS=peer1.org1.dredev.de:8051
$ peer lifecycle chaincode install ${PKG_FILE}

# Peer0 - Org2
CORE_PEER_LOCALMSPID=Org2MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org2.dredev.de/users/Admin@org2.dredev.de/msp
CORE_PEER_ADDRESS=peer0.org2.dredev.de:9051
$ peer lifecycle chaincode install ${PKG_FILE}

# Peer1 - Org2
CORE_PEER_LOCALMSPID=Org2MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org2.dredev.de/users/Admin@org2.dredev.de/msp
CORE_PEER_ADDRESS=peer0.org2.dredev.de:10051
$ peer lifecycle chaincode install ${PKG_FILE}
```
Merlin Output (omitted):
```
  [*] Attempting install on peer0.org1.dredev.de
2020-04-01 12:11:10.471 CEST [cli.lifecycle.chaincode] submitInstallProposal -> INFO 001 Installed remotely: response:<status:200 payload:"\nSfabric-authtoken_1:8e8342c533fd29f7ddb3a4fb4ec2e3faa1bac24095e5c5a437e941f6ffe605cc\022\022fabric-authtoken_1" >
2020-04-01 12:11:10.471 CEST [cli.lifecycle.chaincode] submitInstallProposal -> INFO 002 Chaincode code package identifier: fabric-authtoken_1:8e8342c533fd29f7ddb3a4fb4ec2e3faa1bac24095e5c5a437e941f6ffe605cc
2020-04-01 12:11:11.448 CEST [cli.lifecycle.chaincode] submitInstallProposal -> INFO 001 Installed remotely: response:<status:200 payload:"\nRfabric-orionACL_1:e84361b2be72d7f64e998a8adb1547333e890b4b25c651119a0ff7b25bcddd3f\022\021fabric-orionACL_1" >
2020-04-01 12:11:11.448 CEST [cli.lifecycle.chaincode] submitInstallProposal -> INFO 002 Chaincode code package identifier: fabric-orionACL_1:e84361b2be72d7f64e998a8adb1547333e890b4b25c651119a0ff7b25bcddd3f
2020-04-01 12:11:12.444 CEST [cli.lifecycle.chaincode] submitInstallProposal -> INFO 001 Installed remotely: response:<status:200 payload:"\nYfabric-transaction-log_1:67336db57452e9e5d8b29dbc9f409fc5a76450e45ce532599cde04dbff1eb578\022\030fabric-transaction-log_1" >
2020-04-01 12:11:12.444 CEST [cli.lifecycle.chaincode] submitInstallProposal -> INFO 002 Chaincode code package identifier: fabric-transaction-log_1:67336db57452e9e5d8b29dbc9f409fc5a76450e45ce532599cde04dbff1eb578
	[+] Install on peer0.org1.dredev.de  finished
  ...
```
The Output of the above commands should result in a Package ID: ...
The following text needs to be stored within the Variable PACKAGE_ID, in this case for the fabric-authtoken contract.
```
export PACKAGE_ID=fabric-authtoken_1:8e8342c533fd29f7ddb3a4fb4ec2e3faa1bac24095e5c5a437e941f6ffe605cc
```
The Identifier is now being used to verify the Installed Chaincode:
```
$ peer lifecycle chaincode queryinstalled
Installed chaincodes on peer:
Package ID: fabcar_1:213192848324892394825239052359
```
Merlin is automatically extracting the id and storing it in an appropriate variable for later use. This is a quite involved process.

**Approve the Chaincode**
With the chaincode being installed onto each peer, we need to approve the installment
of the chaincode with the organizations and the orderers. So this needs to be executed for every Organization!
```
CORE_PEER_LOCALMSPID=Org1MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org1.dredev.de/users/Admin@org1.dredev.de/msp
CORE_PEER_ADDRESS=peer0.org1.dredev.de:7051
$ peer lifecycle chaincode approveformyorg -o localhost:7050\
                                           -o localhost:8050\
                                           -o localhost:9050\
                                           -o localhost:10050\
                                           --channelID mychannel\
                                           --name <chaincodename>\
                                           --version 1\
                                           --package-id ${PACKAGE_ID}\
                                           --sequence 1\
                                           --waitForEvent
# Org2
CORE_PEER_LOCALMSPID=Org2MSP
CORE_PEER_MSPCONFIGPATH=$PWD/crypto-config/peerOrganizations/org2.dredev.de/users/Admin@org2.dredev.de/msp
CORE_PEER_ADDRESS=peer0.org2.dredev.de:7051
$ peer lifecycle chaincode approveformyorg -o localhost:7050\
                                           -o localhost:8050\
                                           -o localhost:9050\
                                           -o localhost:10050\
                                           --channelID mychannel\
                                           --name <chaincodename>\
                                           --version 1\
                                           --package-id ${PACKAGE_ID}\
                                           --sequence 1\
                                           --waitForEvent

```
The output should indicate a success with status (VALID) in both cases! Like this:
```
[*] Start approving...
		[*] Org1 is approving ...
2020-04-01 12:11:25.472 CEST [chaincodeCmd] ClientWait -> INFO 001 txid [79f90d915f2483e79042f36975e42725621eb949f1e1f03c63b64dd5145af8e7] committed with status (VALID) at
2020-04-01 12:11:27.661 CEST [chaincodeCmd] ClientWait -> INFO 001 txid [ac7237ac23455c11cf37d861c8b237bda983965b8051dab6f6354219b4287d55] committed with status (VALID) at
2020-04-01 12:11:29.805 CEST [chaincodeCmd] ClientWait -> INFO 001 txid [d0aeb0557d8b255dd80485638b2e8f5f8a94d9fb93287305293a92027f1446cd] committed with status (VALID) at
		[*] Org2 is approving ...
2020-04-01 12:11:31.968 CEST [chaincodeCmd] ClientWait -> INFO 001 txid [82b7e50425f972743bb9a048a62b5ab00140d0d1415ac0e7aba8a7bbc965bff5] committed with status (VALID) at
2020-04-01 12:11:34.128 CEST [chaincodeCmd] ClientWait -> INFO 001 txid [d15e88d2cdfc5fb300d15fc374fae531711cf14642e4322358891f0f970c18ca] committed with status (VALID) at
2020-04-01 12:11:36.250 CEST [chaincodeCmd] ClientWait -> INFO 001 txid [f6846f2d327dd0121a268f1f444e2941d7e19a3ed8b98b658bc3696fe68dbb65] committed with status (VALID) at
[+] Approving complete.
```

**Check Commit Readiness**
If both Organizations approve the Chaincode, we can now check, whether they are ready for the chaincode to be committed. The command `peer lifecycle chaincode checkcommitreadiness --channelID mychannel --name <chaincodename> --version 1 --sequence 1 --output json` code should return the following:
```
$ peer lifecycle chaincode checkcommitreadiness --channelID mychannel --name fabcar --version 1 --sequence 1 --output json --init-required
[*] Checking commit readiness for OrionACL...
  {
    "approvals": {
      "Org1MSP": true,
      "Org2MSP": true
    }
  }
[*] Checking commit readiness for AuthToken...
  {
    "approvals": {
      "Org1MSP": true,
      "Org2MSP": true
    }
  }
[*] Checking commit readiness for Transaction-Log...
  {
    "approvals": {
      "Org1MSP": true,
      "Org2MSP": true
    }
  }
```
Both Orgs approved the Chaincode! There should not be a "false"!

### [](#instantiate-chaincode) Instantiate/Commit chaincode
With Fabric 2.0, there has been a change to the Instantiation Paradigm. The Chaincode now needs to be committed to the Channel first,
then it is being invoked. The following code is expecting the `PEER_CON_PARAMS` to be set! Refer to the Merlin script for an in-detail description. Generally this variable includes the necessary connection information of the peers within the network.
```
$ peer lifecycle chaincode commit -o localhost:7050\
                                  -o localhost:8050\
                                  -o localhost:9050\
                                  --channelID mychannel\
                                  --name <chaincodename>\
                                  $PEER_CON_PARAMS\
                                  --version 1\
```
Merlin Output:
```
[*] Start committing...
		[*] Commit OrionACL...
2020-04-01 12:11:42.690 CEST [chaincodeCmd] ClientWait -> INFO 001 txid [474fc3bb9c0cae44385fdc7a5f2722faa86b3684c81dc77b92bc6b15c8a34b33] committed with status (VALID) at localhost:9051
2020-04-01 12:11:42.699 CEST [chaincodeCmd] ClientWait -> INFO 002 txid [474fc3bb9c0cae44385fdc7a5f2722faa86b3684c81dc77b92bc6b15c8a34b33] committed with status (VALID) at localhost:8051
2020-04-01 12:11:42.708 CEST [chaincodeCmd] ClientWait -> INFO 003 txid [474fc3bb9c0cae44385fdc7a5f2722faa86b3684c81dc77b92bc6b15c8a34b33] committed with status (VALID) at localhost:7051
2020-04-01 12:11:42.720 CEST [chaincodeCmd] ClientWait -> INFO 004 txid [474fc3bb9c0cae44385fdc7a5f2722faa86b3684c81dc77b92bc6b15c8a34b33] committed with status (VALID) at localhost:10051
		[*] Commit AuthToken...
2020-04-01 12:11:44.970 CEST [chaincodeCmd] ClientWait -> INFO 001 txid [b9672a8652ba06012ae9cb3f05b704d71ed9770f80334f89a1acbcf3c484bf20] committed with status (VALID) at localhost:7051
2020-04-01 12:11:45.016 CEST [chaincodeCmd] ClientWait -> INFO 002 txid [b9672a8652ba06012ae9cb3f05b704d71ed9770f80334f89a1acbcf3c484bf20] committed with status (VALID) at localhost:8051
2020-04-01 12:11:45.027 CEST [chaincodeCmd] ClientWait -> INFO 003 txid [b9672a8652ba06012ae9cb3f05b704d71ed9770f80334f89a1acbcf3c484bf20] committed with status (VALID) at localhost:9051
2020-04-01 12:11:45.044 CEST [chaincodeCmd] ClientWait -> INFO 004 txid [b9672a8652ba06012ae9cb3f05b704d71ed9770f80334f89a1acbcf3c484bf20] committed with status (VALID) at localhost:10051
		[*] Commit Transaction-Log...
2020-04-01 12:11:47.421 CEST [chaincodeCmd] ClientWait -> INFO 001 txid [e93cac7c772794f7d581c2a2ccbd70245a65f34ed5f81c6fef6fe86666efa9bb] committed with status (VALID) at localhost:7051
2020-04-01 12:11:47.432 CEST [chaincodeCmd] ClientWait -> INFO 002 txid [e93cac7c772794f7d581c2a2ccbd70245a65f34ed5f81c6fef6fe86666efa9bb] committed with status (VALID) at localhost:9051
2020-04-01 12:11:47.438 CEST [chaincodeCmd] ClientWait -> INFO 003 txid [e93cac7c772794f7d581c2a2ccbd70245a65f34ed5f81c6fef6fe86666efa9bb] committed with status (VALID) at localhost:10051
2020-04-01 12:11:47.518 CEST [chaincodeCmd] ClientWait -> INFO 004 txid [e93cac7c772794f7d581c2a2ccbd70245a65f34ed5f81c6fef6fe86666efa9bb] committed with status (VALID) at localhost:8051
	[+] Committing complete!
```


We can now see whether the CC has been committed to the ledger:
```
$ peer lifecycle chaincode querycommitted --channelID mychannel --name <chaincodename>
```
Merlin Output:
```
=<=<=<=<=<=<=<=<=<=<=<=<=<=<= Chaincodes <=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=
Committed chaincode definition for chaincode 'fabric-orionACL' on channel 'mychannel':
Version: 1, Sequence: 1, Endorsement Plugin: escc, Validation Plugin: vscc, Approvals: [Org1MSP: true, Org2MSP: true]
Committed chaincode definition for chaincode 'fabric-authtoken' on channel 'mychannel':
Version: 1, Sequence: 1, Endorsement Plugin: escc, Validation Plugin: vscc, Approvals: [Org1MSP: true, Org2MSP: true]
Committed chaincode definition for chaincode 'fabric-transaction-log' on channel 'mychannel':
Version: 1, Sequence: 1, Endorsement Plugin: escc, Validation Plugin: vscc, Approvals: [Org1MSP: true, Org2MSP: true]
=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=
```
**That's it!** You got your own network to work with. Merlin will execute a few test transactions then:

### [](#invoke) Invoke
```
# ORDERERS stores all the orderer connections e.g. "-o localhost:7050 -o localhost:8050..."
$ peer chaincode invoke $ORDERERS -C $CHANNEL_ID -n fabric-authtoken $PEER_CON_PARAMS -c '{"function": "createAuthToken", "Args":["test"]}'

2020-04-01 12:20:21.619 CEST [chaincodeCmd] chaincodeInvokeOrQuery -> INFO 001 Chaincode invoke successful. result: status:200 payload:"true"
```

### [](#query) Query
```
//Query
$ peer chaincode query -C $CHANNEL_ID -n fabric-authtoken -c '{"function":"readAuthToken", "Args":["test"]}'
{"revoked":false,"value":"8ca8460c3cbc9851f8d8c8894a19d4335cef1b8efc2c82bdcc9b2350c6e5c269"}
```
Now you can do your thing!
