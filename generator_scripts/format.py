import yaml

# This file contains some neat helpers and formats


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


class Orga:
    def __init__(self, domain, org, orgmsp, ap):
        self.org = org
        self.domain = domain
        self.org_msp = orgmsp
        self.anchor_peer = ap


def tr(s):
    return s.replace('\'<<\'', '<<')  # such output is not valid YAML!


class NetworkConfiguration:
    def __init__(self, _ca_defport=7054,
                 _orderer_defport=7050,
                 _peer_defport=7051,
                 _couchdb_defport=5984,
                 _network_name="byfn",
                 _ordering_service="raft"):
        self.ca_defport = _ca_defport
        self.orderer_defport = _orderer_defport
        self.peer_defport = _peer_defport
        self.couchdb_defport = _couchdb_defport
        self.network_name = _network_name
        self.ordering_service = "raft"


class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True