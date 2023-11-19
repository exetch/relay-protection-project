class MockSerial:
    def __init__(self):
        self.data_queue = []  # очередь для имитации данных, получаемых с порта

    def read(self):
        # Имитация чтения данных из порта
        if self.data_queue:
            return self.data_queue.pop(0)
        return b''

    def write(self, data):
        # Имитация отправки данных в порт
        print(f"Команда отправлена в порт: {data}")

    def close(self):
        print("Порт закрыт")

# Мок-версии функций чтения и отправки команд
def mock_read_data(ser, expected_data, stop_event):
    pass

def mock_send_command(ser, command):
    # Имитация отправки команды в порт
    ser.write(command)

measured_data = {

        1: {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 1, 16: 0, 17: 0,
            18: 0, 19: 0, 20: 0},
        2: {3: 1, 4: 1, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0,
            19: 0, 20: 0},
        3: {4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0,
            20: 0},
        4: {5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0},
        5: {6: 0, 7: 0, 8: 1, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0},
        6: {7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0},
        7: {8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0},
        8: {9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0},
        9: {10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0},
        10: {11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0},
        11: {12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0},
        12: {13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0},
        13: {14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0},
        14: {15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0},
        15: {16: 0, 17: 0, 18: 0, 19: 0, 20: 0},
        16: {17: 0, 18: 0, 19: 0, 20: 0},
        17: {18: 0, 19: 0, 20: 0},
        18: {19: 1, 20: 0},
        19: {20: 0},
    }
voltage_drop_issues = {  # Падение напряжения для контактов 5-8 превышает допустимое
}