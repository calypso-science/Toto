from PyQt5.Qt import Qt
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QApplication,QListWidget,QAbstractItemView,QTreeWidgetItem,QTreeWidget


default=Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled
drag=Qt.ItemIsDragEnabled
drop=Qt.ItemIsDropEnabled
SETTINGS={
    "family":(["root"],default|drag|drop),
    "children":(["family"],default|drag)
}

#itemDropped = QtCore.pyqtSignal()

class CustomTreeWidget(QTreeWidget):
    itemDropped = QtCore.pyqtSignal(str,str,str)
    editmetadata= QtCore.pyqtSignal(QtCore.QModelIndex,str,str)
    editfile= QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        

        self.setItemsExpandable(True)
        self.setAnimated(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        # only one by on for now
        #self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.settings=SETTINGS

        root=self.invisibleRootItem()
        root.setData(0,QtCore.Qt.ToolTipRole,"root")
        
    def mousePressEvent (self, event):
        if event.button() == QtCore.Qt.RightButton:
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
        role=QtCore.Qt.ToolTipRole
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
            fl=self.settings[category][1] |Qt.ItemIsTristate| Qt.ItemIsUserCheckable
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
