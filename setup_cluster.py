"""Variable number of nodes in a lan, pick your node type and operating system.

Instructions:
Wait for the profile instance to start, and then log in to one or more of
the VMs by clicking on them in the toplogy, and choosing the `shell` menu option.
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg

# Create a portal context, needed to defined parameters
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Variable number of nodes.
pc.defineParameter("n", "Number of Nodes", portal.ParameterType.INTEGER, 5)
pc.defineParameter("nDB", "Number of DBs", portal.ParameterType.INTEGER, 2)

# Pick your OS.
imageList = [
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU16-64-STD', 'UBUNTU 16.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU14-64-STD', 'UBUNTU 14.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//CENTOS66-64-STD', 'CENTOS 6.6'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//CENTOS7-64-STD',     'CENTOS 7'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//FBSD103-64-STD', 'FreeBSD 10.3')]
pc.defineParameter("osImage", "Select OS image",
                   portal.ParameterType.IMAGE,
                   imageList[0], imageList,
                   longDescription="Most clusters have this set of images, " +
                   "pick your favorite one.")

# Optional physical type for all nodes.
pc.defineParameter("phystype",  "Optional physical node type (d710, etc)",
                   portal.ParameterType.STRING, "")

# Retrieve the values the user specifies during instantiation.
params = pc.bindParameters()

# Check parameter validity.
if params.n < 2:
    pc.reportError(portal.ParameterError("You must choose at least 2 nodes"))

# Create lans

lan = request.LAN()    

# Set best effort on the lan to make sure it maps.
lan.best_effort = True

nodes = []
dbnodes = []

for i in range(params.n):
    node = request.RawPC("node" + str(i))
    node.disk_image = params.osImage
    nodes.append(node)
    
for i in range(params.nDB):
    dbnode = request.RawPC("DB" + str(i))
    dbnode.disk_image = params.osImage
    dbnodes.append(dbnode)
    
sched = request.RawPC("sched")
sched.disk_image = params.osImage

for i in range(params.n):
    for j in range(params.nDB):
        lan = request.LAN()
        lan.best_effort = True
        node_iface = nodes[i].addInterface("eth" + str(j))
        db_iface = dbnodes[j].addInterface("eth" + str(i))
        lan.addInterface(node_iface)
        lan.addInterface(db_iface)

for i in range(params.n):
    lan = request.LAN()
    lan.best_effort = True
    node_iface = nodes[i].addInterface("eth" + str(params.nDB))
    sched_iface = sched.addInterface("eth" + str(i))
    lan.addInterface(node_iface)
    lan.addInterface(sched_iface)
    
for i in range(params.nDB):
    lan = request.LAN()
    lan.best_effort = True
    db_iface = dbnodes[i].addInterface("eth" + str(params.n))
    sched_iface = sched.addInterface("eth" + str(params.n + i))
    lan.addInterface(db_iface)
    lan.addInterface(sched_iface)

# Print the RSpec to the enclosing page.
pc.printRequestRSpec(request) 
