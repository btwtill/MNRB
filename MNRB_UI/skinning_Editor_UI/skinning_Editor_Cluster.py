from collections import OrderedDict
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializables

class SkinningEditorCluster(Serializable):
    """s
    Class to manage the skinning editor cluster Data.
    """

    def __init__(self, tab, parent=None):
        """
        Initialize the skinning editor cluster.

        :param parent: Parent widget.
        """
        super().__init__(parent)

        self.skinning_tab = tab

        self._cluster_name = None
        
        self.graphic_cluster = None

    @property
    def cluster_name(self):
        """
        Get the cluster name.

        :return: Cluster name.
        """
        return self._cluster_name
    @cluster_name.setter
    def cluster_name(self, value):
        """
        Set the cluster name.

        :param value: Cluster name.
        """
        self._cluster_name = value

    def serialize(self):
        """
        Serialize the cluster Data.

        :return: Serialized data.
        """

        serialize_data = OrderedDict([
            ('id', self.id),
            ('cluster_name', self.cluster_name)
        ])
        return serialize_data