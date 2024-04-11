import datetime
import tomlkit
import customtkinter as CTk
from pygame import mixer
from pathlib import Path


class ChimePlayer:
    """A class to play chimes at set intervals using a simple GUI."""


    def __init__(self, root) -> None:
        """Initialize the GUI components."""
        self.root = root

        CTk.set_appearance_mode("dark")
        CTk.set_default_color_theme("dark-blue")

        root.resizable(False, False)
        root.title("Chime Player")

        mixer.init()

        self.title_frame = CTk.CTkFrame(root, corner_radius=10, fg_color="#0079E1")
        self.title_frame.bind('<Button-1>', self.play_chime)
        self.title_frame.pack(pady=(10, 8))

        self.title_label = CTk.CTkLabel(
            self.title_frame,
            text="TickTockTone",
            font=CTk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color="#002849",
        )
        self.title_label.bind('<Button-1>', self.play_chime)
        self.title_label.pack(padx=9, pady=(2, 1))

        self.intervals = self.load_config("config.toml")

        self._create_interval_dropdown()
        self._create_chime_dropdown()

        self.status_label = CTk.CTkLabel(root, text="Click to start chiming:",
                                         font=CTk.CTkFont(family="Helvetica", size=14))
        self.status_label.pack()

        self.toggle_btn = CTk.CTkButton(
            root,
            text="Start",
            font=CTk.CTkFont(family="Helvetica", size=14),
            command=self.toggle_chiming,
            fg_color="#4CAF50",
        )
        self.toggle_btn.pack(padx=10, pady=(2, 10))

        self.running = False
        self.update_job = None

    def _create_interval_dropdown(self) -> None:
        """Create the dropdown menu for selecting chime intervals."""
        interval_label = CTk.CTkLabel(root, text="Set chime interval:",
                                      font=CTk.CTkFont(family="Helvetica", size=14))
        interval_label.pack()

        interval_options = list(self.intervals.keys())
        if not interval_options:
            interval_options = ["Every hour"]
            self.intervals = {"Every hour": 60}

        self.dropdown_interval = CTk.CTkComboBox(root, values=interval_options)
        self.dropdown_interval.set(interval_options[0])  # Set default option
        self.dropdown_interval.pack(pady=(2, 8))

    def _create_chime_dropdown(self) -> None:
        """Create the dropdown menu for selecting chime sounds."""
        chime_label = CTk.CTkLabel(root, text="Select chime sound:",
                                   font=CTk.CTkFont(family="Helvetica", size=14))
        chime_label.pack()

        chime_files = self.get_chime_files()
        self.dropdown_chime = CTk.CTkComboBox(root, values=chime_files)
        if chime_files:
            self.dropdown_chime.set(chime_files[0])  # Set default chime file if available
        self.dropdown_chime.pack(pady=(2, 8))

    def get_chime_files(self) -> list[str]:
        """Scan the current directory for MP3 chime sound files."""
        path = Path(__file__).parent
        return [file.name for file in path.glob("*.mp3")]

    def play_chime(self, event=None) -> None:
        """Play the selected chime sound."""
        chime_file = self.dropdown_chime.get()
        try:
            mixer.music.load(Path(__file__).parent / chime_file)
            mixer.music.play()
        except Exception as e:
            print(f"Error playing chime: {e}")

    def toggle_chiming(self) -> None:
        """Toggle the chiming process on and off."""
        if self.running:
            self.running = False
            self.toggle_btn.configure(text="Start", fg_color="#2E8B57", hover_color="#1d5737")
            self.status_label.configure(text="Chime stopped.")
            if self.update_job:
                self.root.after_cancel(self.update_job)
                self.update_job = None
        else:
            self.running = True
            self.toggle_btn.configure(text="Stop", fg_color="#cc0000", hover_color="#a50000")
            next_chime_time = self.get_next_chime_time()
            self.update_status(next_chime_time)

    def update_status(self, next_chime_time) -> None:
        """Update the status label with the time until the next chime."""
        if not self.running:
            return
        now = datetime.datetime.now()
        if now < next_chime_time:
            delta = next_chime_time - now
            minutes, seconds = divmod(delta.seconds, 60)
            self.status_label.configure(text=f"Chime in: {minutes}m {seconds}s")
            self.update_job = self.root.after(1000, self.update_status, next_chime_time)
        else:
            self.play_chime()
            if self.running:
                next_chime_time = self.get_next_chime_time()
                self.update_status(next_chime_time)

    def load_config(self, config_name) -> dict[str, int]:
        """Load chime intervals from a TOML configuration file."""
        config_path = Path(__file__).parent / config_name
        try:
            config_data = config_path.read_text()
            config = tomlkit.parse(config_data)
            intervals = config["intervals"]

            # Sort intervals with longer durations first (optional)
            sorted_intervals = {k.replace("_", " "): v for k, v in sorted(intervals.items(),
                                                                          key=lambda item: item[1],
                                                                          reverse=True)}
            return sorted_intervals
        except FileNotFoundError:
            print(f"Config file not found at {config_path}. Using default intervals.")
            return {"Every hour": 60}
        except (tomlkit.exceptions.TOMLKitError, KeyError) as e:
            print(f"Error parsing the config file: {e}")
            return {"Every hour": 60}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"Every hour": 60}

    def get_next_chime_time(self) -> datetime.datetime:
        """Calculate the next chime time based on the selected interval."""
        interval_minutes = self.intervals[self.dropdown_interval.get()]
        now = datetime.datetime.now()
        # Ensure next chime occurs on a whole minute boundary
        next_chime_time = (now + datetime.timedelta(minutes=interval_minutes)).replace(second=0, microsecond=0)
        return next_chime_time

if __name__ == "__main__":
    root = CTk.CTk()
    app = ChimePlayer(root)
    root.mainloop()