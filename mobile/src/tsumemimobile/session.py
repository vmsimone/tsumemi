from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import tsumemi.src.tsumemi.event as evt
import tsumemi.src.tsumemi.event as evt
import tsumemi.src.tsumemi.game.game_controller as gamecon
import tsumemi.src.tsumemi.problem as pb
from tsumemi.src.shogi.basetypes import Side
from tsumemi.src.shogi.parsing import kif
from tsumemi.src.tsumemi.problem import Problem
from tsumemi.src.tsumemi.problem_list.problem_list_model import ProblemList
from tsumemi.src.tsumemi.run_statistics import RunStatistics
from tsumemi.src.tsumemi.timer import Timer, TimerSplitEvent

from tsumemimobile.game_session import MobileGameSession
from tsumemimobile.speedrun import MobileSpeedrunController
from tsumemimobile.storage.kifu_storage import kifu_library_dir, list_kifu_files

if TYPE_CHECKING:
    from pathlib import Path

    from tsumemimobile.board_widget import MobileBoardWidget


class MobileSession(evt.IObserver):
    """Orchestrates problem list, game, timer, and speedrun for mobile UI."""

    def __init__(self, app_paths: object) -> None:
        evt.IObserver.__init__(self)
        self.library_dir = kifu_library_dir(app_paths)
        self.problem_list = ProblemList()
        self.game = MobileGameSession()
        self.timer = Timer()
        self.speedrun = MobileSpeedrunController(self)
        self.auto_next = True
        self.directory_name = str(self.library_dir)
        self._board: MobileBoardWidget | None = None
        self._solution_visible = False
        self.on_problem_loaded: Callable[[], None] | None = None
        self.on_speedrun_finished: Callable[[RunStatistics], None] | None = None
        self.on_timer_tick: Callable[[], None] | None = None
        self.timer.add_observer(self)
        self.add_callback(TimerSplitEvent, self._record_split_time)

    def attach_board(self, board: MobileBoardWidget) -> None:
        self._board = board
        self.game.attach_board(board)

    def on_notify(self, event: evt.Event) -> None:
        event_type = type(event)
        if event_type in self._notify_actions:
            self._notify_actions[event_type](event)

    def reload_problem_list(self) -> int:
        paths = list_kifu_files(self.library_dir)
        self.problem_list.clear(suppress=True)
        self.problem_list.add_problems([Problem(p) for p in paths])
        self.problem_list.sort_by_file()
        return len(self.problem_list)

    def load_current_problem(self) -> bool:
        filepath = self.problem_list.get_curr_filepath()
        if filepath is None:
            return False
        game = kif.read_kif(filepath)
        if game is None:
            return False
        self._solution_visible = False
        self.game.set_game(game)
        self.game.go_to_start()
        if self._board is not None:
            self._board.set_play_as_side(game.position.turn)
            self._board.set_inverted(game.position.turn == Side.GOTE)
        if self.on_problem_loaded is not None:
            self.on_problem_loaded()
        return True

    def start_speedrun(self) -> bool:
        if self.problem_list.is_empty():
            return False
        self.problem_list.clear_statuses(suppress=True)
        self.problem_list.clear_times(suppress=True)
        self.speedrun.start_speedrun()
        return True

    def show_solution(self) -> None:
        self._solution_visible = True
        self.game.show_solution_line()

    def hide_solution(self) -> None:
        self._solution_visible = False
        self.game.go_to_start()

    def enable_move_input(self) -> None:
        self.game.enable_move_input()

    def disable_move_input(self) -> None:
        self.game.disable_move_input()

    def disable_move_navigation(self) -> None:
        pass

    def enable_move_navigation(self) -> None:
        pass

    def build_statistics(self) -> RunStatistics:
        return RunStatistics(self.problem_list, self.directory_name)

    def on_speedrun_complete(self) -> None:
        stats = self.build_statistics()
        if self.on_speedrun_finished is not None:
            self.on_speedrun_finished(stats)

    def _record_split_time(self, event: TimerSplitEvent) -> None:
        self.problem_list.set_time(event.time)
