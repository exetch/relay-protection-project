from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, \
    QComboBox, QMessageBox, QCompleter, QHBoxLayout, QHeaderView, QFormLayout
from PyQt5.QtCore import Qt
import json

button_style = """
QPushButton {
    height: 40px;
    border: 2px solid #8f8f91;
    border-radius: 6px;
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f6f7fa, stop:1 #dadbde);
    min-width: 80px;
}

QPushButton:pressed {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #dadbde, stop:1 #f6f7fa);
}

QPushButton:hover {
    border: 2px solid #1c1c1c;
}
"""
line_edit_style = "QLineEdit { padding: 5px; border-style: solid; border-width: 1px; border-radius: 4px; border-color: #b6b6b6; }"

table_style = """
QTableWidget {
  border: 1px solid #d3d3d3;
  border-radius: 5px;
}

QTableWidget::item {
  border: 1px solid #d3d3d3;
}

QHeaderView::section {
  background-color: lightblue;
  padding: 4px;
  border: 1px solid #d3d3d3;
  border-radius: 5px;
}
"""

class AddRelayProtectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить блок")
        self.setGeometry(200, 200, 580, 684)
        self.setFont(QFont("Arial", 10))

        self.label_vendor_code = QLabel("Введите артикул блока:", self)
        self.line_edit_vendor_code = QLineEdit(self)
        self.line_edit_vendor_code.setStyleSheet(line_edit_style)

        self.label_voltage_drop = QLabel("Введите допустимое падение напряжения (мВ):", self)
        self.line_edit_voltage_drop = QLineEdit(self)
        self.line_edit_voltage_drop.setStyleSheet(line_edit_style)

        self.button_save_relay_protection = QPushButton("Сохранить блок", self)
        self.button_save_relay_protection.setStyleSheet(button_style)

        self.table1 = QTableWidget(10, 2)
        self.table1.setHorizontalHeaderLabels(["Контакт 1", "Контакт 2"])
        self.table1.verticalHeader().setVisible(False)
        self.table1.setStyleSheet(table_style)

        self.table2 = QTableWidget(10, 2)
        self.table2.setHorizontalHeaderLabels(["Контакт 1", "Контакт 2"])
        self.table2.verticalHeader().setVisible(False)
        self.table2.setStyleSheet(table_style)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        layout.addWidget(self.label_vendor_code)
        layout.addWidget(self.line_edit_vendor_code)
        layout.addWidget(self.label_voltage_drop)
        layout.addWidget(self.line_edit_voltage_drop)

        tables_layout = QHBoxLayout()
        tables_layout.setContentsMargins(5, 5, 5, 5)
        tables_layout.setSpacing(5)

        position_1_layout = QVBoxLayout()
        label_position_1 = QLabel("Положение 1", self)
        label_position_1.setAlignment(Qt.AlignCenter)
        label_position_1.setStyleSheet("QLabel { color: red; font-weight: bold; }")
        position_1_layout.setContentsMargins(10, 10, 10, 10)
        position_1_layout.addWidget(label_position_1)
        position_1_layout.addWidget(self.table1)

        position_2_layout = QVBoxLayout()
        label_position_2 = QLabel("Положение 2", self)
        label_position_2.setAlignment(Qt.AlignCenter)
        label_position_2.setStyleSheet("QLabel { color: blue; font-weight: bold; }")
        position_2_layout.setContentsMargins(10, 10, 10, 10)
        position_2_layout.addWidget(label_position_2)
        position_2_layout.addWidget(self.table2)

        tables_layout.addLayout(position_1_layout)
        tables_layout.addLayout(position_2_layout)

        layout.addLayout(tables_layout)

        layout.addWidget(self.button_save_relay_protection)

        self.setLayout(layout)

        self.relay_protection_data = {
            "vendor_code": "",
            "permissible_voltage_drop": 10,
            "position_1": [],
            "position_2": []
        }

        self.button_save_relay_protection.clicked.connect(self.save_relay_protection)

    def save_relay_protection(self):
        try:
            self.relay_protection_data["vendor_code"] = self.line_edit_vendor_code.text()
            voltage_drop_text = self.line_edit_voltage_drop.text()
            self.relay_protection_data["permissible_voltage_drop"] = int(voltage_drop_text) if voltage_drop_text else 10

            for table, position in [(self.table1, "position_1"), (self.table2, "position_2")]:
                contacts = []
                for row in range(20):
                    contact1_item = table.item(row, 0)
                    contact2_item = table.item(row, 1)
                    if contact1_item is not None and contact2_item is not None:
                        contact1 = int(contact1_item.text())
                        contact2 = int(contact2_item.text())
                        contacts.append([contact1, contact2])
                self.relay_protection_data[position] = contacts

            filename = "relay_protections_data.json"
            try:
                with open(filename, "r", encoding='utf-8') as file:
                    data = json.load(file)
            except FileNotFoundError:
                data = []

            data.append(self.relay_protection_data)
            with open(filename, "w", encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False, separators=(", ", ": "))
            self.parent().update_vendor_selection()
            self.parent().update_completer_old()
            QMessageBox.information(self, "Информация", "Блок сохранен")
            self.close()
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")

