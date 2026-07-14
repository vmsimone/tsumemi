from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import tsumemi.src.tsumemi.event as evt
import tsumemi.src.tsumemi.game.game_controller as gamecon
import tsumemi.src.tsumemi.problem as pb
from tsumemi.src.tsumemi.speedrun_states import (
    NotInSpeedrun,
    ReviewAnswer,
    Solving,
    SolutionShown,
    SpeedrunState,
)

if TYPE_CHECKING:
    from tsumemimobile.session import MobileSession


class MobileSpeedrunController(evt.IObserver):
    """Speedrun state machine without tkinter dependencies."""

    def __init__(self, session: MobileSession) -> None:
        evt.IObserver.__init__(self)
        self.session = session
        self._speedrun_states: dict[str, SpeedrunState] = {
            "answer": ReviewAnswer(controller=self),  # type: ignore[arg-type]
            "off": NotInSpeedrun(controller=self),  # type: ignore[arg-type]
            "question": Solving(controller=self),  # type: ignore[arg-type]
            "solution": SolutionShown(controller=self),  # type: ignore[arg-type]
        }
        self.current_speedrun_state = self._speedrun_states["off"]
        self.on_state_changed: Callable[[str], None] | None = None
        self.session.game.add_observer(self)
        self.add_callback(gamecon.GameEndEvent, self._on_correct_solve)
        self.add_callback(gamecon.WrongMoveEvent, self._on_wrong_solve)

    def on_notify(self, event: evt.Event) -> None:
        event_type = type(event)
        if event_type in self._notify_actions:
            self._notify_actions[event_type](event)

    def go_to_state(self, state: str) -> None:
        old_state = self.current_speedrun_state
        new_state = self._speedrun_states[state]
        old_state.on_exit()
        new_state.on_entry()
        self.current_speedrun_state = new_state
        if self.on_state_changed is not None:
            self.on_state_changed(state)

    def _on_correct_solve(self, _event: evt.Event) -> None:
        if isinstance(self.current_speedrun_state, Solving):
            self.mark_correct()
            self.go_to_state("solution")

    def _on_wrong_solve(self, _event: evt.Event) -> None:
        if isinstance(self.current_speedrun_state, Solving):
            self.mark_wrong()
            self.go_to_state("solution")

    def start_speedrun(self) -> None:
        self.session.problem_list.go_to_idx(0)
        self.session.load_current_problem()
        self.session.game.set_speedrun_mode()
        self.session.timer.reset()
        self.start_timer()
        self.go_to_state("question")

    def abort_speedrun(self) -> None:
        self.stop_timer()
        self.session.game.set_free_mode()
        self.enable_solving()
        self.go_to_state("off")

    def go_next_question(self) -> bool:
        next_problem = self.session.problem_list.go_to_next()
        if next_problem is None:
            self.stop_timer()
            self.session.on_speedrun_complete()
            self.abort_speedrun()
        else:
            self.session.load_current_problem()
        return next_problem is not None

    def auto_next_enabled(self) -> bool:
        return self.session.auto_next

    def schedule_auto_next(self, callback: Callable[[], None]) -> None:
        from kivy.clock import Clock

        Clock.schedule_once(lambda _dt: callback(), 0.4)

    def show_solution(self) -> None:
        self.session.show_solution()

    def start_timer(self) -> None:
        self.session.timer.start()

    def stop_timer(self) -> None:
        self.session.timer.stop()

    def split_timer(self) -> None:
        self.session.timer.split()

    def mark_correct(self) -> None:
        self.session.problem_list.set_status(pb.ProblemStatus.CORRECT)

    def mark_wrong(self) -> None:
        self.session.problem_list.set_status(pb.ProblemStatus.WRONG)

    def mark_skip(self) -> None:
        self.session.problem_list.set_status(pb.ProblemStatus.SKIP)

    def disable_solving(self) -> None:
        self.session.disable_move_input()

    def enable_solving(self) -> None:
        self.session.enable_move_input()

    def disable_move_navigation(self) -> None:
        self.session.disable_move_navigation()

    def enable_move_navigation(self) -> None:
        self.session.enable_move_navigation()
