#!/usr/bin/env python3

from seedemu.compiler import Docker
from seedemu.core import Emulator, Node
from seedemu.layers import ScionBase, ScionRouting, ScionIsd, Scion, Ebgp, Ibgp, Ospf, PeerRelationship, ScionSbas
from seedemu.layers.Scion import LinkType as ScLinkType
import examples.scion.utility.experiment as experiment
import python_on_whales
import time

# Initialize
emu = Emulator()
base = ScionBase()
routing = ScionRouting()
scion_isd = ScionIsd()
scion = Scion()
ebgp = Ebgp()
ibgp = Ibgp()
ospf = Ospf()
sbas = ScionSbas()


# ASN Mapping
bgpAsnToSCION = {
    10: "71-2:0:35", # BRIDGES Core
    11: "71-20965", # Geant Core
    12: "71-2:0:3e", # KISTI Core AMS
    13: "71-2:0:3d", # KISTI Core SG
    14: "71-2:0:3b", # KISTI Core DJ
    15: "71-2:0:3f", # KISTI Core CHG

    100: "71-2:0:48", # Equinix
    101: "71-225", # Uva
    102: "71-88", # Princeton
    103: "71-2:0:49", # Cybexer
    104: "71-1140", # SIDN Labs
    105: "71-2:0:4a", # Ovgu 
    106: "71-2546", # Demokritos
}

def createEnvFromASNMapping(node: Node):
    # Iterate over bgpAsnToSCION and create environment variables for each ASN

    # for bgpAsn, scionAsn in bgpAsnToSCION.items():
    node.addBuildCommand(f"echo 'BRIDGES=71-10' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'GEANT=71-11' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'KISTI_AMS=71-12' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'KISTI_SG=71-13' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'KISTI_DJ=71-14' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'KISTI_CHG=71-15' >> /root/.zshrc")
    
    node.addBuildCommand(f"echo 'EQUINIX=71-100' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'UVA=71-101' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'PRINCETON=71-102' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'CYBEXER=71-103' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'SIDN=71-104' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'OVGU=71-105' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'DEMOKRITOS=71-106' >> /root/.zshrc")

    node.addBuildCommand(f"echo 'BRIDGES_HOST=71-10,10.10.0.71' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'GEANT_HOST=71-11,10.11.0.71' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'KISTI_AMS_HOST=71-12,10.12.0.71' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'KISTI_SG_HOST=71-13,10.13.0.71' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'KISTI_DJ_HOST=71-14,10.14.0.71' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'KISTI_CHG_HOST=71-15,10.15.0.71' >> /root/.zshrc")
    
    node.addBuildCommand(f"echo 'EQUINIX_HOST=71-100,10.100.0.71' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'UVA_HOST=71-101,10.101.0.71' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'PRINCETON_HOST=71-102,10.102.0.71' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'CYBEXER_HOST=71-103,10.103.0.71' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'SIDN_HOST=71-104,10.104.0.71' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'OVGU_HOST=71-105,10.105.0.71' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'DEMOKRITOS_HOST=71-106,10.106.0.71' >> /root/.zshrc")

    node.addBuildCommand(f"echo 'EQUINIX_CUSTOMER_HOST=10.200.0.71' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'UVA_CUSTOMER_HOST=10.201.0.71' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'PRINCETON_CUSTOMER_HOST=10.202.0.71' >> /root/.zshrc")
    node.addBuildCommand(f"echo 'OVGU_CUSTOMER_HOST=10.205.0.71' >> /root/.zshrc")


        
# SCION ISDs
base.createIsolationDomain(71)

# Internet Exchange TODO: Currently only 150 is used because of some issues with multiple IXes
base.createInternetExchange(150) # US-Europe
base.createInternetExchange(151) # US-Internal
base.createInternetExchange(152) # Europe Internal
base.createInternetExchange(153) # Europe-KISTI
base.createInternetExchange(154) # KISTI Internal

