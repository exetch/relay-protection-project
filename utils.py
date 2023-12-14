import struct
import traceback

import serial.tools.list_ports
import json
from time import sleep
import pickle
import keyboard

SPACE_KEY = b' '
NEXT_POSITION_SIGNAL = b'\x89'
CORRECTNESS_COMMAND = b'\x83'
INCORRECTNESS_COMMAND = b'\x84'
RESET_SIGNAL = b'\x80'
FILENAME = 'relay_protections_data.json'


def get_open_com_ports():
    ports = serial.tools.list_ports.comports()
    open_com_ports = []
    for port in ports:
        if port.hwid:
            open_com_ports.append(port.device)
    return open_com_ports


def load_rp_data(filename):
    with open(filename) as file:
        data = json.load(file)
        return data



def get_rp_data(vendor_code):
    rp_data = load_rp_data(FILENAME)
    for rp in rp_data:
        if rp['vendor_code'] == vendor_code:
            return rp

    return None


def check_position(switch_data, measured_data):
    incorrect_closed = []
    incorrect_opened = []

    for closed_contacts in switch_data:
        contact1, contact2 = closed_contacts
        if (
                contact1 in measured_data
                and contact2 in measured_data[contact1]
                and measured_data[contact1][contact2] == 0
        ):
            incorrect_opened.append(closed_contacts)

    for contact1 in measured_data:
        for contact2 in measured_data[contact1]:
            contact_pair = [contact1, contact2]

            if (
                    contact_pair not in switch_data
                    and measured_data[contact1][contact2] == 1
            ):
                # Контакты замкнуты, но должны быть разомкнуты
                incorrect_closed.append((contact1, contact2))

    return incorrect_closed, incorrect_opened


