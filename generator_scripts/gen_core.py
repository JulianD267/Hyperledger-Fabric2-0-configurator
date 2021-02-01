import ruamel.yaml
from ruamel.yaml.scalarstring import SingleQuotedScalarString, DoubleQuotedScalarString
from generator_scripts.format import bcolors


def generate_core():
    """
    This function will just generate the core.yaml file from scratch. Nothing really to configure here.
    """
    yaml_new = ruamel.yaml.YAML()
    print(bcolors.WARNING + "     [*] Generating Peer Core")
    peer = {
        "id": "peer",
        "networkId": "byfn",
        "listenAddress": "0.0.0.0:7051",
        "address": "0.0.0.0:7051",
        "addressAutoDetect": False,
        "keepalive": {
            "interval": "7200s",
            "timeout": "20s",
            "minInterval": "60s",
            "client": {
                "interval": "60s",
                "timeout": "20s",
            },
            "deliveryClient": {
                "interval": "60s",
                "timeout": "20s"
            }
        },
        "gossip": {
            "bootstrap": "127.0.0.1:7051",
            "useLeaderElection": True,
            "orgLeader": False,
            "membershipTrackerInterval": "5s",
            "endpoint": None,
            "maxBlockCountToStore": 100,
            "maxPropagationBurstLatency": "10ms",
            "maxPropagationBurstSize": 10,
            "propagateIterations": 1,
            "propagatePeerNum": 3,
            "pullInterval": "4s",
            "pullPeerNum": 3,
            "requestStateInfoInterval": "4s",
            # Determines frequency of pushing state info messages to peers(unit: second)
            "publishStateInfoInterval": "4s",
            # Maximum time a stateInfo message is kept until expired
            "stateInfoRetentionInterval": None,
            # Time from startup certificates are included in Alive messages(unit: second)
            "publishCertPeriod": "10s",
            # Should we skip verifying block messages or not (currently not in use)
            "skipBlockVerification": False,
            # Dial timeout(unit: second)
            "dialTimeout": "3s",
            # Connection timeout(unit: second)
            "connTimeout": "2s",
            # Buffer size of received messages
            "recvBuffSize": 20,
            # Buffer size of sending messages
            "sendBuffSize": 200,
            # Time to wait before pull engine processes incoming digests (unit: second)
            # Should be slightly smaller than requestWaitTime
            "digestWaitTime": "1s",
            # Time to wait before pull engine removes incoming nonce (unit: milliseconds)
            # Should be slightly bigger than digestWaitTime
            "requestWaitTime": "1500ms",
            # Time to wait before pull engine ends pull (unit: second)
            "responseWaitTime": "2s",
            # Alive check interval(unit: second)
            "aliveTimeInterval": "5s",
            # Alive expiration timeout(unit: second)
            "aliveExpirationTimeout": "25s",
            # Reconnect interval(unit: second)
            "reconnectInterval": "25s",
            # This is an endpoint that is published to peers outside of the organization.
            # If this isn't set, the peer will not be known to other organizations.
            "externalEndpoint": None,
            # Leader election service configuration
            "election": {
                # Longest time peer waits for stable membership during leader election startup (unit: second)
                "startupGracePeriod": "15s",
                # Interval gossip membership samples to check its stability (unit: second)
                "membershipSampleInterval": "1s",
                # Time passes since last declaration message before peer decides to perform leader election (unit: second)
                "leaderAliveThreshold": "10s",
                # Time between peer sends propose message and declares itself as a leader (sends declaration message) (unit: second)
                "leaderElectionDuration": "5s"
            },
            "pvtData": {
                "pullRetryThreshold": "60s",
                "transientstoreMaxBlockRetention": 1000,
                "pushAckTimeout": "3s",
                "btlPullMargin": 10,
                "reconcileBatchSize": 10,
                "reconcileSleepInterval": "1m",
                "reconciliationEnabled": True,
                "skipPullingInvalidTransactionsDuringCommit": False,
            },
            "state": {
                "enabled": True,
                "checkInterval": "10s",
                "responseTimeout": "3s",
                "batchSize": 10,
                "blockBufferSize": 100,
                "maxRetries": 3
            },
        },
        "tls": {
            "enabled":  True,
            "clientAuthRequired": False,
            "cert": {
                "file": "tls/server.crt",
            },
            "key": {
                "file": "tls/server.key",
            },
            "rootcert": {
                "file": "tls/ca.crt",
            },
            "clientRootCAs": {
                "files": [
                    "tls/ca.crt"
                ]
            },
            "clientKey": {
                "file": None
            },
            "clientCert": {
                "file": None
            }
        },
        "authentication": {
            "timewindow": "15m"
        },
        "fileSystemPath": "/var/hyperledger/production",
        "BCCSP": {
            "Default": "SW",
            "SW": {
                "Hash": "SHA2",
                "Security": 256,
                "FileKeyStore": {
                    "KeyStore": None,
                },
            },
            "PKCS11": {
                "Library": None,
                "Label": None,
                "Pin": None,
                "Hash": None,
                "Security": None
            }
        },
        "mspConfigPath": "msp",
        "localMspId": "SampleOrg",
        "client": {
            "connTimeout": "3s"
        },
        "deliveryclient": {
            "reconnectTotalTimeThreshold": "3600s",
            "connTimeout": "3s",
            "reConnectBackoffThreshold": "3600s",
            "addressOverrides": None,
        },
        "localMspType": "bccsp",
        "profile": {
            "enabled": False,
            "listenAddress": "0.0.0.0:6060"
        },
        "handlers": {
            "authFilters": [
                { "name": "DefaultAuth" },
                { "name": "ExpirationCheck" },
            ],
            "decorators": [
                { "name": "DefaultDecorator" }
            ],
            "endorsers": {
                "escc": {
                    "name": "DefaultEndorsement",
                    "library": None,
                }
            },
            "validators": {
                "vscc": {
                    "name": "DefaultValidation",
                    "library": None,
                }
            }
        },
        "validatorPoolSize": None,
        "discovery": {
            "enabled": True,
            "authCacheEnabled": True,
            "authCacheMaxSize": 1000,
            "authCachePurgeRetentionRatio": 0.75,
            "orgMembersAllowedAccess": False,
        },
        "limits": {
            "concurrency": {
                "qscc": 5000,
            }
        }
    }
    print(bcolors.OKGREEN + "     [+] Generating Peer Core COMPLETE")

    print(bcolors.WARNING + "     [*] Generating VM Core ")
    vm = {
        "endpoint": "unix:///var/run/docker.sock",
        "docker": {
            "tls": {
                "enabled": True,
                "ca": {
                    "file": "docker/ca.crt",
                },
                "cert": {
                    "file": "docker/tls.crt",
                },
                "key": {
                    "file": "docker/tls.key",
                },
            },
            "attachStdout": False,
            "hostConfig": {
                "NetworkMode": "host",
                "Dns": None,
                "LogConfig": {
                    "Type": "json-file",
                    "Config": {
                        "max-size": DoubleQuotedScalarString("50m"),
                        "max-file": DoubleQuotedScalarString("5")
                    }
                },
                "Memory": 2147483648
            }
        }
    }

    print(bcolors.OKGREEN + "     [+] Generating VM Core COMPLETE")

    print(bcolors.WARNING + "     [*] Generating Chaincode Core ")
    chaincode = {
        "id": {
            "path": None,
            "name": None,
        },
        "builder": "$(DOCKER_NS)/fabric-ccenv:$(TWO_DIGIT_VERSION)",
        "pull": False,
        "golang": {
            "runtime": "$(DOCKER_NS)/fabric-baseos:$(TWO_DIGIT_VERSION)",
            "dynamicLink": False,
        },
        "java": {
            "runtime": "$(DOCKER_NS)/fabric-javaenv:$(TWO_DIGIT_VERSION)",
        },
        "node": {
            "runtime": "$(DOCKER_NS)/fabric-nodeenv:$(TWO_DIGIT_VERSION)",
        },
        "externalBuilders": [],
        "installTimeout": "300s",
        "startuptimeout": "300s",
        "executetimeout": "30s",
        "mode": "net",
        "keepalive": 0,
        "system": {
            "_lifecycle": "enable",
            "cscc": "enable",
            "lscc": "enable",
            "escc": "enable",
            "vscc": "enable",
            "qscc": "enable",
        },
        "logging": {
            "level":  "info",
            "shim":   "warning",
            "format": SingleQuotedScalarString('%{color}%{time:2006-01-02 15:04:05.000 MST} [%{module}] %{shortfunc} '
                                               '-> %{level:.4s} %{id:03x}%{color:reset} %{message}')
        }
    }

    print(bcolors.OKGREEN + "     [+] Generating Chaincode Core COMPLETE")

    print(bcolors.WARNING + "     [*] Generating Ledger Core ")
    ledger = {
        "blockchain": None,
        "state": {
            "stateDatabase": "goleveldb",
            "totalQueryLimit": 100000,
            "couchDBConfig": {
                "couchDBAddress": "127.0.0.1:5984",
                "username": None,
                "password": None,
                "maxRetries": 3,
                "maxRetriesOnStartup": 12,
                "requestTimeout": "35s",
                "internalQueryLimit": 1000,
                "maxBatchUpdateSize": 1000,
                "warmIndexesAfterNBlocks": 1,
                "createGlobalChangesDB": False,
                "cacheSize": 64,
            }
        },
        "history": {
            "enableHistoryDatabase": True,
        },
        "pvtdataStore": {
            "collElgProcMaxDbBatchSize": 5000,
            "collElgProcDbBatchesInterval": 1000
        }

    }

    print(bcolors.OKGREEN + "     [+] Generating Ledger Core COMPLETE")
    print(bcolors.WARNING + "     [*] Generating Operations Core ")
    operations = {
        "listenAddress": "127.0.0.1:9443",
        "tls": {
            "enabled": True,
            "cert": {
                "file": None,
            },
            "key": {
                "file": None,
            },
            "clientAuthRequired": False,
            "clientRootCAs": {
                "files": []
            }
        }
    }
    print(bcolors.OKGREEN + "     [+] Generating Operations Core COMPLETE")
    print(bcolors.WARNING + "     [*] Generating Metrics Core ")

    metrics = {
        "provider": "disabled",
        "statsd": {
            "network": "udp",
            "address": "127.0.0.1:8125",
            "writeInterval": "10s",
            "prefix": None
        }
    }
    print(bcolors.OKGREEN + "     [*] Generating Metrics Core COMPLETE")

    print(bcolors.OKBLUE + "======= Generating final Structure =======")
    final = {
        "peer": peer,
        "vm": vm,
        "chaincode": chaincode,
        "ledger": ledger,
        "operations": operations,
        "metrics": metrics
    }

    # yaml_new.dump(final, sys.stdout)
    f = open("core.yaml", "w")
    yaml_new.dump(final, f)
    print(bcolors.HEADER + "========================================")
    print(">>> core.yaml has been dumped!")
    print("========================================")
