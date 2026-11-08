import requests
import threading
from datetime import datetime, timedelta
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window

API_URL = "https://v3.football.api-sports.io"

class FootballAI(App):
    def build(self):
        Window.clearcolor = (0.04, 0.07, 0.12, 1)

        root = BoxLayout(orientation="vertical", padding=12, spacing=10)

        title = Label(
            text="[b]FOOTBALL AI PRO[/b]",
            markup=True, font_size="25sp",
            size_hint_y=None, height=55
        )
        root.add_widget(title)

        self.api_key = TextInput(
            hint_text="API-Football kalitini kiriting",
            password=True, multiline=False,
            size_hint_y=None, height=50
        )
        root.add_widget(self.api_key)

        buttons = BoxLayout(size_hint_y=None, height=50, spacing=8)

        today = Button(text="BUGUN")
        tomorrow = Button(text="ERTAGA")

        today.bind(on_press=lambda x: self.load_matches(0))
        tomorrow.bind(on_press=lambda x: self.load_matches(1))

        buttons.add_widget(today)
        buttons.add_widget(tomorrow)
        root.add_widget(buttons)

        self.status = Label(
            text="Futbol uchrashuvlarini yuklash uchun kunni tanlang.",
            size_hint_y=None, height=55
        )
        root.add_widget(self.status)

        scroll = ScrollView()
        self.results = BoxLayout(
            orientation="vertical",
            size_hint_y=None, spacing=8
        )
        self.results.bind(minimum_height=self.results.setter("height"))
        scroll.add_widget(self.results)
        root.add_widget(scroll)

        return root

    def load_matches(self, offset):
        key = self.api_key.text.strip()

        if not key:
            self.status.text = "Avval API kalitini kiriting!"
            return

        date = (datetime.now() + timedelta(days=offset)).strftime("%Y-%m-%d")
        self.status.text = "Uchrashuvlar yuklanmoqda..."
        self.results.clear_widgets()

        threading.Thread(
            target=self.fetch_matches,
            args=(key, date),
            daemon=True
        ).start()

    def fetch_matches(self, key, date):
        try:
            response = requests.get(
                API_URL + "/fixtures",
                headers={"x-apisports-key": key},
                params={"date": date, "timezone": "Asia/Tashkent"},
                timeout=25
            )
            response.raise_for_status()
            data = response.json()

            if data.get("errors"):
                raise ValueError(str(data["errors"]))

            matches = data.get("response", [])

            Clock.schedule_once(
                lambda dt: self.show_matches(matches, date)
            )

        except Exception as e:
            message = str(e)
            Clock.schedule_once(
                lambda dt: self.show_error(message)
            )

    def show_matches(self, matches, date):
        self.status.text = f"{date}: {len(matches)} ta uchrashuv topildi."

        if not matches:
            self.results.add_widget(
                Label(
                    text="Bu sanada uchrashuv topilmadi.",
                    size_hint_y=None, height=60
                )
            )
            return

        for match in matches:
            league = match["league"]["name"]
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            goals = match["goals"]
            status = match["fixture"]["status"]["short"]
            time = match["fixture"]["date"][11:16]

            if goals["home"] is None:
                score = "VS"
            else:
                score = f'{goals["home"]} : {goals["away"]}'

            text = (
                f"[b]{home}  {score}  {away}[/b]\n"
                f"{league} | {time} | {status}"
            )

            card = Label(
                text=text, markup=True,
                size_hint_y=None, height=85,
                halign="center", valign="middle"
            )
            card.bind(size=lambda obj, size: setattr(
                obj, "text_size", (size[0] - 10, None)
            ))
            self.results.add_widget(card)

    def show_error(self, error):
        self.status.text = "Xatolik: " + error[:250]

FootballAI().run()
