from __future__ import annotations

from typing import TYPE_CHECKING

import tsumemi.src.tsumemi.event as evt
import tsumemi.src.tsumemi.move_input_handler as mih

from tsumemi.src.shogi.game import Game
from tsumemi.src.shogi.move import TerminationMove
from tsumemi.src.tsumemi.game.game_controller import GameEndEvent, WrongMoveEvent
from tsumemi.src.tsumemi.game.game_model import GameModel, GameStepEvent, GameUpdateEvent

if TYPE_CHECKING:
    from tsumemimobile.board_widget import MobileBoardWidget


class MobileGameSession(evt.Emitter, evt.IObserver):
    """Game model + speedrun move verification, without tkinter."""

    def __init__(self) -> None:
        evt.Emitter.__init__(self)
        evt.IObserver.__init__(self)
        self.model = GameModel()
        self._board: MobileBoardWidget | None = None
        self._move_handler: mih.MoveInputHandler | None = None
        self.set_free_mode()

    def attach_board(self, board: MobileBoardWidget) -> None:
        self._board = board
        self._move_handler = mih.MoveInputHandler(board)
        self._move_handler.add_observer(self)
        self.model.add_observer(board)
        board.bind_game_events(self.model)

    def on_notify(self, event: evt.Event) -> None:
        event_type = type(event)
        if event_type in self._notify_actions:
            self._notify_actions[event_type](event)

    def set_game(self, game: Game) -> None:
        self.model.copy_from(game)

    def set_speedrun_mode(self) -> None:
        self.add_callback(mih.MoveEvent, self.verify_move)

    def set_free_mode(self) -> None:
        self.add_callback(mih.MoveEvent, self._ignore_move)

    def _ignore_move(self, _event: mih.MoveEvent) -> None:
        return

    def verify_move(self, event: mih.MoveEvent) -> None:
        move = event.move
        if not self.model.game.is_mainline(move):
            self._notify_observers(WrongMoveEvent())
            return
        self.model.make_move(move)
        if self.model.game.is_end():
            self._notify_observers(GameEndEvent())
            return
        response_move = self.model.game.get_mainline_move()
        if isinstance(response_move, TerminationMove):
            self._notify_observers(GameEndEvent())
            return
        self.model.make_move(response_move)
        if self.model.game.is_end():
            self._notify_observers(GameEndEvent())

    def enable_move_input(self) -> None:
        if self._move_handler is not None:
            self._move_handler.enable()

    def disable_move_input(self) -> None:
        if self._move_handler is not None:
            self._move_handler.disable()

    def show_solution_line(self) -> None:
        self.model.go_to_end()
        self._notify_observers(GameUpdateEvent(self.model))

    def go_to_start(self) -> None:
        self.model.go_to_start()
