from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

if TYPE_CHECKING:
    from tsumemi.src.tsumemi.run_statistics import RunStatistics


class StatsScreen(Screen):
    """Post-run statistics summary."""

    def __init__(
        self,
        on_done: Callable[[], None],
        **kwargs: object,
    ) -> None:
        super().__init__(name="stats", **kwargs)
        self.on_done = on_done
        self._stats: RunStatistics | None = None
        root = BoxLayout(orientation="vertical", padding=16, spacing=8)
        self.summary = Label(text="", halign="left", valign="top")
        root.add_widget(self.summary)
        done_btn = Button(text="Back to import", size_hint_y=0.12)
        done_btn.bind(on_release=lambda _x: on_done())
        root.add_widget(done_btn)
        self.add_widget(root)

    def show_stats(self, stats: RunStatistics) -> None:
        self._stats = stats
        slow = stats.slowest_problem.name if stats.slowest_problem else "—"
        fast = stats.fastest_problem.name if stats.fastest_problem else "—"
        self.summary.text = (
            f"Run complete\n\n"
            f"Problems: {stats.total_problems}\n"
            f"Correct: {stats.total_correct}\n"
            f"Wrong: {stats.total_wrong}\n"
            f"Skipped: {stats.total_skipped}\n"
            f"Total time: {stats.total_time}\n"
            f"Avg per seen: {stats.average_time_per_problem}\n"
            f"Fastest: {fast}\n"
            f"Slowest: {slow}"
        )
