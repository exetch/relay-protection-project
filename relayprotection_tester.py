from PyQt5.QtWidgets import QMainWindow, QToolBar, QAction, QMenu, QWidget, QLabel, QCompleter, QTableWidget, \
    QTableWidgetItem, QVBoxLayout, QPushButton, QApplication, QHBoxLayout, QComboBox, QSplitter, QSizePolicy, QTextEdit, \
    QScrollArea, QMessageBox
from PyQt5.QtCore import Qt, QMetaObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QBrush
import json
import threading
import sys
from utils import get_open_com_ports, load_saved_vendor_code, save_vendor_code, save_selected_port, load_saved_port, \
    save_tests_counter, load_tests_counter, update_user_tests_counter
from configuration import AddRelayProtectionDialog, EditRelayProtectionDialog, DelRelayProtectionDialog
from data_processing import data_processing
from users import add_user, del_user



class MainWindow(QMainWindow):
    updateTableSignal = pyqtSignal(int, list, dict, dict, dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Block Tester")
        self.setGeometry(0, 0, 1290, 990)
        self.init_toolbar()
        self.init_vendor_selection()
        self.init_table_widget()
        self.message_widget = QTextEdit()

        self.init_layout()
        self.updateTableSignal.connect(self.update_table_with_results_slot)
        self.tests_counter = load_tests_counter()
        self.update_tests_counter_label()
        load_saved_vendor_code(self.combo_box_vendor_code)
        load_saved_port(self.combo_box_ports)
        self.stop_event = threading.Event()

    def init_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        configuration_menu = QMenu("Конфигурация", self)
        user_menu = QMenu("Пользователь", self)

        add_switch_action = QAction("Добавить блок", self)
        add_switch_action.triggered.connect(self.open_add_switch_dialog)
        configuration_menu.addAction(add_switch_action)

        edit_switch_action = QAction("Редактировать блок", self)
        edit_switch_action.triggered.connect(self.edit_switch)
        configuration_menu.addAction(edit_switch_action)

        delete_switch_action = QAction("Удалить блок", self)
        delete_switch_action.triggered.connect(self.open_del_switch_dialog)
        configuration_menu.addAction(delete_switch_action)

        add_user_action = QAction("Добавить пользователя", self)
        add_user_action.triggered.connect(self.add_user)
        user_menu.addAction(add_user_action)

        delete_user_action = QAction("Удалить пользователя", self)
        delete_user_action.triggered.connect(self.del_user)
        user_menu.addAction(delete_user_action)

        configuration_button = CustomButton("Конфигурация")
        configuration_button.setMenu(configuration_menu)

        user_button = CustomButton("Пользователь")
        user_button.setMenu(user_menu)

        configuration_button.clicked.connect(configuration_menu.exec_)
        user_button.clicked.connect(user_menu.exec_)

        toolbar.addWidget(configuration_button)

        toolbar.addWidget(user_button)
        space = QLabel("")
        space.setMinimumWidth(63)
        toolbar.addWidget(space)

        active_user_label = QLabel("Выбрать пользователя:")
        active_user_label.setMinimumWidth(150)
        toolbar.addWidget(active_user_label)

        self.user_combobox = QComboBox()
        self.user_combobox.setFixedHeight(27)
        self.user_combobox.setFixedWidth(200)
        toolbar.addWidget(self.user_combobox)

        self.update_user_combobox()

        self.setCentralWidget(QWidget())
        self.user_combobox.currentIndexChanged.connect(self.update_tests_counter_label)

    def init_vendor_selection(self):
        self.vendor_selection = QWidget(self)

        vendor_selection_layout = QHBoxLayout(self.vendor_selection)

        self.label_vendor_code = QLabel("Артикул блока:", self.vendor_selection)
        self.combo_box_vendor_code = QComboBox(self.vendor_selection)
        self.combo_box_vendor_code.setEditable(True)
        self.combo_box_vendor_code.setCompleter(self.create_completer_old())
        self.create_completer()
        self.search_button = QPushButton("Найти", self.vendor_selection)
        self.start_button = QPushButton("Старт", self.vendor_selection)
        self.stop_button = QPushButton("Стоп", self.vendor_selection)
        self.clear_button = QPushButton("Очистить", self.vendor_selection)
        self.reset_counter_button = QPushButton("Сброс", self.vendor_selection)

        self.label_vendor_code.setFixedWidth(150)
        self.combo_box_vendor_code.setFixedWidth(175)
        self.search_button.setFixedWidth(75)
        self.start_button.setFixedWidth(75)
        self.stop_button.setFixedWidth(75)
        self.clear_button.setFixedWidth(75)

        vendor_selection_layout.addWidget(self.label_vendor_code)
        vendor_selection_layout.addWidget(self.combo_box_vendor_code)
        vendor_selection_layout.addWidget(self.search_button)
        vendor_selection_layout.addWidget(self.start_button)
        vendor_selection_layout.addWidget(self.stop_button)
        vendor_selection_layout.addWidget(self.clear_button)

        self.label_select_port = QLabel("Выберите порт:", self.vendor_selection)
        self.combo_box_ports = QComboBox(self.vendor_selection)
        self.combo_box_ports.setFixedHeight(27)

        vendor_selection_layout.addWidget(self.label_select_port)
        vendor_selection_layout.addWidget(self.combo_box_ports)

        vendor_selection_layout.addStretch(1)

        self.combo_box_vendor_code.lineEdit().returnPressed.connect(self.retrieve_rp_data)
        self.search_button.clicked.connect(self.retrieve_rp_data)
        self.search_button.clicked.connect(self.clear_message_widget)
        self.start_button.clicked.connect(self.run_data_processing)
        self.stop_button.clicked.connect(self.stop_data_processing)
        self.clear_button.clicked.connect(self.clear_message_widget)
        self.start_button.clicked.connect(self.init_layout)

        open_ports = get_open_com_ports()
        self.combo_box_ports.addItems(open_ports)
        self.label_tests_counter = QLabel("Тестов выполнено: 0", self.vendor_selection)
        self.label_tests_counter.setFixedWidth(200)
        vendor_selection_layout.addWidget(self.label_tests_counter)
        vendor_selection_layout.addWidget(self.reset_counter_button)
        self.reset_counter_button.clicked.connect(self.reset_tests_counter)


    def reset_tests_counter(self):
        username = self.user_combobox.currentText()
        self.tests_counter[username] = 0
        self.update_tests_counter_label()

    def update_tests_counter_label(self):
        username = self.user_combobox.currentText()
        tests_count = self.tests_counter.get(username, 0)
        self.label_tests_counter.setText(f"Счетчик тестов {username}: {tests_count}")
        update_user_tests_counter(username, tests_count)

    def init_table_widget(self):
        # Инициализация таблиц
        self.table_widget_position_1 = QTableWidget(self)
        self.table_widget_position_2 = QTableWidget(self)

        # Настройка таблиц для отображения 25 строк и 25 столбцов
        self.table_widget_position_1.setRowCount(26)
        self.table_widget_position_1.setColumnCount(26)
        self.table_widget_position_2.setRowCount(26)
        self.table_widget_position_2.setColumnCount(26)

        # Установка размера ячеек для обеих таблиц
        for i in range(26):
            self.table_widget_position_1.setRowHeight(i, 25)
            self.table_widget_position_1.setColumnWidth(i, 25)
            self.table_widget_position_2.setRowHeight(i, 25)
            self.table_widget_position_2.setColumnWidth(i, 25)
        # Создание заголовков для строк и столбцов
        headers = [str(i) for i in range(1, 26)]
        self.table_widget_position_1.setHorizontalHeaderLabels(headers)
        self.table_widget_position_1.setVerticalHeaderLabels(headers)
        self.table_widget_position_2.setHorizontalHeaderLabels(headers)
        self.table_widget_position_2.setVerticalHeaderLabels(headers)

        blue_background_style = """
        QHeaderView::section {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                              stop:0 #6db9e8, stop: 0.5 #5daee4, stop:1 #4da0df);
            padding: 4px;
            border: 1px solid #6db9e8;
            font-size: 12pt;
            font-weight: bold;
            color: white;
            height: 28px;
            text-align: center;
            box-shadow: 0 4px 6px -6px #222;
        }
        """

        self.table_widget_position_1.horizontalHeader().setStyleSheet(blue_background_style)
        self.table_widget_position_1.verticalHeader().setStyleSheet(blue_background_style)

        self.table_widget_position_2.horizontalHeader().setStyleSheet(blue_background_style)
        self.table_widget_position_2.verticalHeader().setStyleSheet(blue_background_style)



    def create_completer(self):
        with open('relay_protections_data.json', 'r') as file:
            data = json.load(file)
            vendor_codes = [switch['vendor_code'] for switch in data]
            sorted_vendor_codes = sorted(vendor_codes, key=lambda
                x: x.lower())  # Сортировка элементов по алфавиту (без учета регистра)
            self.combo_box_vendor_code.addItems(sorted_vendor_codes)

    def create_completer_old(self):
        with open('relay_protections_data.json', 'r') as file:
            data = json.load(file)
            vendor_codes = [switch['vendor_code'] for switch in data]
            sorted_vendor_codes = sorted(vendor_codes, key=lambda
                x: x.lower())  # Сортировка элементов по алфавиту (без учета регистра)
            completer = QCompleter(sorted_vendor_codes)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            return completer

    def update_completer_old(self):
        with open('relay_protections_data.json', 'r') as file:
            data = json.load(file)
            vendor_codes = [switch['vendor_code'] for switch in data]
            sorted_vendor_codes = sorted(vendor_codes, key=lambda x: x.lower())
        self.combo_box_vendor_code.setCompleter(None)
        completer = QCompleter(sorted_vendor_codes)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.combo_box_vendor_code.setCompleter(completer)

    def retrieve_rp_data(self):
        vendor_code = self.combo_box_vendor_code.currentText()
        save_vendor_code(self.combo_box_vendor_code)
        save_selected_port(self.combo_box_ports)
        try:
            with open('relay_protections_data.json', 'r') as file:
                data = json.load(file)
                relay_protection = next((rp for rp in data if rp['vendor_code'] == vendor_code), None)
                if relay_protection:
                    self.display_rp_info(relay_protection)
                else:
                    QMessageBox.warning(self, "Предупреждение", "Блок с данным артикулом не найдено.")
        except FileNotFoundError:
            QMessageBox.warning(self, "Предупреждение", "Файл с данными не найден.")

    def display_rp_info(self, relay_protection):
        self.table_widget_position_1.clearContents()
        self.table_widget_position_2.clearContents()

        self.fill_table_with_data(self.table_widget_position_1, relay_protection["position_1"],
                                  relay_protection["permissible_voltage_drop_position_1"])
        self.fill_table_with_data(self.table_widget_position_2, relay_protection["position_2"],
                                  relay_protection["permissible_voltage_drop_position_2"])

    def fill_table_with_data(self, table_widget, position_data, voltage_drop):
        for contact_pair in position_data:

            contact1, contact2 = map(int, contact_pair)

            item = QTableWidgetItem(str(voltage_drop))

            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

            table_widget.setItem(contact1 - 1, contact2 - 1, item)
    def init_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        layout_table = QHBoxLayout()
        layout_table.addWidget(self.table_widget_position_1)
        layout_table.addWidget(self.table_widget_position_2)

        self.setLayout(layout_table)
        self.table_widget_position_1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_widget_position_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.vendor_selection)
        main_layout.addLayout(layout_table)

        contact_info_widget = QWidget()
        contact_info_layout = QHBoxLayout(contact_info_widget)
        contact_info_layout.setContentsMargins(20, 10, 0, 10)

        color_mapping = {
            "green": ("Соответствует схеме", "#00FF00"),
            "red": ("Не соответствует схеме, не замкнуты", "#FF0000"),
            "yellow": ("Не соответствует схеме, замкнуты", "#FFFF00"),
        }

        for color, (label_text, color_code) in color_mapping.items():
            color_rect = QLabel()
            color_rect.setFixedSize(25, 25)
            color_rect.setStyleSheet(f"background-color: {color_code};")

            color_label = QLabel(label_text)

            contact_info_layout.addWidget(color_rect)
            contact_info_layout.addWidget(color_label)

        main_layout.addWidget(contact_info_widget)
        message_scroll_area = QScrollArea()
        message_scroll_area.setWidgetResizable(True)
        message_scroll_area.setWidget(self.message_widget)

        desired_height = 200
        message_scroll_area.setFixedHeight(desired_height)
        # message_scroll_area.setMinimumHeight(desired_height)
        # message_scroll_area.setMaximumHeight(desired_height)

        main_layout.addWidget(message_scroll_area)

        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

    def open_add_switch_dialog(self):
        dialog = AddRelayProtectionDialog(self)
        dialog.exec_()

    def update_vendor_selection(self):
        self.combo_box_vendor_code.clear()
        completer = self.create_completer()
        self.combo_box_vendor_code.setCompleter(completer)

    def edit_switch(self):
        edit_dialog = EditRelayProtectionDialog(self)
        edit_dialog.exec_()

    def open_del_switch_dialog(self):
        dialog = DelRelayProtectionDialog(self)
        dialog.exec_()

    def run_data_processing(self):
        port = self.combo_box_ports.currentText()
        vendor_code = self.combo_box_vendor_code.currentText()
        username = self.user_combobox.currentText()

        processing_thread = threading.Thread(
            target=data_processing, args=(port, vendor_code, self.stop_event, self, username)
        )
        processing_thread.start()



    def update_user_combobox(self):
        with open("users.txt", "r", encoding="utf-8") as file:
            users = [line.strip() for line in file]
        self.user_combobox.clear()
        self.user_combobox.addItems(users)

    def stop_data_processing(self):
        self.stop_event.set()
        self.retrieve_rp_data()


    def add_user(self):
        add_user(self)
        self.update_user_combobox()

    def del_user(self):
        del_user(self)
        self.update_user_combobox()

    def add_message_to_widget(self, message):
        self.message_widget.append(message)

    def clear_message_widget(self):
        QMetaObject.invokeMethod(self.message_widget, "clear")

    @pyqtSlot(int, list, dict, dict, dict)
    def update_table_with_results_slot(self, position, switch_data, measured_data, voltage_drop_issues, measured_voltage_drops):
        all_contacts_correct = True

        table_widget = self.table_widget_position_1 if position == 1 else self.table_widget_position_2

        for contact_pair in switch_data:
            contact1, contact2 = map(int, contact_pair)
            item = table_widget.item(contact1 - 1, contact2 - 1)
            if item is not None:
                if measured_data[contact1][contact2] == 1:
                    item.setBackground(QColor("green"))
                    voltage_drop = measured_voltage_drops.get((contact1, contact2), 0)
                    item.setText(str(voltage_drop))
                    item.setTextAlignment(Qt.AlignCenter)
                    if (contact1, contact2) in voltage_drop_issues:
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                        item.setForeground(QBrush(QColor("red")))
                    else:
                        item.setForeground(QBrush(QColor("black")))
                else:
                    item.setBackground(QColor("red"))
                    all_contacts_correct = False

        for contact1 in measured_data:
            for contact2 in measured_data[contact1]:
                if [contact1, contact2] not in switch_data and measured_data[contact1][contact2] == 1:
                    item = table_widget.item(contact1 - 1, contact2 - 1)
                    if item is None:
                        item = QTableWidgetItem()
                        table_widget.setItem(contact1 - 1, contact2 - 1, item)
                    item.setBackground(QColor("yellow"))
                    voltage_drop = measured_voltage_drops.get((contact1, contact2), 0)
                    item.setText(str(voltage_drop))
                    all_contacts_correct = False
                    item.setTextAlignment(Qt.AlignCenter)

                    if (contact1, contact2) in voltage_drop_issues:
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                        item.setForeground(QBrush(QColor("red")))
                        item.setText(str(voltage_drop_issues[(contact1, contact2)]))


    def closeEvent(self, event):
        self.stop_event.set()
        self.processing_thread.join()

        if self.ser.is_open:
            self.ser.close()

        super().closeEvent(event)

class CustomButton(QPushButton):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            event.ignore()
        else:
            super().keyPressEvent(event)
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()