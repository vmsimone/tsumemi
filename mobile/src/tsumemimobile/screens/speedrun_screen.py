from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from tsumemimobile.board_widget import MobileBoardWidget

if TYPE_CHECKING:
    from tsumemi.src.tsumemi.run_statistics import RunStatistics
    from tsumemimobile.session import MobileSession


class SpeedrunScreen(Screen):
    """Timed speedrun: board, timer, skip/solution controls."""

    def __init__(
        self,
        session: MobileSession,
        on_finished: Callable[[RunStatistics], None],
        **kwargs: object,
    ) -> None:
        super().__init__(name="speedrun", **kwargs)
        self.session = session
        self.on_finished = on_finished
        self._timer_event = None
        root = BoxLayout(orientation="vertical", padding=4, spacing=4)
        header = BoxLayout(size_hint_y=0.08, spacing=4)
        self.problem_label = Label(text="", halign="left", valign="middle")
        self.timer_label = Label(text="00:00:00.0", halign="right")
        header.add_widget(self.problem_label)
        header.add_widget(self.timer_label)
        root.add_widget(header)
        self.board = MobileBoardWidget(size_hint_y=0.72)
        root.add_widget(self.board)
        self.controls = BoxLayout(size_hint_y=0.12, spacing=4)
        root.add_widget(self.controls)
        self.feedback = Label(text="", size_hint_y=0.08, halign="center")
        root.add_widget(self.feedback)
        self.add_widget(root)
        self.session.attach_board(self.board)
        self.session.on_problem_loaded = self._update_header
        self.session.on_speedrun_finished = self._finish
        self.session.speedrun.on_state_changed = self._on_state_changed

    def on_enter(self, *_args: object) -> None:
        if not self.session.start_speedrun():
            self.feedback.text = "No problems loaded"
            return
        self._start_timer_display()
        self._update_header()
        self._on_state_changed("question")

    def on_leave(self, *_args: object) -> None:
        self._stop_timer_display()

    def _start_timer_display(self) -> None:
        self._stop_timer_display()
        self._timer_event = Clock.schedule_interval(lambda _dt: self._tick_timer(), 0.1)

    def _stop_timer_display(self) -> None:
        if self._timer_event is not None:
            Clock.unschedule(self._timer_event)
            self._timer_event = None

    def _tick_timer(self) -> None:
        self.timer_label.text = str(self.session.timer.read())

    def _update_header(self) -> None:
        idx = self.session.problem_list.curr_prob_idx
        total = len(self.session.problem_list)
        prob = self.session.problem_list.curr_prob
        name = prob.name if prob else "?"
        self.problem_label.text = f"{(idx or 0) + 1}/{total}  {name}"

    def _on_state_changed(self, state: str) -> None:
        self.controls.clear_widgets()
        sr = self.session.speedrun
        if state == "question":
            self.feedback.text = "Solve the problem"
            self.session.hide_solution()
            solving = sr._speedrun_states["question"]
            self.controls.add_widget(
                Button(text="Show solution", on_release=lambda _x: solving.show_answer())
            )
            self.controls.add_widget(
                Button(text="Skip", on_release=lambda _x: solving.skip())
            )
        elif state == "answer":
            self.feedback.text = "Mark your attempt"
            answer = sr._speedrun_states["answer"]
            self.controls.add_widget(
                Button(
                    text="Correct",
                    on_release=lambda _x: answer.mark_correct_and_continue(),
                )
            )
            self.controls.add_widget(
                Button(
                    text="Wrong",
                    on_release=lambda _x: answer.mark_wrong_and_continue(),
                )
            )
        elif state == "solution":
            prob = self.session.problem_list.curr_prob
            status = prob.status.name if prob else ""
            self.feedback.text = f"Result: {status}"
            solution = sr._speedrun_states["solution"]
            if not self.session.auto_next:
                self.controls.add_widget(
                    Button(
                        text="Next",
                        on_release=lambda _x: solution.next_question(),
                    )
                )

    def _finish(self, stats: RunStatistics) -> None:
        self._stop_timer_display()
        self.on_finished(stats)
