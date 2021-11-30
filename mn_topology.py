from mininet.topo import Topo

class MyTopo(Topo):
    def __init__(self, *args, **params):
        Topo.__init__(self)

        # add host
        h1 = self.addHost('h1', ip = '10.0.0.1')
        h2 = self.addHost('h2', ip = '10.0.0.2')

        # add switch
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # add link
        self.addLink(h1, s1)
        self.addLink(h2, s2)
        self.addLink(s1, s2)

topos = { 'mytopo' : (lambda: MyTopo()) }