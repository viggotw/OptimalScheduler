from network.model import Network

network = Network()

network.addSource(id=1, name='Ola Nordmann', cost=150, attributes={'supervisor'})
network.addSource(id=2, name='Ola Svenskmann', cost=150, attributes={'supervisor', 'electrician'})
network.addSource(id=3, name='Ola Danskmann', cost=200, attributes={'electrician'})

network.addSink(id=1,name='Project A', capacityMin=2, capacityMax=5,
                attributesMin={'supervisor':1, 'electrician':0},
                attributesMax={'supervisor':1, 'electrician':1})
network.addSink(id=2, name='Project A', capacityMin=2, capacityMax=5,
                attributesMin={'supervisor':1},
                attributesMax={'supervisor':1})
network.addSink(id=3, name='Project A', capacityMin=2, capacityMax=5,
                attributesMin={'electrician':1},
                attributesMax={'electrician':2})