base.createInternetExchange(180) # Equinix Customer
base.createInternetExchange(181) # UVA Customer
base.createInternetExchange(182) # Princeton Customer
base.createInternetExchange(183) # Ovgu Customer

# Bridges Core (currently only one node)
bridgesCore = base.createAutonomousSystem(10)
scion_isd.addIsdAs(71, 10, is_core=True)
bridgesCore.createNetwork('net0')
cs1 = bridgesCore.createControlService('cs1').joinNetwork('net0')
createEnvFromASNMapping(cs1)
bridgesCore_router = bridgesCore.createRouter('br0')
bridgesCore_router.joinNetwork('net0').joinNetwork('ix150')#.joinNetwork('ix151')
bridgesCore_router2 = bridgesCore.createRouter('br1')
bridgesCore_router2.joinNetwork('net0').joinNetwork('ix151')
bridgesCore_router.appendStartCommand("tcset ix150 --delay=70ms --overwrite")
ebgp.addRsPeer(150, 10)
ebgp.addRsPeer(151, 10)

# GEANT Core
geantCore = base.createAutonomousSystem(11)
scion_isd.addIsdAs(71, 11, is_core=True)
geantCore.createNetwork('net0')
cs1 = geantCore.createControlService('cs1').joinNetwork('net0')
createEnvFromASNMapping(cs1)
geantCore_router1 = geantCore.createRouter('br0')
geantCore_router1.joinNetwork('net0').joinNetwork('ix150')
geantCore_router1.appendStartCommand("tcset net0 --delay=10ms --overwrite")
geantCore_router2 = geantCore.createRouter('br1')
geantCore_router2.joinNetwork('net0').joinNetwork('ix152')
geantCore_router2.appendStartCommand("tcset net0 --delay=10ms --overwrite")
geantCore_router3 = geantCore.createRouter('br2')
geantCore_router3.joinNetwork('net0').joinNetwork('ix153')
ebgp.addRsPeer(150, 11)
ebgp.addRsPeer(152, 11)
ebgp.addRsPeer(153, 11)


# Connect Bridges / GEANT TODO: More than one link does not work...
scion.addIxLink(150, (71, 10), (71, 11), ScLinkType.Core, count=2)
# scion.addIxLink(151, (71, 10), (71, 11), ScLinkType.Core)
ebgp.addPrivatePeering(150, 10, 11, PeerRelationship.Unfiltered)

# KISTI Cores
# 12: "71-2:0:3e", # KISTI Core AMS
# 13: "71-2:0:3d", # KISTI Core SG
# 14: "71-2:0:3b", # KISTI Core DJ
# 15: "71-2:0:3f", # KISTI Core CHG
kistiAmsCore = base.createAutonomousSystem(12)
scion_isd.addIsdAs(71, 12, is_core=True)
kistiAmsCore.createNetwork('net0')
cs1 = kistiAmsCore.createControlService('cs1').joinNetwork('net0')
createEnvFromASNMapping(cs1)
kistiAmsCore_router1 = kistiAmsCore.createRouter('br0')
kistiAmsCore_router1.joinNetwork('net0').joinNetwork('ix153')
kistiAmsCore_router1.appendStartCommand("tcset ix153 --delay=16ms --overwrite")
kistiAmsCore_router2 = kistiAmsCore.createRouter('br1')
kistiAmsCore_router2.joinNetwork('net0').joinNetwork('ix154')
kistiAmsCore_router2.appendStartCommand("tcset ix154 --delay=245ms --overwrite")
ebgp.addRsPeer(153, 12)
ebgp.addRsPeer(154, 12)

