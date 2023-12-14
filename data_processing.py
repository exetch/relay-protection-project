import traceback
from time import sleep

import serial
from utils import get_rp_data, send_command, process_position, read_data
from utils import update_user_tests_counter

RESET_SIGNAL = b'\x80'
READY_SIGNAL = b'\x87'
START_MEASUREMENT_COMMAND = b'\x82'
CORRECTNESS_COMMAND = b'\x83'
INCORRECTNESS_COMMAND = b'\x84'
CORRECT_ALL_COMMAND = b'\x85'
CONTACTS_COUNT = b'\x88'
NEXT_POSITION_SIGNAL = b'\x89'
SPACE_KEY = b' '


def data_processing(port, vendor_code, stop_event, instance, username):
    reset_signal_received = False

    baudrate = 256000
    ser = serial.Serial(port, baudrate)
    while True:
        sleep(0.05)
        instance.clear_message_widget()
        instance.retrieve_rp_data()
        instance.add_message_to_widget('Старт теста! Нажмите пробел')
        instance.tests_counter[username] = instance.tests_counter.get(username, 0) + 1
        update_user_tests_counter(username, instance.tests_counter[username])
        read_data(stop_event)
        if stop_event.is_set():
            stop_event.clear()
            break
        instance.update_tests_counter_label()

        while True:
            if stop_event.is_set():
                stop_event.clear()
                break
            if reset_signal_received:
                reset_signal_received = False
            rp_data = get_rp_data(vendor_code)

            correct_positions = []
            incorrect_positions = []

            for position in range(1, 3):
                send_command(instance, ser, START_MEASUREMENT_COMMAND)
                if process_position(ser, rp_data, position, instance):
                    correct_positions.append(position)
                else:
                    incorrect_positions.append(position)

                if position == 2:
                    print('before exit')
                    break
                sleep(0.05)
                instance.add_message_to_widget('Нажмите пробел для измерения положения №2')
                read_data(stop_event)
                instance.clear_message_widget()
                if stop_event.is_set():
                    break

            #
            if len(correct_positions) == 2:
                print("block is correct.")

                sleep(0.05)
                instance.add_message_to_widget("Переключатель полностью годен.")
                sleep(0.05)
                instance.add_message_to_widget('\nНажмите пробел для продолжения тестирования...')
                read_data(stop_event)
                instance.clear_message_widget()

            else:
                print("Переключатель негоден. Некорректные положения:")
                sleep(0.05)
                instance.add_message_to_widget("\nПереключатель негоден. Некорректные положения:")
                for position in range(1, 3):
                    if position in incorrect_positions:
                        print(f"Положение {position}")
                        instance.add_message_to_widget(f"Положение {position}")
                sleep(0.05)
                instance.add_message_to_widget('\nНажмите пробел для продолжения тестирования...')
                read_data(stop_event)
                sleep(0.05)
                instance.clear_message_widget()
            break
    ser.close()
    instance.add_message_to_widget('Порт закрыт, тестирование завершено')

