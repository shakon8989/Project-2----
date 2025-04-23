import speech_recognition as sr
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import threading

# Ключевые слова и соответствующие GIF анимации жестов
sign_language_gifs = {
    "сәлем": "surdosigns/salem.gif",
    "математика": "surdosigns/matematika.gif",
    "қош бол": "surdosigns/sau_bol.gif",
    "рақмет": "surdosigns/rahmet.gif",
    "жоқ": "surdosigns/jok.gif",
    "иә": "surdosigns/ia.gif",
    "су": "surdosigns/su.gif",
    "тамак": "surdosigns/tamaq.gif",
    "дұрыс": "surdosigns/durys.gif",
    "кешіріңіз": "surdosigns/kesiriniz.gif",
    "жұмыс": "surdosigns/zhumys.gif",
    "үй": "surdosigns/uy.gif",
    "пошта": "surdosigns/poshta.gif"
}

# Класс для отображения анимации GIF
class AnimatedGIF(tk.Label):
    def __init__(self, master, gif_path):
        super().__init__(master)
        self.gif_path = gif_path
        self.playing = True
        self.frames = []
        self.load_gif()
        self.after(self.delay, self.play)

    def load_gif(self):
        im = Image.open(self.gif_path)
        try:
            while True:
                self.frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(len(self.frames))
        except EOFError:
            pass
        self.delay = im.info.get('duration', 100)
        self.idx = 0
        self.config(image=self.frames[0])

    def play(self):
        if not self.playing:
            return
        self.config(image=self.frames[self.idx])
        self.idx = (self.idx + 1) % len(self.frames)
        self.after(self.delay, self.play)

    def stop(self):
        self.playing = False

# Функция для распознавания речи и отображения жестов
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        status_label.config(text="Тыңдап жатыр...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language="kk-KZ").lower()
            status_label.config(text=f"Танылған: {text}")
            for word in sign_language_gifs:
                if word in text:
                    show_sign(word)
                    break
        except:
            status_label.config(text="Тануға келмеді.")

# Функция для отображения GIF анимации жеста
def show_sign(word):
    clear_sign_frame()
    gif_path = sign_language_gifs.get(word)
    if gif_path:
        gif_player = AnimatedGIF(sign_frame, gif_path)
        gif_player.pack()
        refresh_btn.pack(pady=10)

# Удаление текущего GIF и кнопки "Жаңарту"
def clear_sign_frame():
    for widget in sign_frame.winfo_children():
        if isinstance(widget, AnimatedGIF):
            widget.stop()
        widget.destroy()
    refresh_btn.pack_forget()

# Обновить интерфейс
def refresh_interface():
    clear_sign_frame()
    status_label.config(text="Бастау үшін 'Тыңдау' батырмасын басыңыз")

# --- GUI интерфейс ---
root = tk.Tk()
root.title("AI-СурдоКамера (Прототип)")
root.geometry("1280x800")

# Шрифт побольше для высокого разрешения
status_label = tk.Label(root, text="Бастау үшін 'Тыңдау' батырмасын басыңыз", font=("Arial", 16))
status_label.pack(pady=20)

# Контейнер для GIF
sign_frame = tk.Frame(root, width=1000, height=500)
sign_frame.pack(pady=30)

# Кнопка "Тыңдау"
btn = tk.Button(root, text="🎤 Тыңдау", font=("Arial", 16),
                width=20, height=2,
                command=lambda: threading.Thread(target=recognize_speech).start())
btn.pack(pady=10)

# Кнопка "Жаңарту"
refresh_btn = tk.Button(root, text="🔁 Жаңарту", font=("Arial", 14),
                        width=20, height=2,
                        command=refresh_interface)

root.mainloop()