kistiSgCore = base.createAutonomousSystem(13)
scion_isd.addIsdAs(71, 13, is_core=True)
kistiSgCore.createNetwork('net0')
kistiSgCore.createControlService('cs1').joinNetwork('net0')
cs1 = createEnvFromASNMapping(cs1)
kistiSgCore_router1 = kistiSgCore.createRouter('br0')
kistiSgCore_router1.joinNetwork('net0').joinNetwork('ix153')
kistiSgCore_router1.appendStartCommand("tcset ix153 --delay=340ms --overwrite")
kistiSgCore_router2 = kistiSgCore.createRouter('br1')
kistiSgCore_router2.joinNetwork('net0').joinNetwork('ix154')
kistiSgCore_router1.appendStartCommand("tcset ix153 --delay=76ms --overwrite")
ebgp.addRsPeer(153, 13)
ebgp.addRsPeer(154, 13)

kistiDjCore = base.createAutonomousSystem(14)
scion_isd.addIsdAs(71, 14, is_core=True)
kistiDjCore.createNetwork('net0')
cs1 = kistiDjCore.createControlService('cs1').joinNetwork('net0')
createEnvFromASNMapping(cs1)
kistiDjCore_router1 = kistiDjCore.createRouter('br0')
kistiDjCore_router1.joinNetwork('net0').joinNetwork('ix154')
ebgp.addRsPeer(154, 14)

kistiChgCore = base.createAutonomousSystem(15)
scion_isd.addIsdAs(71, 15, is_core=True)
kistiChgCore.createNetwork('net0')
kistiChgCore.createControlService('cs1').joinNetwork('net0')
cs1 = createEnvFromASNMapping(cs1)
kistiChgCore_router1 = kistiChgCore.createRouter('br0')
kistiChgCore_router1.joinNetwork('net0').joinNetwork('ix154')
ebgp.addRsPeer(154, 15)

# KISTI Links
scion.addIxLink(153, (71, 11), (71, 12), ScLinkType.Core)
scion.addIxLink(153, (71, 11), (71, 13), ScLinkType.Core)
scion.addIxLink(154, (71, 14), (71, 12), ScLinkType.Core)
scion.addIxLink(154, (71, 14), (71, 13), ScLinkType.Core)
scion.addIxLink(154, (71, 14), (71, 15), ScLinkType.Core)
ebgp.addPrivatePeering(153, 11, 12, PeerRelationship.Unfiltered)
ebgp.addPrivatePeering(153, 11, 13, PeerRelationship.Unfiltered)
ebgp.addPrivatePeering(154, 14, 12, PeerRelationship.Unfiltered)
ebgp.addPrivatePeering(154, 14, 13, PeerRelationship.Unfiltered)
ebgp.addPrivatePeering(154, 14, 15, PeerRelationship.Unfiltered)


# Equinix AS
equinix = base.createAutonomousSystem(100)
scion_isd.addIsdAs(71, 100)
scion_isd.setCertIssuer((71, 100), issuer=10)
equinix.createNetwork('net0')
cs1 = equinix.createControlService('cs1').joinNetwork('net0')
createEnvFromASNMapping(cs1)
equinix_router1 = equinix.createRouter('br0')
equinix_router1.joinNetwork('net0').joinNetwork('ix151')
equinix_router1.appendStartCommand("tcset ix151 --delay=30ms --overwrite")
equinix_router2 = equinix.createRouter('br1')
equinix_router2.joinNetwork('net0').joinNetwork('ix180')
scion.addIxLink(151, (71, 10), (71, 100), ScLinkType.Transit)
ebgp.addRsPeer(151, 100)
ebgp.addRsPeer(180, 100)
ebgp.addPrivatePeering(151, 10, 100, PeerRelationship.Unfiltered)


