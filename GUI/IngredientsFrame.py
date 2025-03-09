from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableView, QStyledItemDelegate, QSpinBox
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from DataHandler import DataHandler

class IngredientTableModel(QAbstractTableModel):
    def __init__(self, ingredients=None):
        super().__init__()
        data_handler = DataHandler()
        self.ingredients = list(data_handler.ingredients_set)
        self.ingredients = [dict(item, pinned=item.get("pinned", 0)) for item in self.ingredients]
        self.ingredients.sort(key=lambda x: (-x["pinned"], x["name"]))
        self.max_pin = max((item["pinned"] for item in self.ingredients), default=0)

    def toggle_pin(self, row):
        if 0 <= row < len(self.ingredients):
            current_pin = self.ingredients[row]["pinned"]
            if current_pin == 0:  # Jeśli nieprzypięte, przypnij z nowym numerem
                self.max_pin += 1
                self.ingredients[row]["pinned"] = self.max_pin
            else:  # Jeśli przypięte, odpinasz (ustaw na 0)
                self.ingredients[row]["pinned"] = 0
            # Ponowne sortowanie po zmianie
            self.ingredients.sort(key=lambda x: (-x["pinned"], x["name"]))
            # Powiadomienie widoku o zmianie wszystkich danych
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