from __future__ import annotations

from typing import TYPE_CHECKING

import tsumemi.src.tsumemi.event as evt

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from tsumemi.src.shogi.basetypes import HAND_TYPES, Koma, KomaType, Side
from tsumemi.src.shogi.move import Move
from tsumemi.src.shogi.square import Square
from tsumemi.src.tsumemi.game.game_model import GameStepEvent, GameUpdateEvent

if TYPE_CHECKING:
    from tsumemi.src.shogi.position import Position
    from tsumemi.src.tsumemi.game.game_model import GameModel
    from tsumemi.src.tsumemi.move_input_handler import MoveInputHandler


KOMA_LABELS: dict[Koma, str] = {
    Koma.FU: "歩",
    Koma.KY: "香",
    Koma.KE: "桂",
    Koma.GI: "銀",
    Koma.KI: "金",
    Koma.KA: "角",
    Koma.HI: "飛",
    Koma.OU: "玉",
    Koma.TO: "と",
    Koma.NY: "杏",
    Koma.NK: "圭",
    Koma.NG: "全",
    Koma.UM: "馬",
    Koma.RY: "龍",
    Koma.vFU: "v歩",
    Koma.vKY: "v香",
    Koma.vKE: "v桂",
    Koma.vGI: "v銀",
    Koma.vKI: "v金",
    Koma.vKA: "v角",
    Koma.vHI: "v飛",
    Koma.vOU: "v玉",
    Koma.vTO: "vと",
    Koma.vNY: "v杏",
    Koma.vNK: "v圭",
    Koma.vNG: "v全",
    Koma.vUM: "v馬",
    Koma.vRY: "v龍",
}


class MobileBoardWidget(BoxLayout, evt.IObserver):
    """Minimal shogi board for touch input; duck-types as BoardCanvas."""

    def __init__(self, **kwargs: object) -> None:
        super().__init__(orientation="vertical", spacing=4, padding=4, **kwargs)
        evt.IObserver.__init__(self)
        self.position: Position | None = None
        self.move_input_handler: MoveInputHandler | None = None
        self.play_as_side = Side.SENTE
        self.inverted = False
        self._focused_sq = Square.NONE
        self._focused_ktype = KomaType.NONE
        self._square_buttons: dict[Square, Button] = {}
        self._hand_buttons: dict[tuple[Side, KomaType], Button] = {}
        self._north_hand = BoxLayout(size_hint_y=0.08, spacing=2)
        self._board_grid = GridLayout(cols=9, spacing=1, size_hint_y=0.84)
        self._south_hand = BoxLayout(size_hint_y=0.08, spacing=2)
        self.add_widget(self._north_hand)
        self.add_widget(self._board_grid)
        self.add_widget(self._south_hand)
        self._build_board_grid()

    def _build_board_grid(self) -> None:
        self._board_grid.clear_widgets()
        self._square_buttons.clear()
        for drow in range(9):
            for dcol in range(9):
                sq = self._display_to_square(dcol, drow)
                btn = Button(
                    text="",
                    font_size="14sp",
                    background_normal="",
                    background_color=(0.93, 0.86, 0.68, 1),
                )
                btn.bind(on_release=lambda _inst, s=sq: self._on_square_press(s))
                self._square_buttons[sq] = btn
                self._board_grid.add_widget(btn)

    def bind_game_events(self, model: GameModel) -> None:
        model.add_observer(self)

    def on_notify(self, event: evt.Event) -> None:
        if isinstance(event, (GameUpdateEvent, GameStepEvent)):
            self.receive_position_and_last_move(
                event.game.get_position(), event.game.get_last_move()
            )

    def receive_position_and_last_move(self, pos: Position, _last_move: Move) -> None:
        self.set_position(pos)

    def set_position(self, pos: Position) -> None:
        self.position = pos
        if self.move_input_handler is not None:
            self.move_input_handler.position = pos
        self._redraw()

    def set_play_as_side(self, side: Side) -> None:
        self.play_as_side = side

    def set_inverted(self, inverted: bool) -> None:
        self.inverted = inverted
        self._build_board_grid()
        if self.position is not None:
            self._redraw()

    def set_focus(self, sq: Square, ktype: KomaType = KomaType.NONE) -> None:
        self._focused_sq = sq
        self._focused_ktype = ktype
        self._redraw()

    def prompt_promotion(self, sq: Square, ktype: KomaType) -> None:
        content = BoxLayout(orientation="vertical", spacing=8, padding=8)
        popup = Popup(
            title="Promote?",
            content=content,
            size_hint=(0.8, 0.35),
            auto_dismiss=False,
        )

        def choose(is_promotion: bool | None) -> None:
            popup.dismiss()
            if self.move_input_handler is not None:
                self.move_input_handler.execute_promotion_choice(
                    is_promotion, sq, ktype
                )

        content.add_widget(Button(text="Promote", on_release=lambda _x: choose(True)))
        content.add_widget(
            Button(text="No promotion", on_release=lambda _x: choose(False))
        )
        content.add_widget(Button(text="Cancel", on_release=lambda _x: choose(None)))
        popup.open()

    def clear_promotion_prompts(self) -> None:
        return

    def is_inverted(self, side: Side) -> bool:
        return side != self.play_as_side

    def _display_to_square(self, dcol: int, drow: int) -> Square:
        if self.inverted:
            col = 9 - dcol
            row = 9 - drow
        else:
            col = dcol + 1
            row = 9 - drow
        return Square.from_cr(col, row)

    def _square_label(self, koma: Koma) -> str:
        if koma == Koma.NONE:
            return ""
        return KOMA_LABELS.get(koma, str(koma))

    def _redraw(self) -> None:
        if self.position is None:
            return
        for sq, btn in self._square_buttons.items():
            koma = self.position.get_koma(sq)
            btn.text = self._square_label(koma)
            if sq == self._focused_sq:
                btn.background_color = (0.75, 0.85, 1.0, 1)
            else:
                btn.background_color = (0.93, 0.86, 0.68, 1)
        self._redraw_hands()

    def _redraw_hands(self) -> None:
        self._north_hand.clear_widgets()
        self._south_hand.clear_widgets()
        self._hand_buttons.clear()
        if self.position is None:
            return
        north = self.play_as_side.switch()
        south = self.play_as_side
        self._fill_hand_row(self._north_hand, north)
        self._fill_hand_row(self._south_hand, south)

    def _fill_hand_row(self, row: BoxLayout, side: Side) -> None:
        if self.position is None:
            return
        hand = self.position.get_hand_of_side(side)
        for ktype in HAND_TYPES:
            count = hand.get_komatype_count(ktype)
            if count <= 0:
                continue
            label = f"{KOMA_LABELS.get(Koma.make(side, ktype), '?')}×{count}"
            btn = Button(text=label, size_hint_x=None, width=56, font_size="12sp")
            btn.bind(
                on_release=lambda _inst, kt=ktype, sd=side: self._on_hand_press(kt, sd)
            )
            self._hand_buttons[(side, ktype)] = btn
            row.add_widget(btn)

    def _on_square_press(self, sq: Square) -> None:
        if self.move_input_handler is not None:
            self.move_input_handler.receive_square(None, sq)

    def _on_hand_press(self, ktype: KomaType, side: Side) -> None:
        if self.move_input_handler is not None:
            self.move_input_handler.receive_square(
                None, Square.HAND, hand_ktype=ktype, hand_side=side
            )
