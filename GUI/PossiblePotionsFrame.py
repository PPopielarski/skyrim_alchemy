from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt


class PotionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Tworzymy główny layout pionowy
        self.layout = QVBoxLayout()

        # 1. QLineEdit na górze do sortowania
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Type name of effect...")

        # 2. QTreeWidget dla mikstur
        self.potions_tree_view = QTreeWidget()
        self.potions_tree_view.setHeaderLabels(
            ["Effect", "Max potion quantity", "Ingredients", "Ingredient quantity"])

        # Ustawiamy możliwość zaznaczania tylko jednego elementu na raz
        self.potions_tree_view.setSelectionMode(QTreeWidget.SingleSelection)

        # Dodajemy wszystkie widgety do layoutu
        self.layout.addWidget(self.search_bar)
        self.layout.addWidget(self.potions_tree_view)

        # Ustawiamy layout dla widgetu
        self.setLayout(self.layout)

    def populate_example_data(self):
        # Przykładowe mikstury
        potion1 = QTreeWidgetItem(self.potions_tree_view, ["Mikstura zdrowia", "1", "", ""])
        potion2 = QTreeWidgetItem(self.potions_tree_view, ["Mikstura many", "1", "", ""])

        # Dodajemy dostępne składniki jako dzieci dla potion1
        available1 = ["Zioła", "Woda"]
        unavailable1 = ["Coś"]
        for ingredient in available1:
            child = QTreeWidgetItem(potion1)
            child.setText(2, ingredient)  # Kolumna "Available ingredients"
            child.setFlags(child.flags() | Qt.ItemIsSelectable)  # Ustawiamy możliwość zaznaczania

        for ingredient in unavailable1:
            child = QTreeWidgetItem(potion1)
            child.setText(3, ingredient)  # Kolumna "Unavailable ingredients"
            child.setFlags(child.flags() | Qt.ItemIsSelectable)

        # Dodajemy dostępne składniki jako dzieci dla potion2
        available2 = ["Kryształ", "Esencja"]
        unavailable2 = ["Sok"]
        for ingredient in available2:
            child = QTreeWidgetItem(potion2)
            child.setText(2, ingredient)  # Kolumna "Available ingredients"
            child.setFlags(child.flags() | Qt.ItemIsSelectable)

        for ingredient in unavailable2:
            child = QTreeWidgetItem(potion2)
            child.setText(3, ingredient)  # Kolumna "Unavailable ingredients"
            child.setFlags(child.flags() | Qt.ItemIsSelectable)

        # Rozwijamy wszystkie elementy
        self.potions_tree_view.expandAll()

    # Metoda do pobierania aktualnie zaznaczonego składnika
    def get_selected_ingredient(self):
        selected_items = self.potions_tree_view.selectedItems()
        if selected_items:
            item = selected_items[0]
            # Sprawdzamy, w której kolumnie jest tekst (dostępne czy niedostępne składniki)
            available = item.text(2)
            unavailable = item.text(3)
            if available:
                return available, "available"
            elif unavailable:
                return unavailable, "unavailable"
        return None, None


# Przykład użycia w MainWindow z oknem informacyjnym
from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QDockWidget
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Alchemiczne Mikstury")

        # Tworzymy nasz widget
        self.potion_widget = PotionWidget()

        # Ustawiamy go jako centralny widget
        self.setCentralWidget(self.potion_widget)

        # Ustawiamy rozmiar okna
        self.resize(600, 400)

        # Wypełniamy przykładowymi danymi
        self.potion_widget.populate_example_data()

        # Podłączamy sygnał zmiany zaznaczenia
        self.potion_widget.potions_tree_view.itemSelectionChanged.connect(self.update_info)

    def update_info(self):
        ingredient, status = self.potion_widget.get_selected_ingredient()
        if ingredient:
            self.info_label.setText(f"Ingredient: {ingredient}\nStatus: {status}")
        else:
            self.info_label.setText("Select an ingredient to see details")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())