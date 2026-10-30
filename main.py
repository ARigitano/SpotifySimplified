import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
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

        self.cover_image = AsyncImage(fit_mode="contain", size_hint_y=0.7)

        self.next_button = Button(text="Next", size_hint_y=0.3)
        self.next_button.bind(on_release=lambda _: self.on_next())

        self.poll_event = None

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

    # Swaps the status label for the cover art once connected and starts periodic now-playing polling.
    def _on_connected(self, controller):
        self.controller = controller
        self.remove_widget(self.status_label)
        self.remove_widget(self.connect_button)
        self.add_widget(self.cover_image)
        self.add_widget(self.next_button)
        self.refresh_now_playing()
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
        Clock.schedule_once(lambda _dt: self._update_cover(playback))

    # Shows the current track's cover art, or clears it if nothing is playing.
    def _update_cover(self, playback):
        cover_url = playback["cover_url"] if playback else None
        self.cover_image.source = cover_url or ""

    # Skips to the next track, then refreshes the cover right away instead of waiting for the next poll.
    def on_next(self):
        def worker():
            self.controller.next_track()
            Clock.schedule_once(lambda _dt: self.refresh_now_playing())

        threading.Thread(target=worker, daemon=True).start()


class SpotifySimplifiedApp(App):
    # Builds and returns the root widget for the app.
    def build(self):
        return RootLayout()


if __name__ == "__main__":
    SpotifySimplifiedApp().run()
