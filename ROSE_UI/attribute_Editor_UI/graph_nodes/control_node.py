from PySide6.QtWidgets import (QLabel, QListWidget, QListWidgetItem, QAbstractItemView, #type: ignore
                               QWidget, QVBoxLayout, QLineEdit, QPushButton, QSizePolicy)
from PySide6.QtCore import Qt, QSize #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_Node import AttributeGraphNode, AttributeNodeProperties #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_conf import (registerAttributeNode, #type: ignore
                                                                    OPERATIONCODE_CONTROL_NODE)
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_categories import CATEGORY_TARGET #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")

#two lines per row: the editable proxy name, and the source underneath it. One
#line could not show both in a 250px dock - the name was clipped to '..._Visibility'
ROW_HEIGHT = 42

class ControlNodeProperties(AttributeNodeProperties):
    """The control's ordered proxy list.

    Order lives here rather than on the canvas because it is channel-box order,
    not topology - which attribute is wired in says nothing about where it should
    sit in the channel box. Dragging rows here reorders; the canvas stays a
    picture of what drives what.
    """

    def initUI(self):
        super().initUI()

        self.layout.addWidget(QLabel("Channel box order:"))

        self.proxy_list = QListWidget()
        self.proxy_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.proxy_list.setSelectionMode(QAbstractItemView.SingleSelection)
        #sized to its content below, so the properties dock's own scrollbar does
        #the scrolling rather than nesting a second one inside it
        self.proxy_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.proxy_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.proxy_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.proxy_list.model().rowsMoved.connect(self.onRowsMoved)
        self.layout.addWidget(self.proxy_list)

    def onRowsMoved(self, *args):
        new_order = []
        for index in range(self.proxy_list.count()):
            entry_id = self.proxy_list.item(index).data(Qt.ItemDataRole.UserRole)
            entry = self.node.getProxyEntry(entry_id)
            if entry is not None:
                new_order.append(entry)

        if len(new_order) == len(self.node.proxy_entries):
            self.node.proxy_entries = new_order
            self.setHasBeenModified()

    def onProxyNameEdited(self, entry_id, name_edit):
        success, message = self.node.setProxyName(entry_id, name_edit.text())
        if not success:
            log.warning("CONTROLNODE:: --onProxyNameEdited:: ", message)
        #always re-read from the model, so a refused name never stays on screen
        self.refresh()

    def refresh(self):
        super().refresh()

        if not hasattr(self, "proxy_list"):
            return

        self.proxy_list.blockSignals(True)
        self.proxy_list.clear()

        for entry in self.node.proxy_entries:
            item = QListWidgetItem(self.proxy_list)
            item.setData(Qt.ItemDataRole.UserRole, entry["source_node_id"])
            item.setSizeHint(QSize(0, ROW_HEIGHT))
            self.proxy_list.setItemWidget(item, self.buildProxyRow(entry))

        self.proxy_list.blockSignals(False)
        self.proxy_list.setFixedHeight(max(len(self.node.proxy_entries), 1) * ROW_HEIGHT + 6)

    def buildProxyRow(self, entry):
        row_widget = QWidget()
        row = QVBoxLayout(row_widget)
        row.setContentsMargins(2, 1, 2, 1)
        row.setSpacing(0)

        #the name it will carry in the channel box - the thing being edited, so
        #it gets the full width
        name_edit = QLineEdit(entry["proxy_name"])
        name_edit.setFixedHeight(20)
        name_edit.editingFinished.connect(
            lambda entry_id=entry["source_node_id"], edit=name_edit: self.onProxyNameEdited(entry_id, edit))
        row.addWidget(name_edit)

        source_name = entry.get("source_name", "")
        is_deprecated = entry.get("deprecated", False)

        if is_deprecated:
            #same red the Skinning tab uses for a deform that no longer resolves
            row_widget.setAttribute(Qt.WA_StyledBackground, True)
            row_widget.setStyleSheet("background-color: #FF6B2E2E;")
            source_name = "%s  (missing)" % source_name

        source_label = QLabel("< %s" % source_name)
        source_label.setStyleSheet("color: #FFDDBBBB; font-size: 10px;" if is_deprecated
                                   else "color: #FF888888; font-size: 10px;")
        #the full text on hover, since a long component prefix can still outrun
        #a narrow dock
        source_label.setToolTip(source_name)
        row.addWidget(source_label)

        return row_widget


