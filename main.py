from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.popup import Popup

from plyer import notification

import threading
import time
from datetime import datetime


# Удаляем фиксированный размер окна, чтобы оно было адаптивным
# Window.size = (400, 300)  # Удалите или закомментируйте эту строку


class ReminderApp(App):
    def build(self):
        self.title = "Напоминания"
        self.reminders = []

        # Основной ScrollView для прокрутки содержимого при необходимости
        scroll_view = ScrollView(size_hint=(1, 1))

        # Внутренний контейнер - BoxLayout с вертикальной ориентацией
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))

        # Заголовок
        header = Label(text='Создайте напоминание', font_size=24, size_hint_y=None, height=50)
        main_layout.add_widget(header)

        # Поле для названия напоминания
        self.name_input = TextInput(hint_text='Название напоминания', multiline=False, size_hint_y=None, height=40)
        main_layout.add_widget(self.name_input)

        # Поле для даты (ГГГГ-ММ-ДД)
        date_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        date_label = Label(text='Дата (ГГГГ-ММ-ДД):', size_hint_x=None, width=150)
        self.date_input = TextInput(hint_text='2024-12-31', multiline=False)
        date_layout.add_widget(date_label)
        date_layout.add_widget(self.date_input)
        main_layout.add_widget(date_layout)

        # Поле для времени (ЧЧ:ММ)
        time_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        time_label = Label(text='Время (ЧЧ:ММ):', size_hint_x=None, width=150)
        self.time_input = TextInput(hint_text='14:30', multiline=False)
        time_layout.add_widget(time_label)
        time_layout.add_widget(self.time_input)
        main_layout.add_widget(time_layout)

        # Кнопка добавления напоминания
        add_btn = Button(
            text='Добавить напоминание',
            size_hint_y=None,
            height=50,
            background_color=(0.3, 0.6, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        add_btn.bind(on_press=self.add_reminder)
        main_layout.add_widget(add_btn)

        scroll_view.add_widget(main_layout)

        # Запускаем фоновую проверку напоминаний в отдельном потоке
        threading.Thread(target=self.check_reminders_loop, daemon=True).start()

        return scroll_view

    def add_reminder(self, instance):
        name = self.name_input.text.strip()
        date_str = self.date_input.text.strip()
        time_str = self.time_input.text.strip()

        if not name or not date_str or not time_str:
            self.show_popup("Ошибка", "Пожалуйста, заполните все поля.")
            return

        try:
            date_part = datetime.strptime(date_str, '%Y-%m-%d')
            time_part = datetime.strptime(time_str, '%H:%M')
            reminder_dt = datetime(
                year=date_part.year,
                month=date_part.month,
                day=date_part.day,
                hour=time_part.hour,
                minute=time_part.minute
            )
            now_dt = datetime.now()

            # Проверка: нельзя ставить напоминание на прошедшую дату/время
            if reminder_dt <= now_dt:
                self.show_popup("Ошибка", "Указанная дата и время уже прошли.")
                return

            # Добавляем напоминание в список
            self.reminders.append({'name': name, 'datetime': reminder_dt})

            # Очистка полей ввода после добавления
            self.name_input.text = ''
            self.date_input.text = ''
            self.time_input.text = ''

        except ValueError:
            self.show_popup("Ошибка", "Некорректный формат. Используйте:\nДата: ГГГГ-ММ-ДД\nВремя: ЧЧ:ММ.")

    def check_reminders_loop(self):
        while True:
            now = datetime.now()
            for rem in self.reminders[:]:
                rem_time = rem['datetime']
                delta_seconds = (rem_time - now).total_seconds()
                if 0 <= delta_seconds < 1:
                    # Время для уведомления достигнуто
                    notification.notify(
                        title='Напоминание',
                        message=rem['name'],
                        timeout=10
                    )
                    # Удаляем напоминание после уведомления
                    self.reminders.remove(rem)
            time.sleep(1)  # Проверять каждую секунду

    def show_popup(self, title, message):
        popup_content = BoxLayout(orientation='vertical', padding=10)

        _label = Label(text=message)

        _btn_close = Button(text='ОК', size_hint_y=None, height=40)

        def close_popup(instance):
            popup.dismiss()

        _btn_close.bind(on_press=close_popup)

        popup_content.add_widget(_label)
        popup_content.add_widget(_btn_close)

        popup = Popup(title=title,
                      content=popup_content,
                      size_hint=(0.8, 0.4))

        popup.open()


if __name__ == '__main__':
    ReminderApp().run()
