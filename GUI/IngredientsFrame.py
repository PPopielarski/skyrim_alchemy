from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QStyledItemDelegate, QSpinBox, QTableView, QApplication, QWidget, QVBoxLayout, QLineEdit

from DataHandler import DataHandler
from PySide6.QtCore import QAbstractTableModel, Qt, QSortFilterProxyModel


class IngredientsTableModel(QAbstractTableModel):
    def __init__(self, data_list, pinned_rows_list):
        super().__init__()
        self.data_list = data_list
        self.pinned_rows_list = pinned_rows_list

    def rowCount(self, index=None):
        return len(self.data_list)

    def columnCount(self, index=None):
        return 2

    def data(self, index, role):
        if not index.isValid():
            return None

        value = self.data_list[index.row()][index.column()]

        if role == Qt.DisplayRole and index.column() == 0 and index.row() in self.pinned_rows_list:
            return f"> {value}"
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return str(value) if index.column() == 0 else value

        return None
    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        if index.column() == 1:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return ["Ingredient", "Count"][section]
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.isValid():
            self.data_list[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

class IngredientsTableSortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, pinned_rows_list: list, parent=None):
        super().__init__(parent)
        self.pinned_rows_list: list = pinned_rows_list
        self.filter_text = ""

    def toggle_pin(self, row):
        if row in self.pinned_rows_list:
            self.pinned_rows_list.remove(row)
        else:
            self.pinned_rows_list.append(row)

        proxy_index = self.index(row, 0)
        self.dataChanged.emit(proxy_index, proxy_index)
        self.invalidate()

    def lessThan(self, left, right):

        left_row = left.row()
        right_row = right.row()

        if left_row in self.pinned_rows_list:
            left_row = -self.pinned_rows_list.index(left_row) - 1

        if right_row in self.pinned_rows_list:
            right_row = -self.pinned_rows_list.index(right_row)- 1

        return left_row > right_row

    def filterAcceptsRow(self, source_row, source_parent):
        if self.filter_text:
            index = self.sourceModel().index(source_row, 0, source_parent)
            name = self.sourceModel().data(index, Qt.DisplayRole).lower()
            return self.filter_text.lower() in name
        return True

    def setFilterText(self, text):
        self.filter_text = text
        self.invalidateFilter()

class SpinBoxDelegate(QStyledItemDelegate):

    def createEditor(self, parent, option, index):
        if index.column() == 1:
            spinbox = QSpinBox(parent)
            spinbox.setMinimum(0)
            spinbox.setMaximum(1000000)
            return spinbox
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if index.column() == 1:
            value = index.model().data(index, Qt.EditRole)
            editor.setValue(value)

    def setModelData(self, editor, model, index):
        if index.column() == 1:
            model.setData(index, editor.value(), Qt.EditRole)

class IngredientTableView(QTableView):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setModel(model)
        self.setItemDelegateForColumn(1, SpinBoxDelegate())
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        max_ingredient_string_width = max(
            QFontMetrics(self.font()).horizontalAdvance(item[0]) for item in self.model.sourceModel().data_list) + 10
        self.setColumnWidth(0, max_ingredient_string_width)
        three_digit_string_width = QFontMetrics(self.font()).horizontalAdvance("999") + 20
        self.setColumnWidth(1, three_digit_string_width)
        self.total_width = max_ingredient_string_width + three_digit_string_width + 50

    def mousePressEvent(self, event):
        index = self.indexAt(event.position().toPoint())
        if not index.isValid():
            return super().mousePressEvent(event)

        if event.button() == Qt.RightButton:
            source_row_number = self.model.mapToSource(self.model.index(index.row(), 1)).row()
            self.model.toggle_pin(source_row_number)
        elif index.column() == 0 and event.button() == Qt.LeftButton:
            source_index = self.model.mapToSource(self.model.index(index.row(), 1))
            current_value = self.model.sourceModel().data(source_index, Qt.DisplayRole) or 0
            self.model.sourceModel().setData(source_index, int(current_value) + 1, Qt.EditRole)

        super().mousePressEvent(event)

class IngredientTableFrame(QWidget):

    def __init__(self):
        super().__init__()
        self.data_handler = DataHandler()
        self.pinned_rows_list = []
        input_data = [[ingredient, 0] for ingredient in sorted(self.data_handler.ingredients_set)]
        self.model = IngredientsTableModel(input_data, self.pinned_rows_list)

        self.proxy = IngredientsTableSortFilterProxyModel(self.pinned_rows_list)
        self.proxy.setSourceModel(self.model)
        self.proxy.setSortRole(Qt.DisplayRole)

        self.table = IngredientTableView(self.proxy)
        self.table.setSortingEnabled(True)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type name of ingredient...")
        self.search_box.textChanged.connect(self.proxy.setFilterText)

        layout = QVBoxLayout()
        layout.addWidget(self.search_box)
        layout.addWidget(self.table)
        self.resize(self.table.total_width, QApplication.primaryScreen().availableGeometry().height())
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication([])
    window = IngredientTableFrame()
    window.show()
    app.exec()