@registerAttributeNode(OPERATIONCODE_CONTROL_NODE)
class ControlTargetNode(AttributeGraphNode):
    """A control receiving proxied attributes.

    Input only - nothing reads a value back out of a control here. Every incoming
    edge becomes one proxy attribute, created in the order held in proxy_entries.
    """

    operation_code = OPERATIONCODE_CONTROL_NODE
    operation_title = "Control"
    category = CATEGORY_TARGET
    Node_Properties_Class = ControlNodeProperties

    def __init__(self, scene):
        super().__init__(scene,
                         inputs = [["proxies", SocketTypes.attribute, True]],
                         outputs = [])

        self.control_ref = None
        #ordered [{source_node_id, source_name, proxy_name}] - kept in step with
        #the incoming edges by syncProxyEntries()
        self.proxy_entries = []
        self.built_proxy_names = []

    def setControlRef(self, control):
        self.control_ref = {"id": control.id, "name": control.name,
                            "prefix": control.node.getComponentFullPrefix()}
        #the bare slot name as the title, the component underneath it - the full
        #name is mostly prefix, which elides away and leaves every control looking alike
        self.title = control.control_name if hasattr(control, "control_name") else control.name
        self.properties.refresh()

    def getSubtitle(self):
        return self.control_ref.get("prefix", "") if self.control_ref else ""

    def resolveControl(self):
        if self.control_ref is None:
            return None

        rig_scene = self.scene.getRigScene()
        if rig_scene is None:
            return None

        control = rig_scene.getControlById(self.control_ref["id"])
        if control is None:
            control = rig_scene.getControlByName(self.control_ref["name"])

        if control is not None:
            self.control_ref["id"] = control.id
            self.control_ref["name"] = control.name
            self.control_ref["prefix"] = control.node.getComponentFullPrefix()

        return control

    def getDescription(self):
        control = self.resolveControl()
        if control is None:
            return "Unresolved control '%s'" % (self.control_ref["name"] if self.control_ref else "?")
        return "Proxies %d attribute(s) onto %s" % (len(self.proxy_entries), control.name)

    def getProxyEntry(self, source_node_id):
        return next((entry for entry in self.proxy_entries
                     if entry["source_node_id"] == source_node_id), None)

    def setProxyName(self, source_node_id, proxy_name):
        proxy_name = proxy_name.strip()
        if not proxy_name:
            return False, "Name cannot be empty"

        for entry in self.proxy_entries:
            if entry["source_node_id"] != source_node_id and entry["proxy_name"] == proxy_name:
                return False, "'%s' is already used on this control" % proxy_name

        entry = self.getProxyEntry(source_node_id)
        if entry is None:
            return False, "Not connected to this control"

        entry["proxy_name"] = proxy_name
        #flagged, so syncProxyEntries stops regenerating it automatically
        entry["custom_name"] = True
        return True, proxy_name

    def buildSourceLabel(self, upstream):
        subtitle = upstream.getSubtitle()
        return "%s%s" % (subtitle + " " if subtitle else "", upstream.title)

    def buildDefaultProxyName(self, upstream, taken_names):
        """A name unique to this control, and self-describing.

        Every component exposes a Control_Visibility, so defaulting to the bare
        attribute name gave all of them the same one - Maya then created the first
        and refused the rest, which looked like only one attribute being proxied.
        The component prefix makes it unique and says where it came from.
        """
        prefix = upstream.getSubtitle()
        #a prefix is only usable in an attribute name if it looks like one -
        #'Rig Root' and 'operator' are labels, not prefixes
        if prefix and prefix.endswith("_") and " " not in prefix:
            candidate = "%s%s" % (prefix, upstream.title)
        else:
            candidate = upstream.title

        if candidate not in taken_names:
            return candidate

        suffix = 1
        while "%s%d" % (candidate, suffix) in taken_names:
            suffix += 1
        return "%s%d" % (candidate, suffix)

    def syncProxyEntries(self):
        """Reconcile the ordered list against the edges actually connected.

        New edges append (so a freshly wired attribute lands at the bottom of the
        channel box), disconnected ones drop out, and anything already listed
        keeps its position.
        """
        upstream_nodes = self.getUpstreamNodes(0)
        upstream_by_id = {node.id: node for node in upstream_nodes}

        kept = []
        for entry in self.proxy_entries:
            upstream = upstream_by_id.get(entry["source_node_id"])
            if upstream is None:
                continue
            entry["source_name"] = self.buildSourceLabel(upstream)
            entry["deprecated"] = upstream.isDeprecated()
            kept.append(entry)

        listed_ids = set(entry["source_node_id"] for entry in kept)
        for upstream in upstream_nodes:
            if upstream.id in listed_ids:
                continue
            kept.append({
                "source_node_id": upstream.id,
                "source_name": self.buildSourceLabel(upstream),
                "proxy_name": "",
                "custom_name": False,
                "deprecated": upstream.isDeprecated(),
            })

        self.proxy_entries = self.applyAutomaticProxyNames(kept, upstream_by_id)

    def applyAutomaticProxyNames(self, entries, upstream_by_id):
        """Give every entry the automatic name unless the user renamed it.

        The automatic name carries the component prefix, so several components'
        Control_Visibility can sit on one control - without that they all ask
        Maya for the same attribute name and only the first is created. A name
        the user typed is flagged and left alone.
        """
        taken = set(entry["proxy_name"] for entry in entries
                    if entry.get("custom_name") and entry.get("proxy_name"))

        named = []
        for entry in entries:
            if entry.get("custom_name") and entry.get("proxy_name"):
                named.append(entry)
                continue

            upstream = upstream_by_id.get(entry["source_node_id"])
            if upstream is None:
                named.append(entry)
                continue

            entry["proxy_name"] = self.buildDefaultProxyName(upstream, taken)
            entry["custom_name"] = False
            taken.add(entry["proxy_name"])
            named.append(entry)

        return named

    def isDeprecated(self):
        return self.control_ref is not None and self.resolveControl() is None

    def validate(self):
        self.syncProxyEntries()
        return self.setValidity(self.control_ref is not None and not self.isDeprecated())

    def removeBuiltProxies(self):
        from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore

        control_name = self.control_ref["name"] if self.control_ref else None
        if control_name and MC.objectExists(control_name):
            for proxy_name in self.built_proxy_names:
                if MC.attributeExists(control_name, proxy_name):
                    MC.deleteAttribute(control_name, proxy_name)

        self.built_proxy_names = []

    def buildProxies(self):
        from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore

        control = self.resolveControl()
        if control is None:
            return False, "Control '%s' no longer exists" % (self.control_ref["name"] if self.control_ref else "?")
        if not control.exists():
            return False, "Control '%s' is not built in the scene" % control.name

        #order and names can both have changed since the last build, and Maya's
        #channel box order is just order-of-creation, so clear before re-adding
        self.removeBuiltProxies()
        self.syncProxyEntries()

        skipped = []
        for entry in self.proxy_entries:
            upstream = next((node for node in self.getUpstreamNodes(0)
                             if node.id == entry["source_node_id"]), None)
            if upstream is None:
                continue

            source_plug = upstream.getOutputPlug()
            if source_plug is None:
                skipped.append(entry["proxy_name"])
                continue

            source_node, source_attribute = source_plug.split(".", 1)
            if MC.attributeExists(control.name, entry["proxy_name"]):
                #not ours to overwrite - removeBuiltProxies() already cleared
                #everything this node made, so anything left is someone else's
                skipped.append(entry["proxy_name"])
                log.warning("CONTROLNODE:: --buildProxies:: '%s' already exists on %s - skipped"
                            % (entry["proxy_name"], control.name))
                continue

            MC.addProxyAttribute(control.name, entry["proxy_name"], source_node, source_attribute)
            self.built_proxy_names.append(entry["proxy_name"])

        return True, skipped

    def serialize(self):
        result_data = super().serialize()
        result_data['control_ref'] = self.control_ref
        result_data['proxy_entries'] = self.proxy_entries
        result_data['built_proxy_names'] = self.built_proxy_names
        return result_data

    def deserialize(self, data, hashmap = {}, restore_id = True, exists = False):
        result = super().deserialize(data, hashmap, restore_id, exists)
        self.control_ref = data.get('control_ref', None)
        self.proxy_entries = data.get('proxy_entries', [])
        #entries saved before names carried the component prefix have no flag, so
        #they count as automatic and get re-derived on the next sync
        for entry in self.proxy_entries:
            entry.setdefault("custom_name", False)
        self.built_proxy_names = data.get('built_proxy_names', [])
        return result
