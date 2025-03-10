from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableView, QStyledItemDelegate, QSpinBox, QLineEdit
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, QSortFilterProxyModel
from DataHandler import DataHandler

class IngredientTableModel(QAbstractTableModel):

    def _sort_item_list(self):
        self.ingredients.sort(key=lambda x: (-x["pinned"], x["name"]))

    def __init__(self):
        super().__init__()
        self.data_handler = DataHandler()
        self.ingredients = list(self.data_handler.ingredients_set)
        self.ingredients = [{"name": item, "pinned": 0, "count": 0} for item in self.ingredients]
        self._sort_item_list()
        self.max_pin = max((item["pinned"] for item in self.ingredients), default=0)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Ustawia nazwy kolumn."""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ["Ingredient", "Count"][section]
        return super().headerData(section, orientation, role)

    def toggle_pin(self, row):
        if 0 <= row < len(self.ingredients):
            current_pin = self.ingredients[row]["pinned"]
            if current_pin == 0:  # Jeśli nieprzypięte, przypnij z nowym numerem
                self.max_pin += 1
                self.ingredients[row]["name"] = f"> {self.ingredients[row]["name"]}"
                self.ingredients[row]["pinned"] = self.max_pin
            else:  # Jeśli przypięte, odpinasz (ustaw na 0)
                self.ingredients[row]["pinned"] = 0
                self.ingredients[row]["name"] = self.ingredients[row]["name"][2:]
            # Ponowne sortowanie po zmianie
            self._sort_item_list()
            # Powiadomienie widoku po zmianie wszystkich danych
            top_left = self.index(0, 0)
            bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])

    def rowCount(self, parent=None):
        return len(self.ingredients)

    def columnCount(self, parent=None):
        return 2

    def data(self, index, role):
        if not index.isValid():
            return None

        row, col = index.row(), index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return self.ingredients[row]["name"]
            elif col == 1:
                return self.ingredients[row]["count"]

        if role == Qt.UserRole:
            if col == 1:
                return self.ingredients[row]["count"]

        return None

    def setData(self, index, value, role):
        if role == Qt.EditRole and index.column() == 1:
            self.ingredients[index.row()]["count"] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False

    def flags(self, index):
        if index.column() == 1:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

class IngredientTableView(QTableView):
    def __init__(self, model):
        super().__init__()
        self.setModel(model)
        self.setItemDelegateForColumn(1, SpinBoxDelegate())
        self.setSelectionBehavior(QTableView.SelectRows)
        self.horizontalHeader().setStretchLastSection(True)

# ======== Delegat (obsługuje QSpinBox w drugiej kolumnie) ========
class SpinBoxDelegate(QStyledItemDelegate):

    def createEditor(self, parent, option, index):
        """Tworzy edytor dla drugiej kolumny (QSpinBox)"""
        if index.column() == 1:
            spinbox = QSpinBox(parent)
            spinbox.setMinimum(0)
            spinbox.setMaximum(1000)
            return spinbox
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        """Ustawia początkową wartość w QSpinBox"""
        if index.column() == 1:
            value = index.model().data(index, Qt.UserRole)
            editor.setValue(value)

    def setModelData(self, editor, model, index):
        """Zapisuje wartość z QSpinBox do modelu"""
        if index.column() == 1:
            model.setData(index, editor.value(), Qt.EditRole)

class IngredientFilter(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self._filter_text = ""

    def setFilterText(self, text):
        """Ustawienie tekstu filtra"""
        self._filter_text = text
        self.invalidateFilter()  # Przeładuj filtr, gdy zmieni się tekst

    def filterAcceptsRow(self, source_row, source_parent):
        """Akceptuj wiersz, jeśli nazwa składnika zawiera ciąg z pola tekstowego"""
        if self._filter_text:  # Jeśli tekst filtra nie jest pusty
            index = self.sourceModel().index(source_row, 0, source_parent)
            name = self.sourceModel().data(index, Qt.DisplayRole).lower()
            return self._filter_text.lower() in name
        return True

# ======== Główne okno aplikacji ========
class IngredientTable(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        # Model i filtr
        self.model = IngredientTableModel()
        self.filter = IngredientFilter()
        self.filter.setSourceModel(self.model)

        # Pole tekstowe
        self.search_field = QLineEdit(self)
        self.search_field.setPlaceholderText("Search Ingredients...")
        self.layout.addWidget(self.search_field)

        self.model = IngredientTableModel()
        self.table_view = IngredientTableView(self.model)

        self.table_view = IngredientTableView(self.filter)
        self.layout.addWidget(self.table_view)

        # Połączenie: filtracja na podstawie tekstu w polu
        self.search_field.textChanged.connect(self.on_search_changed)

    def on_search_changed(self, text):
        """Aktualizacja filtra w momencie zmiany tekstu w polu"""
        self.filter.setFilterRegExp(text)  # Filtruj według wprowadzonego tekstu
        self.filter.invalidate()  # Odśwież filtr

class IngredientTableView(QTableView):
    def __init__(self, model):
        super().__init__()
        self.setModel(model)
        self.setItemDelegateForColumn(1, SpinBoxDelegate())
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.adjust_first_column_width()

    def adjust_first_column_width(self):
        font_metrics = QFontMetrics(self.font())
        max_width = max(font_metrics.horizontalAdvance(item["name"]) for item in self.model().ingredients) + 10
        self.setColumnWidth(0, max_width)

    def mousePressEvent(self, event):
        index = self.indexAt(event.position().toPoint())
        if not index.isValid():
            return super().mousePressEvent(event)

        if event.button() == Qt.RightButton:
            self.model().toggle_pin(index.row())
        elif index.column() == 0:
            count_index = self.model().index(index.row(), 1)
            current_value = self.model().data(count_index, Qt.UserRole) or 0
            self.model().setData(count_index, current_value + 1, Qt.EditRole)

        super().mousePressEvent(event)

if __name__ == "__main__":
    app = QApplication([])
    window = IngredientTable()
    window.show()
    app.exec()
