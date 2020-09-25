from enum import Enum
from network.model import Network

network = Network()

network.setCredentials('SUPERVISOR', 'ELECTRICITAN')

network.addSource(id=1, name='Person A', cost=100)
network.addSource(id=2, name='Person B', cost=150, creds={"ELECTRICITAN"})
network.addSource(id=3, name='Person C', cost=200, creds={network.creds.ELECTRICITAN, network.creds.SUPERVISOR})
network.addSource(id=4, name='Person D', cost=200, creds={network.creds.ELECTRICITAN, network.creds.SUPERVISOR})

network.addSink(1, 'Project A', capacityMin=1)
network.addSink(2, 'Project B', capacityMin=1, credentials={"SUPERVISOR": 1})
network.addSink(3, 'Project C', capacityMin=2, capacityMax=2, credentials={network.creds.SUPERVISOR: 1})