class EditRelayProtectionDialog(AddRelayProtectionDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать блок")
        self.init_vendor_code_completer()

    def init_vendor_code_completer(self):
        try:
            with open("relay_protections_data.json", "r", encoding='utf-8') as file:
                data = json.load(file)
            # Создание списка артикулов для автозаполнения
            vendor_codes = [rp["vendor_code"] for rp in data]
            completer = QCompleter(vendor_codes, self)
            completer.activated.connect(self.on_vendor_code_selected)
            self.line_edit_vendor_code.setCompleter(completer)
        except FileNotFoundError:
            QMessageBox.warning(self, "Предупреждение", "Файл с данными не найден.")
            self.close()

    def on_vendor_code_selected(self, text):
        self.load_relay_protection_data(text)


    def load_relay_protection_data(self, vendor_code):
        try:
            with open("relay_protections_data.json", "r", encoding='utf-8') as file:
                data = json.load(file)
            relay_protection = next((rp for rp in data if rp['vendor_code'] == vendor_code), None)
            if relay_protection:
                self.line_edit_voltage_drop.setText(str(relay_protection['permissible_voltage_drop']))
                # Заполняем таблицу position_1
                for i, contact_pair in enumerate(relay_protection['position_1']):
                    self.table1.setItem(i, 0, QTableWidgetItem(str(contact_pair[0])))
                    self.table1.setItem(i, 1, QTableWidgetItem(str(contact_pair[1])))

                # Заполняем таблицу position_2
                for i, contact_pair in enumerate(relay_protection['position_2']):
                    self.table2.setItem(i, 0, QTableWidgetItem(str(contact_pair[0])))
                    self.table2.setItem(i, 1, QTableWidgetItem(str(contact_pair[1])))
            else:
                QMessageBox.warning(self, "Предупреждение", "Блок с данным артикулом не найден.")
        except FileNotFoundError:
            QMessageBox.warning(self, "Предупреждение", "Файл с данными не найден.")
            self.close()

    def save_relay_protection(self):
        # Обновляем данные из интерфейса
        self.relay_protection_data["vendor_code"] = self.line_edit_vendor_code.text()
        voltage_drop_text = self.line_edit_voltage_drop.text()
        self.relay_protection_data["permissible_voltage_drop"] = int(voltage_drop_text) if voltage_drop_text else 10

        # Собираем контакты из таблиц
        for table, position_key in [(self.table1, "position_1"), (self.table2, "position_2")]:
            contacts = []
            for row in range(table.rowCount()):
                contact1_item = table.item(row, 0)
                contact2_item = table.item(row, 1)
                if contact1_item and contact2_item and contact1_item.text() and contact2_item.text():
                    contact1 = int(contact1_item.text())
                    contact2 = int(contact2_item.text())
                    contacts.append([contact1, contact2])
            self.relay_protection_data[position_key] = contacts

        try:
            with open("relay_protections_data.json", "r", encoding='utf-8') as file:
                data = json.load(file)

            for i, rp in enumerate(data):
                if rp['vendor_code'] == self.relay_protection_data['vendor_code']:
                    data[i] = self.relay_protection_data
                    break

            with open("relay_protections_data.json", "w", encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False, separators=(", ", ": "))

            QMessageBox.information(self, "Информация", "Изменения в блоке сохранены")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"При сохранении изменений произошла ошибка: {e}")
            print(f"Произошла ошибка: {e}")


class DelRelayProtectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удалить данные о реле")
        self.setGeometry(200, 200, 400, 200)
        self.setFont(QFont("Arial", 10))

        # Элементы интерфейса
        self.label = QLabel("Введите артикул реле:", self)
        self.line_edit = QLineEdit(self)
        self.delete_button = QPushButton("Удалить", self)
        self.cancel_button = QPushButton("Отмена", self)

        # Расположение элементов
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

        # Связывание кнопок с методами
        self.delete_button.clicked.connect(self.show_confirm_dialog)
        self.cancel_button.clicked.connect(self.close)

        # Инициализация автозаполнения
        self.create_completer()

    def create_completer(self):
        try:
            with open("relay_protections_data.json", "r", encoding='utf-8') as file:
                data = json.load(file)
            vendor_codes = [rp["vendor_code"] for rp in data]
            completer = QCompleter(vendor_codes, self)
            self.line_edit.setCompleter(completer)
        except FileNotFoundError:
            QMessageBox.warning(self, "Предупреждение", "Файл с данными не найден.")

    def show_confirm_dialog(self):
        vendor_code = self.line_edit.text()
        reply = QMessageBox.question(self, 'Подтверждение',
                                     f"Вы уверены, что хотите удалить блок с артикулом {vendor_code}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.delete_relay_protection()

    def delete_relay_protection(self):
        vendor_code = self.line_edit.text()
        try:
            with open("relay_protections_data.json", "r", encoding='utf-8') as file:
                data = json.load(file)

            data = [rp for rp in data if rp['vendor_code'] != vendor_code]

            with open("relay_protections_data.json", "w", encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False, separators=(", ", ": "))
            self.parent().update_vendor_selection()
            self.parent().update_completer_old()
            QMessageBox.information(self, "Информация", "Блок удален.")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"При удалении произошла ошибка: {e}")


