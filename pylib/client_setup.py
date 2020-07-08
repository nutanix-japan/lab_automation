from mod.base import Base
from mod.alerts import Alerts
from mod.clusters import Clusters
from mod.containers import Containers
from mod.images import Images
from mod.networks import Networks
from mod.tasks import Tasks
from mod.users import Users
from mod.vms import Vms

class NutanixSetupClient(Base, Alerts, Clusters, Containers, Images, Networks, Tasks, Users, Vms):

  def __init__(self, ip, username, password, timeout_connection=5, timeout_read=15):
    super().__init__(ip, username, password, timeout_connection, timeout_read)
