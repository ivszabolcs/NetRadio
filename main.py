import customtkinter as ctk
import vlc
import json
import os
import sys
from threading import Thread
from PIL import Image, ImageDraw
import pystray


SETTINGS_FILE = "settings.json"


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "stations": {
                "Heart90s": "https://media-ssl.musicradio.com/Heart90s",
                "Heart80s": "https://media-ice.musicradio.com/Heart80sMP3",
                "Heart70s": "https://media-ssl.musicradio.com/Heart70s",
                "Radio Swiss Pop": "http://stream.srg-ssr.ch/m/rsp/mp3_128",
            },
            "appearance_mode": "dark",
            "window_size": [450, 200],
            "last_station": None,
            "last_volume": 70
        }


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)


class RadioPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.settings = load_settings()

        ctk.set_appearance_mode(self.settings.get("appearance_mode", "dark"))
        ctk.set_default_color_theme("dark-blue")

        self.title("NetRadio")
        w, h = self.settings.get("window_size", [450, 200])
        self.geometry(f"{w}x{h}")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()

        # UI elemek
        self.station_selector = ctk.CTkComboBox(self, values=list(self.settings["stations"].keys()), font=("Arial", 14))
        self.station_selector.pack(pady=10)
        self.station_selector.set("Select station")

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=5)

        self.play_button = ctk.CTkButton(btn_frame, text="▶ Play", width=80, command=self.play_station)
        self.play_button.grid(row=0, column=0, padx=5)

        self.stop_button = ctk.CTkButton(btn_frame, text="⏹ Stop", width=80, command=self.stop)
        self.stop_button.grid(row=0, column=1, padx=5)

        self.volume_slider = ctk.CTkSlider(btn_frame, from_=0, to=100, width=150, command=self.set_volume)
        initial_volume = self.settings.get("last_volume", 70)
        self.volume_slider.set(initial_volume)
        self.volume_slider.grid(row=0, column=2, padx=5)

        self.meta_label = ctk.CTkLabel(self, text="Now Playing: ", font=("Arial", 14))
        self.meta_label.pack(pady=10)

        self.current_media = None
        self.player.audio_set_volume(initial_volume)

        last = self.settings.get("last_station")
        if last and last in self.settings["stations"]:
            self.station_selector.set(last)
            self.after(500, self.play_station)

        Thread(target=self.create_tray_icon, daemon=True).start()
        self.after(100, self.place_bottom_right)

    def place_bottom_right(self):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        win_width = self.winfo_width()
        win_height = self.winfo_height()
        x = screen_width - win_width - 20
        y = screen_height - win_height - 50
        self.geometry(f"+{x}+{y}")

    def play_station(self):
        selection = self.station_selector.get()
        if selection in self.settings["stations"]:
            url = self.settings["stations"][selection]
            media = self.vlc_instance.media_new(url)
            self.player.set_media(media)
            self.player.play()
            self.current_media = media
            self.update_metadata()

            self.settings["last_station"] = selection
            save_settings(self.settings)

    def update_metadata(self):
        if self.current_media:
            self.current_media.parse_with_options(vlc.MediaParseFlag.network, 0)
            title = self.current_media.get_meta(vlc.Meta.NowPlaying)
            if not title:
                title = self.current_media.get_meta(vlc.Meta.Title)

            # Nem releváns metaadat kiszűrése
            invalid_keywords = ["tdsdk", "banners", "pname", "pversion", "sbmid"]
            if title and any(keyword in title.lower() for keyword in invalid_keywords):
                title = None

            if title:
                self.meta_label.configure(text=f"Now Playing: {title}")
            else:
                # Ha nincs jó metaadat, akkor a rádió neve jelenik meg
                current_station = self.station_selector.get()
                self.meta_label.configure(text=f"Now Playing: {current_station}")

        self.after(3000, self.update_metadata)

    def set_volume(self, volume):
        vol = int(float(volume))
        self.player.audio_set_volume(vol)
        self.settings["last_volume"] = vol
        save_settings(self.settings)

    def stop(self):
        self.player.stop()
        self.meta_label.configure(text="Now Playing: ")
        self.current_media = None

    def on_close(self):
        self.withdraw()
        self.settings["window_size"] = [self.winfo_width(), self.winfo_height()]
        self.settings["last_volume"] = int(float(self.volume_slider.get()))
        save_settings(self.settings)

    def show_window(self):
        self.deiconify()
        self.place_bottom_right()

    def open_settings(self):
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
            self.settings_window.focus()
            return

        self.settings_window = ctk.CTkToplevel(self)
        self.settings_window.title("Options")
        self.settings_window.geometry("300x300")
        self.settings_window.transient(self)

        ctk.CTkLabel(self.settings_window, text="Theme:", font=("Arial", 14)).pack(pady=10)
        mode_combo = ctk.CTkComboBox(self.settings_window, values=["light", "dark"], font=("Arial", 14))
        mode_combo.set(self.settings.get("appearance_mode", "dark"))
        mode_combo.pack(pady=5)

        ctk.CTkLabel(self.settings_window, text="Window width:", font=("Arial", 14)).pack(pady=10)
        width_entry = ctk.CTkEntry(self.settings_window, font=("Arial", 14))
        width_entry.insert(0, str(self.settings.get("window_size", [450, 200])[0]))
        width_entry.pack()

        ctk.CTkLabel(self.settings_window, text="Window hight:", font=("Arial", 14)).pack(pady=10)
        height_entry = ctk.CTkEntry(self.settings_window, font=("Arial", 14))
        height_entry.insert(0, str(self.settings.get("window_size", [450, 200])[1]))
        height_entry.pack()

        def save_options():
            new_mode = mode_combo.get()
            try:
                new_width = int(width_entry.get())
                new_height = int(height_entry.get())
                if new_width < 100 or new_height < 100:
                    raise ValueError("Size too small")
            except Exception as e:
                ctk.CTkMessageBox.show_error(title="Error", message=f"Invalid size: {e}")
                return

            self.settings["appearance_mode"] = new_mode
            self.settings["window_size"] = [new_width, new_height]
            save_settings(self.settings)

            ctk.set_appearance_mode(new_mode)
            self.geometry(f"{new_width}x{new_height}")
            self.place_bottom_right()
            self.settings_window.destroy()

        save_btn = ctk.CTkButton(self.settings_window, text="Save", command=save_options)
        save_btn.pack(pady=15)

    def open_add_radio(self):
        if hasattr(self, 'add_radio_window') and self.add_radio_window.winfo_exists():
            self.add_radio_window.focus()
            return

        self.add_radio_window = ctk.CTkToplevel(self)
        self.add_radio_window.title("Add Radio")
        self.add_radio_window.geometry("300x230")
        self.add_radio_window.transient(self)

        ctk.CTkLabel(self.add_radio_window, text="Radio name:", font=("Arial", 14)).pack(pady=5)
        name_entry = ctk.CTkEntry(self.add_radio_window, font=("Arial", 14))
        name_entry.pack(pady=5)

        ctk.CTkLabel(self.add_radio_window, text="Stream URL:", font=("Arial", 14)).pack(pady=5)
        url_entry = ctk.CTkEntry(self.add_radio_window, font=("Arial", 14))
        url_entry.pack(pady=5)

        def add_radio():
            name = name_entry.get().strip()
            url = url_entry.get().strip()
            if not name or not url:
                ctk.CTkMessageBox.show_error(title="Error", message="Both fields are required!")
                return
            self.settings["stations"][name] = url
            save_settings(self.settings)

            self.station_selector.configure(values=list(self.settings["stations"].keys()))
            self.add_radio_window.destroy()

        add_btn = ctk.CTkButton(self.add_radio_window, text="Add", command=add_radio)
        add_btn.pack(pady=15)

    def create_tray_icon(self):
        def create_image():
            size = 64
            image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            dc = ImageDraw.Draw(image)
            margin = 8
            dc.ellipse((margin, margin, size - margin, size - margin), fill=(0, 122, 204, 255))
            return image

        def on_quit(icon, item):
            icon.visible = False
            self.player.stop()
            self.icon.stop()
            self.destroy()
            sys.exit()

        def on_show(icon, item):
            self.after(0, self.show_window)

        def on_options(icon, item):
            self.after(0, self.open_settings)

        def on_add_radio(icon, item):
            self.after(0, self.open_add_radio)

        def on_left_click(icon, item):
            self.after(0, self.show_window)

        menu = pystray.Menu(
            pystray.MenuItem("Open", on_show),
            pystray.MenuItem("Options", on_options),
            pystray.MenuItem("Add Radio", on_add_radio),
            pystray.MenuItem("Exit", on_quit)
        )

        self.icon = pystray.Icon("NetRadio", create_image(), "NetRadio", menu)
        self.icon.run_detached()


if __name__ == "__main__":
    app = RadioPlayer()
    app.mainloop()
