from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QCompleter,QMessageBox, QComboBox
from PyQt5.QtCore import QStringListModel

def add_user(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Добавить пользователя")
    dialog.resize(250, 75)

    layout = QVBoxLayout(dialog)

    name_label = QLabel("Имя пользователя:")
    name_input = QLineEdit()
    layout.addWidget(name_label)
    layout.addWidget(name_input)

    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)

    if dialog.exec_() == QDialog.Accepted:
        user_name = name_input.text().strip()
        if user_name:
            with open("users.txt", "a", encoding='utf-8') as file:
                file.write(user_name + "\n")
            QMessageBox.information(parent, "Добавление пользователя", f"Пользователь {user_name} добавлен")

def del_user(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Удалить пользователя")

    layout = QVBoxLayout(dialog)

    name_label = QLabel("Имя пользователя:")
    name_input = QLineEdit()
    layout.addWidget(name_label)
    layout.addWidget(name_input)

    completer = QCompleter()
    model = QStringListModel()
    completer.setModel(model)
    name_input.setCompleter(completer)

    with open("users.txt", "r", encoding='utf-8') as file:
        users = [line.strip() for line in file]
        model.setStringList(users)

    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)

    if dialog.exec_() == QDialog.Accepted:
        user_name = name_input.text().strip()
        if user_name:
            with open("users.txt", "r", encoding='utf-8') as file:
                lines = file.readlines()
            with open("users.txt", "w", encoding='utf-8') as file:
                for line in lines:
                    if line.strip() != user_name:
                        file.write(line)
            QMessageBox.information(parent, "Удаление пользователя", f"Пользователь {user_name} удален")


