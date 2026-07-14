from __future__ import annotations

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from tsumemimobile.screens import ImportScreen, SpeedrunScreen, StatsScreen
from tsumemimobile.session import MobileSession


class TsumemiMobileApp(App):
    def build(self) -> ScreenManager:
        self.title = "Tsumemi"
        self.session = MobileSession(self)
        sm = ScreenManager()
        stats = StatsScreen(on_done=lambda: setattr(sm, "current", "import"))
        speedrun = SpeedrunScreen(
            self.session,
            on_finished=lambda s: (stats.show_stats(s), setattr(sm, "current", "stats")),
        )
        import_screen = ImportScreen(
            self.session,
            on_ready=lambda: setattr(sm, "current", "speedrun"),
        )
        sm.add_widget(import_screen)
        sm.add_widget(speedrun)
        sm.add_widget(stats)
        return sm


def main() -> None:
    TsumemiMobileApp().run()
