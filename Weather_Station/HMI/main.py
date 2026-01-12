import tkinter as tk
from datetime import datetime

import config
import weather

class HMI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.configure(bg="black")
        self.attributes("-fullscreen", True)

        self.time_label = tk.Label(
            self,
            font=("Helvetica", 80),
            fg="white",
            bg="black"
        )
        self.time_label.pack(pady=40)

        self.weather_label = tk.Label(
            self,
            font=("Helvetica", 40),
            fg="white",
            bg="black"
        )
        self.weather_label.pack()

        self.update_time()
        self.update_weather()

        # ESC to exit during development
        self.bind("<Escape>", lambda e: self.destroy())

    def update_time(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=now)
        self.after(config.TIME_REFRESH_MS, self.update_time)

    def update_weather(self):
        temp = weather.get_current_temperature(
            config.LATITUDE,
            config.LONGITUDE
        )

        if temp is None:
            self.weather_label.config(text="Weather unavailable")
        else:
            self.weather_label.config(text=f"{temp:.1f} °C")

        self.after(config.WEATHER_REFRESH_MS, self.update_weather)

if __name__ == "__main__":
    app = HMI()
    app.mainloop()