# def read_data(stop_event):
#     while True:
#         try:
#             if stop_event.is_set() or keyboard.is_pressed(' '):
#                 sleep(0.2)
#                 break
#         except Exception as e:
#             print(f"Произошла ошибка: {e}")
#             traceback.print_exc()  # Вывести трассировку стека
def read_data(stop_event):
    try:
        keyboard.wait(' ')
        print("space is pressed.")
    except keyboard.KeyboardEvent as e:
        if e.event_type == keyboard.KEY_DOWN:
            print(f"Произошла ошибка: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def read_voltage_drop(ser, position):
    voltage_drop_bytes = ser.read(4)  # Чтение 4 байтов
    voltage_drop = struct.unpack('f', voltage_drop_bytes)[0]  # Преобразование в число с плавающей точкой
    return voltage_drop / 2 if position == 2 else voltage_drop


def send_command(instance, ser, command):
    print('sending command')
    sleep(0.05)
    ser.write(command)

def process_position(ser, relay_protection_data, position, instance):
    measured_data = {}
    voltage_drop_issues = {} # Словарь для хранения превышений падения напряжения
    measured_voltage_drops = {}

    # if position == 1:
    #     measured_data = {
    #
    #         1: {2: 1, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0,
    #             18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         2: {3: 1, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0,
    #             18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         3: {4: 1, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0,
    #             18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         4: {5: 1, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0,
    #             18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         5: {6: 1, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0,
    #             18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         6: {7: 1, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0,
    #             18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         7: {8: 1, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0,
    #             18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         8: {9: 1, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0,
    #             24: 0,
    #             25: 0},
    #         9: {10: 1, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0,
    #             25: 0},
    #         10: {11: 1, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0,
    #              25: 0},
    #         11: {12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         12: {13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         13: {14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         14: {15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         15: {16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         16: {17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         17: {18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         18: {19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         19: {20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         20: {21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         21: {22: 0, 23: 0, 24: 0, 25: 0},
    #         22: {23: 0, 24: 0, 25: 0},
    #         23: {24: 0, 25: 0},
    #         24: {25: 0},
    #
    #     }
    #     voltage_drop_issues = {}
    #     measured_voltage_drops = {(1, 2): 100, (2, 3): 150, (4, 5): 100, (10, 11): 199}
    # if position == 2:
    #     measured_data = {
    #
    #         1: {2: 0, 3: 0, 4: 1, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0,
    #             18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         2: {3: 0, 4: 0, 5: 1, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0,
    #             18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         3: {4: 0, 5: 0, 6: 1, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0,
    #             18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         4: {5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0,
    #             18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         5: {6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0,
    #             18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         6: {7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0,
    #             18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         7: {8: 0, 9: 0, 10: 1, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0,
    #             18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         8: {9: 0, 10: 1, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0,
    #             24: 0,
    #             25: 0},
    #         9: {10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0,
    #             25: 0},
    #         10: {11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0,
    #              25: 0},
    #         11: {12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         12: {13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         13: {14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         14: {15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         15: {16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         16: {17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         17: {18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         18: {19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         19: {20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         20: {21: 0, 22: 0, 23: 0, 24: 0, 25: 0},
    #         21: {22: 0, 23: 0, 24: 0, 25: 0},
    #         22: {23: 0, 24: 0, 25: 0},
    #         23: {24: 0, 25: 0},
    #         24: {25: 0},
    #
    #     }
    #     voltage_drop_issues = {(2, 3): 310, (3, 4): 400, (8, 9): 350, (10,11): 400}
    #     measured_voltage_drops = {(2, 3): 310, (3, 4): 400, (7, 8): 100, (8, 9): 350, (10, 11): 400}
    for i in range(1, 26):  # Перебор 26 контактов
        first_contact_byte = ser.read()
        first_contact_number = first_contact_byte[0] & 0x3F

        contact_status = {}
        while True:
            contact_byte = ser.read()
            if contact_byte == b'\x86':  # Конец чтения данных для этого контакта
                break

            contact_number = contact_byte[0] & 0x3F
            contact_state = (contact_byte[0] & 0xC0) >> 6
            contact_status[contact_number] = contact_state

            if contact_state == 1:  # Если контакты замкнуты
                voltage_drop = read_voltage_drop(ser, position)
                measured_voltage_drops[(first_contact_number, contact_number)] = voltage_drop
                if voltage_drop > relay_protection_data[f"permissible_voltage_drop_position_{position}"]:
                    voltage_drop_issues[(first_contact_number, contact_number)] = voltage_drop

        measured_data[first_contact_number] = contact_status

    incorrect_closed, incorrect_opened = check_position(relay_protection_data[f'position_{position}'], measured_data)
    instance.updateTableSignal.emit(position, relay_protection_data[f'position_{position}'], measured_data, voltage_drop_issues, measured_voltage_drops)



    if len(incorrect_closed) == 0 and len(incorrect_opened) == 0 and len(voltage_drop_issues) == 0:
        print(f"in {position} all correct.")
        print('before add message about contacts')
        sleep(0.05)
        instance.add_message_to_widget(f"В положении {position} все хорошо. Положение собрано корректно")
        print('after add message about contacts')

        return position
    else:
        print(f"Положение {position} собрано некорректно. Некорректные контакты:")
        sleep(0.1)
        instance.add_message_to_widget(f"\nПоложение {position} собрано некорректно. Некорректные контакты:")
        for closed_contact in incorrect_closed:
            print(f"Замкнуты контакты {closed_contact[0]} и {closed_contact[1]}")
            sleep(0.1)
            instance.add_message_to_widget(f"Замкнуты контакты {closed_contact[0]} и {closed_contact[1]}")
        for opened_contact in incorrect_opened:
            print(f"Разомкнуты контакты {opened_contact[0]} и {opened_contact[1]}")
            sleep(0.1)
            instance.add_message_to_widget(f"Разомкнуты контакты {opened_contact[0]} и {opened_contact[1]}")
        for contact_pair, voltage in voltage_drop_issues.items():
            print(f"Контакты {contact_pair[0]} и {contact_pair[1]} с падением напряжения {voltage} мВ")
            sleep(0.05)
            instance.add_message_to_widget(f"Контакты {contact_pair[0]} и {contact_pair[1]} с падением напряжения {voltage} мВ")

        return []



def load_saved_vendor_code(combo_box_vendor_code):
    try:
        with open('saved_vendor_code.pickle', 'rb') as file:
            saved_code = pickle.load(file)
        if saved_code:
            combo_box_vendor_code.setCurrentText(saved_code)
    except (FileNotFoundError, EOFError):
        pass



def save_vendor_code(combo_box_vendor_code):
    vendor_code = combo_box_vendor_code.currentText()
    with open("saved_vendor_code.pickle", 'wb') as file:
        pickle.dump(vendor_code, file)

def save_selected_port(combo_box_ports):
    selected_port = combo_box_ports.currentText()
    with open('saved_port.pickle', 'wb') as file:
        pickle.dump(selected_port, file)

def load_saved_port(combo_box_ports):
    try:
        with open('saved_port.pickle', 'rb') as file:
            saved_port = pickle.load(file)
        if saved_port:
            index = combo_box_ports.findText(saved_port)
            if index != -1:
                combo_box_ports.setCurrentIndex(index)
    except (FileNotFoundError, EOFError):
        pass

def save_tests_counter(tests_counter):
    with open("tests_counter.pkl", "wb") as file:
        pickle.dump(tests_counter, file)

def load_tests_counter():
    try:
        with open("tests_counter.pkl", "rb") as file:
            if file.peek(1):
                return pickle.load(file)
            else:
                return {}
    except (FileNotFoundError, EOFError):
        return {}

def update_user_tests_counter(username, tests_count):
    tests_counter = load_tests_counter()
    tests_counter[username] = tests_count
    save_tests_counter(tests_counter)

