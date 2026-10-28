import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from spotify_client import NoActiveDeviceError, SpotifyController

POLL_INTERVAL_SECONDS = 3


class RootLayout(BoxLayout):
    # Builds the initial UI: a status label and a single "Connect" button.
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=12, **kwargs)
        self.controller = None

        self.status_label = Label(text="Not connected", font_size=20, size_hint_y=0.3)
        self.add_widget(self.status_label)

        self.connect_button = Button(text="Connect to Spotify", size_hint_y=0.2)
        self.connect_button.bind(on_release=lambda _: self.connect())
        self.add_widget(self.connect_button)

        self.controls = BoxLayout(spacing=10, size_hint_y=0.3)
        self.previous_button = self._make_control_button("Previous", self.on_previous)
        self.play_pause_button = self._make_control_button("Play/Pause", self.on_play_pause)
        self.next_button = self._make_control_button("Next", self.on_next)
        self.controls.add_widget(self.previous_button)
        self.controls.add_widget(self.play_pause_button)
        self.controls.add_widget(self.next_button)
        self._set_controls_enabled(False)

        self.poll_event = None

    # Creates a single control button, initially disabled until connected.
    def _make_control_button(self, text, handler):
        button = Button(text=text)
        button.bind(on_release=lambda _: handler())
        return button

    # Enables or disables the playback control buttons.
    def _set_controls_enabled(self, enabled):
        for button in (self.previous_button, self.play_pause_button, self.next_button):
            button.disabled = not enabled

    # Kicks off Spotify authentication on a background thread so the UI doesn't freeze.
    def connect(self):
        self.status_label.text = "Connecting... (check your browser)"
        self.connect_button.disabled = True
        threading.Thread(target=self._connect_worker, daemon=True).start()

    # Runs the blocking OAuth flow, then starts the target playlist and polling.
    def _connect_worker(self):
        try:
            controller = SpotifyController()
            controller.start_playlist()
        except NoActiveDeviceError as error:
            message = str(error)
            Clock.schedule_once(lambda _dt: self._on_connect_failed(message))
            return
        except Exception as error:  # noqa: BLE001 - surface any auth/API error to the UI
            message = str(error)
            Clock.schedule_once(lambda _dt: self._on_connect_failed(message))
            return
        Clock.schedule_once(lambda _dt: self._on_connected(controller))

    # Updates the UI once connected and starts periodic now-playing polling.
    def _on_connected(self, controller):
        self.controller = controller
        self.add_widget(self.controls)
        self._set_controls_enabled(True)
        self.remove_widget(self.connect_button)
        self.status_label.text = "Connected"
        self.poll_event = Clock.schedule_interval(lambda _dt: self.refresh_now_playing(), POLL_INTERVAL_SECONDS)

    # Re-enables the connect button and shows the error if connecting failed.
    def _on_connect_failed(self, message):
        self.status_label.text = f"Connection failed: {message}"
        self.connect_button.disabled = False

    # Fetches now-playing info on a background thread to avoid blocking the UI.
    def refresh_now_playing(self):
        threading.Thread(target=self._refresh_worker, daemon=True).start()

    # Performs the blocking now-playing API call, then hands the result to the UI thread.
    def _refresh_worker(self):
        try:
            playback = self.controller.get_current_playback()
        except Exception:  # noqa: BLE001 - a transient poll failure shouldn't crash the app
            return
        Clock.schedule_once(lambda _dt: self._update_status_label(playback))

    # Renders the now-playing dict onto the status label.
    def _update_status_label(self, playback):
        if playback is None:
            self.status_label.text = "Nothing playing"
            return
        state = "Playing" if playback["is_playing"] else "Paused"
        outside_note = "" if playback["in_target_playlist"] else " (outside target playlist)"
        self.status_label.text = f"{state}: {playback['track_name']} - {playback['artist_name']}{outside_note}"

    # Toggles between play and pause based on the last known state.
    def on_play_pause(self):
        def worker():
            playback = self.controller.get_current_playback()
            if playback and playback["is_playing"]:
                self.controller.pause()
            else:
                self.controller.play()
            Clock.schedule_once(lambda _dt: self.refresh_now_playing())

        threading.Thread(target=worker, daemon=True).start()

    # Skips to the next track.
    def on_next(self):
        threading.Thread(target=self.controller.next_track, daemon=True).start()

    # Goes back to the previous track.
    def on_previous(self):
        threading.Thread(target=self.controller.previous_track, daemon=True).start()


class SpotifySimplifiedApp(App):
    # Builds and returns the root widget for the app.
    def build(self):
        return RootLayout()


if __name__ == "__main__":
    SpotifySimplifiedApp().run()