# UVA
uva = base.createAutonomousSystem(101)
scion_isd.addIsdAs(71, 101)
scion_isd.setCertIssuer((71, 101), issuer=10)
uva.createNetwork('net0')
cs1 = uva.createControlService('cs1').joinNetwork('net0')
createEnvFromASNMapping(cs1)
uva_router1 = uva.createRouter('br0')
uva_router1.joinNetwork('net0').joinNetwork('ix151')
uva_router1.appendStartCommand("tcset ix151 --delay=20ms --overwrite")
uva_router2 = uva.createRouter('br1')
uva_router2.joinNetwork('net0').joinNetwork('ix181')
scion.addIxLink(151, (71, 10), (71, 101), ScLinkType.Transit)
ebgp.addRsPeer(151, 101)
ebgp.addRsPeer(181, 101)
ebgp.addPrivatePeering(151, 10, 101, PeerRelationship.Unfiltered)


# Princeton
princeton = base.createAutonomousSystem(102)
scion_isd.addIsdAs(71, 102)
scion_isd.setCertIssuer((71, 102), issuer=10)
princeton.createNetwork('net0')
cs1 = princeton.createControlService('cs1').joinNetwork('net0')
createEnvFromASNMapping(cs1)
princeton_router1 = princeton.createRouter('br0')
princeton_router1.joinNetwork('net0').joinNetwork('ix151')
princeton_router1.appendStartCommand("tcset ix151 --delay=29ms --overwrite")
princeton_router2 = princeton.createRouter('br1')
princeton_router2.joinNetwork('net0').joinNetwork('ix182')
scion.addIxLink(151, (71, 10), (71, 102), ScLinkType.Transit)
ebgp.addRsPeer(151, 102)
ebgp.addRsPeer(182, 102)
ebgp.addPrivatePeering(151, 10, 102, PeerRelationship.Unfiltered)

# Cybexer
cybexer = base.createAutonomousSystem(103)
scion_isd.addIsdAs(71, 103)
scion_isd.setCertIssuer((71, 103), issuer=11)
cybexer.createNetwork('net0')
cs1 = cybexer.createControlService('cs1').joinNetwork('net0')
createEnvFromASNMapping(cs1)
cybexer_router1 = cybexer.createRouter('br0')
cybexer_router1.joinNetwork('net0').joinNetwork('ix152')
cybexer_router1.appendStartCommand("tcset ix152 --delay=35ms --overwrite")
scion.addIxLink(152, (71, 11), (71, 103), ScLinkType.Transit)
ebgp.addRsPeer(152, 103)
ebgp.addPrivatePeering(152, 11, 103, PeerRelationship.Unfiltered)



# SIDN Labs
sidn = base.createAutonomousSystem(104)
scion_isd.addIsdAs(71, 104)
scion_isd.setCertIssuer((71, 104), issuer=11)
sidn.createNetwork('net0')
cs1 = sidn.createControlService('cs1').joinNetwork('net0')
createEnvFromASNMapping(cs1)
sidn_router1 = sidn.createRouter('br0')
sidn_router1.joinNetwork('net0').joinNetwork('ix152')
sidn_router1.appendStartCommand("tcset ix152 --delay=32ms --overwrite")
scion.addIxLink(152, (71, 11), (71, 104), ScLinkType.Transit)
ebgp.addRsPeer(152, 104)
ebgp.addPrivatePeering(152, 11, 104, PeerRelationship.Unfiltered)


# Ovgu
ovgu = base.createAutonomousSystem(105)
scion_isd.addIsdAs(71, 105)
scion_isd.setCertIssuer((71, 105), issuer=11)
ovgu.createNetwork('net0')
cs1 = ovgu.createControlService('cs1').joinNetwork('net0')
createEnvFromASNMapping(cs1)
ovgu_router1 = ovgu.createRouter('br0')
ovgu_router1.joinNetwork('net0').joinNetwork('ix152')
ovgu_router1.appendStartCommand("tcset ix152 --delay=16ms --overwrite")
ovgu_router2 = ovgu.createRouter('br1')
ovgu_router2.joinNetwork('net0').joinNetwork('ix183')
scion.addIxLink(152, (71, 11), (71, 105), ScLinkType.Transit)
ebgp.addRsPeer(152, 105)
ebgp.addRsPeer(183, 105)
ebgp.addPrivatePeering(152, 11, 105, PeerRelationship.Unfiltered)

