from PyQt5.QtCore import Qt, QModelIndex, pyqtSignal, QSignalBlocker
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QApplication,QListWidget,QAbstractItemView,QTreeWidgetItem,QTreeWidget


default=Qt.ItemIsSelectable|Qt.ItemIsEnabled
drag=Qt.ItemIsDragEnabled
drop=Qt.ItemIsDropEnabled
SETTINGS={
    "family":(["root"],default|drag|drop),
    "children":(["family"],default|drag)
}

#itemDropped = pyqtSignal()

class CustomTreeWidget(QTreeWidget):
    itemDropped = pyqtSignal(str,str,str)
    editmetadata= pyqtSignal(QModelIndex,str,str)
    editfile= pyqtSignal(str)
    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        

        self.setItemsExpandable(True)
        self.setAnimated(True)
        self.setDragEnabled(True)
        self.setHeaderHidden(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.blocker = QSignalBlocker(self)
        self.blocker.unblock()
        

        # only one by on for now
        #self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.settings=SETTINGS

        root=self.invisibleRootItem()
        root.setData(0,Qt.ToolTipRole,"root")
        
    def mousePressEvent (self, event):
        if event.button() == Qt.RightButton:
            QTreeWidget.mousePressEvent(self, event)
            selModel = self.selectionModel()
            indices = selModel.selectedRows()

            if indices:
                for indice in indices:
                    if indice.parent().data():
                        parents=indice.parent().data()
                        childs=indice.data()
                        self.editmetadata.emit(indice,parents,childs)
                    else:
                        self.editfile.emit(indice.data())

        QTreeWidget.mousePressEvent(self, event)

    def dragMoveEvent(self, event):
        role=Qt.ToolTipRole
        itemToDropIn = self.itemAt(event.pos())
        itemBeingDragged=self.currentItem()
        okList=self.settings[itemBeingDragged.data(0,role)][0]

        if itemToDropIn is None:
            itemToDropIn=self.invisibleRootItem()

        if itemToDropIn.data(0,role) in okList:
            super(CustomTreeWidget, self).dragMoveEvent(event)
            return
        else:
            # possible "next to drop target" case
            parent=itemToDropIn.parent()
            if parent is None:
                parent=self.invisibleRootItem()
            if parent.data(0,role) in okList:
                super(CustomTreeWidget, self).dragMoveEvent(event)
                return
        event.ignore()

    def dropEvent(self, event):
        role=Qt.ToolTipRole

        #item being dragged
        itemBeingDragged=self.currentItem()
        okList=self.settings[itemBeingDragged.data(0,role)][0]

        #parent before the drag
        oldParent=itemBeingDragged.parent()
        if oldParent is None:
            oldParent=self.invisibleRootItem()
        oldIndex=oldParent.indexOfChild(itemBeingDragged)

        #accept any drop
        super(CustomTreeWidget,self).dropEvent(event)

        #look at where itemBeingDragged end up
        newParent=itemBeingDragged.parent()
        if newParent is None:
            newParent=self.invisibleRootItem()

        if newParent.data(0,role) in okList and newParent!=oldParent:
            fileIN=newParent.text(0)
            fileOUT=oldParent.text(0)
            var=itemBeingDragged.text(0)
           
            self.itemDropped.emit(fileIN,var,fileOUT)


        else:
            # drop was not ok, put back the item
            newParent.removeChild(itemBeingDragged)
            oldParent.insertChild(oldIndex,itemBeingDragged)

    def addItem(self,strings,category,parent=None,WhatsThis=''):
        if category not in self.settings:
            print("unknown categorie" +str(category))
            return False
        if parent is None:
            parent=self.invisibleRootItem()
            fl=self.settings[category][1] | Qt.ItemIsUserCheckable #Qt.ItemIsTristate
        else:
            fl=self.settings[category][1]| Qt.ItemIsUserCheckable



        item = QTreeWidgetItem(parent)

        item.setText(0, strings)
        item.setCheckState(0, Qt.Unchecked)
        item.setData(0,Qt.ToolTipRole,category)
        item.setExpanded(True)
        item.setFlags(item.flags()| fl)


        return item

    def rename(self,item,new_name):
        item.model().setData(item,new_name)

    def populate_tree(self,data,keys=None):

        self.blocker.reblock()

        if keys is None:
            keys=data.keys()
            self.clear()
            


        first=True
        for file in keys:
            parent=self.addItem(file,"family")
            for var in data[file]['metadata'].keys():
                if var != 'time':
                    item=self.addItem(var,"children",parent,data[file]['metadata'][var]['short_name'])
                    if first:
                        item.setCheckState(0, Qt.Checked)
                        first=False

        self.expandAll()
        self.blocker.unblock()

    def get_all_items(self):
        """Returns all QTreeWidgetItems in the given QTreeWidget."""
        self.blocker.reblock()
        check_vars = []
        checks_files=[]
        checks_dataframe=[]
        for i in range(self.topLevelItemCount()):
            top_item = self.topLevelItem(i)
            file=top_item.text(0)
            if top_item.checkState(0)== Qt.Checked:
                checks_dataframe.append(file)

            var=[]
            for j in range(top_item.childCount()):
                if (top_item.child(j).checkState(0) == Qt.Checked):# and (top_item.child(j).text(0)[:2] != 'No'):
                    var.append(top_item.child(j).text(0))

            check_vars.append(var)
            checks_files.append(file)


        self.blocker.unblock()

        return checks_files,check_vars,checks_dataframe

    def auto_check(self,all_file=False,all_vars=False,unchecked=False):
        self.blocker.reblock()
        if unchecked:
            all_file=True
            all_vars=True
            flag=Qt.Unchecked
        else:
            flag=Qt.Checked

        for i in range(self.topLevelItemCount()):
            top_item = self.topLevelItem(i)
            if all_file:
                top_item.setCheckState(0, flag)

            for j in range(top_item.childCount()):
                if all_vars:
                    top_item.child(j).setCheckState(0, flag)



        self.blocker.unblock()

    def check_item(self,files):
        self.blocker.reblock()
        flag=Qt.Checked
        for i in range(self.topLevelItemCount()):
            top_item = self.topLevelItem(i)
            if top_item.text(0) in files:
                top_item.setCheckState(0, flag)
        self.blocker.unblock()