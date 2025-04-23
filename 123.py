
import serial
import os
import time
import pyautogui
import requests



from datetime import datetime

# Настройки последовательного порта
SERIAL_PORT = 'COM8'  # Замените на ваш COM-порт
BAUD_RATE = 9600


# Телеграм API токен и ID чата
TELEGRAM_BOT_TOKEN = '8007369046:AAFFb6TrYqSJVvca2GjWgPVCiinPX8YpEuQ'  # Ваш токен
CHAT_ID = '2039883178'  # Ваш ID чата



# Папка для сохранения видео
VIDEO_FOLDER = r"D:\eltai\Pictures\Camera Roll"  # Путь к папке для сохранения видео

# Флаг состояния камеры
is_camera_open = False

def send_message_to_telegram(message):
    """Отправка текстового сообщения в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        print(f"Сообщение отправлено: {message}")
    else:
        print(f"Ошибка отправки сообщения: {response.status_code}")

def send_video_to_telegram(video_path):
    """Отправка видео в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(video_path, 'rb') as video_file:
        payload = {'chat_id': CHAT_ID}
        files = {'video': video_file}
        response = requests.post(url, data=payload, files=files)
    
    if response.status_code == 200:
        print(f"Видео отправлено в Telegram.")
    else:
        print(f"Ошибка отправки видео: {response.status_code}")

def open_camera():
    """Открывает приложение 'Камера'."""
    global is_camera_open
    if not is_camera_open:
        print("Открываю приложение 'Камера'...")
        os.system("start microsoft.windows.camera:")  # Запуск камеры на Windows
        time.sleep(5)  # Подождём, пока откроется камера
        is_camera_open = True
    else:
        print("Камера уже открыта.")

def close_camera():
    """Закрывает приложение 'Камера'."""
    global is_camera_open
    if is_camera_open:
        print("Закрываю приложение 'Камера'...")
        pyautogui.hotkey('alt', 'f4')  # Закрываем окно через Alt+F4
        is_camera_open = False

def start_recording():
    """Запуск записи видео."""
    # Нажимаем Enter для начала записи
    pyautogui.press('enter')
    print("Запись видео начата.")
    time.sleep(12)  # Запись длится 5 секунд
    # Нажимаем Enter для остановки записи
    pyautogui.press('enter')
    print("Запись завершена.")

def wait_for_new_video(initial_files):
    """Ожидание появления нового файла в папке."""
    while True:
        current_files = set(os.listdir(VIDEO_FOLDER))
        new_files = current_files - initial_files
        for new_file in new_files:
            if new_file.endswith('.mp4'):  # Проверяем, является ли файл видео
                return os.path.join(VIDEO_FOLDER, new_file)
        time.sleep(1)  # Проверяем каждые 1 секунду

def main():
    global is_camera_open
    try:
        # Подключение к последовательному порту
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("Ожидание сигналов от Arduino...")

        while True:
            # Чтение данных из порта
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                print(f"Получено: {data}")

                if data == "MOTION_DETECTED":
                    send_message_to_telegram("Обнаружено движение! Начинаю запись...")  # Отправляем сообщение в Telegram
                    
                    # Получаем список файлов перед началом записи
                    initial_files = set(os.listdir(VIDEO_FOLDER))
                    
                    open_camera()  # Включаем камеру
                    time.sleep(2)  # Даем камере время на открытие

                    start_recording()  # Включаем запись

                    # Ждем появления нового файла
                    print("Ждем появления нового видеофайла...")
                    video_path = wait_for_new_video(initial_files)

                    if os.path.exists(video_path):
                        send_message_to_telegram("Запись завершена, отправляю видео.")  # Отправляем сообщение о завершении записи
                        send_video_to_telegram(video_path)  # Отправляем видео в Telegram
                    else:
                        send_message_to_telegram("Ошибка: видео файл не найден.")  # Сообщаем об ошибке

                    close_camera()  # Закрываем камеру

    except serial.SerialException as e:
        print(f"Ошибка работы с последовательным портом: {e}")
    except KeyboardInterrupt:
        print("Выход из программы.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