# Demokritos
demokritos = base.createAutonomousSystem(106)
scion_isd.addIsdAs(71, 106)
scion_isd.setCertIssuer((71, 106), issuer=11)
demokritos.createNetwork('net0')
cs1 = demokritos.createControlService('cs1').joinNetwork('net0')
createEnvFromASNMapping(cs1)
demokritos_router1 = demokritos.createRouter('br0')
demokritos_router1.joinNetwork('net0').joinNetwork('ix152')
demokritos_router1.appendStartCommand("tcset ix152 --delay=40ms --overwrite")
scion.addIxLink(152, (71, 11), (71, 106), ScLinkType.Transit)
ebgp.addRsPeer(152, 106)
ebgp.addPrivatePeering(152, 11, 106, PeerRelationship.Unfiltered)

# SBAS customers
# AS-200: Equinix customer
as200 = base.createAutonomousSystem(200)
scion_isd.addIsdAs(1, 200, is_core=True)
as200.createNetwork('net0')
as200.createRouter('br0').joinNetwork('net0').joinNetwork('ix180')
ebgp.addRsPeer(180, 200)

# AS-201: UVA Customer
as201 = base.createAutonomousSystem(201)
scion_isd.addIsdAs(1, 201, is_core=True)
as201.createNetwork('net0')
as201.createRouter('br0').joinNetwork('net0').joinNetwork('ix181')
ebgp.addRsPeer(181, 201)

# AS-202: Princeton Customer
as202 = base.createAutonomousSystem(202)
scion_isd.addIsdAs(1, 202, is_core=True)
as202.createNetwork('net0')
as202.createRouter('br0').joinNetwork('net0').joinNetwork('ix182')
ebgp.addRsPeer(182, 202)

# AS-205: Princeton Customer
as205 = base.createAutonomousSystem(205)
scion_isd.addIsdAs(1, 205, is_core=True)
as205.createNetwork('net0')
as205.createRouter('br0').joinNetwork('net0').joinNetwork('ix183')
ebgp.addRsPeer(183, 205)

sbas.addPop(100)
sbas.addPop(101)
sbas.addPop(102)
sbas.addPop(105)
# sbas.addPop(14)

ebgp.addPrivatePeering(180, 100, 200, abRelationship=PeerRelationship.Peer)
ebgp.addPrivatePeering(181, 101, 201, abRelationship=PeerRelationship.Peer)
ebgp.addPrivatePeering(182, 102, 202, abRelationship=PeerRelationship.Peer)
ebgp.addPrivatePeering(183, 105, 205, abRelationship=PeerRelationship.Peer)

# Add customer, this also reuses the IX links and 
# networks etc from AS configuration
# First argument is the pop, second the customer and the last one the IX at which customer and pop connect
sbas.addCustomer(100, 200, 180)
sbas.addCustomer(101, 201, 181)
sbas.addCustomer(102, 202, 182)
sbas.addCustomer(105, 205, 183)

# Rendering
emu.addLayer(base)
emu.addLayer(sbas)
emu.addLayer(routing)
emu.addLayer(ospf)
emu.addLayer(scion_isd)
emu.addLayer(scion)
emu.addLayer(ibgp)
emu.addLayer(ebgp)

emu.render()

# Compilation
emu.compile(Docker(), './output', override=True)

whales = python_on_whales.DockerClient(compose_files=["./output/docker-compose.yml"])
whales.compose.build()
whales.compose.up(detach=True)    

print("Sleeping for 10 seconds until hijack")
time.sleep(10)

print("Hijacking AS, sleeping for 10 minutes")
experiment.hijackAS(11, 101)
time.sleep(600)

experiment.endHijack(11)
print("Hijack ended, sleep for another 30 seconds")
time.sleep(30)

experiment.down()
