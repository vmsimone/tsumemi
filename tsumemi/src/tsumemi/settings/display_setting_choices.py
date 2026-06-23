from __future__ import annotations

import tkinter as tk

from tkinter import ttk

import tsumemi.src.tsumemi.settings.setting_choices as setc


class PieceAlignmentChoice(setc.Choice[str]):
    pass


PIECE_ALIGNMENT_CHOICES: list[PieceAlignmentChoice] = [
    PieceAlignmentChoice("CENTER", "Centered", "CENTER"),
    PieceAlignmentChoice(
        "EDGE",
        "Edge-aligned (Sente bottom, Gote top)",
        "EDGE",
    ),
]


class PieceAlignmentSelection(setc.Selection[str]):
    pass


class PieceAlignmentController:
    def __init__(self) -> None:
        self.model = PieceAlignmentSelection(PIECE_ALIGNMENT_CHOICES)

    def get_alignment(self) -> str:
        return self.model.get_item()

    def get_config_string(self) -> str:
        return self.model.get_config_string()

    def select_by_config(self, config_string: str) -> None:
        self.model.select_by_config(config_string)


class PieceAlignmentDropdown(setc.Dropdown[str]):
    pass


class PieceAlignmentSelectionFrame(ttk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        controller: PieceAlignmentController,
    ) -> None:
        super().__init__(parent)
        self.lbl_name = ttk.Label(self, text="Piece alignment")
        self.cmb_dropdown = PieceAlignmentDropdown(
            parent=self, controller=controller.model
        )
        self.lbl_name.grid(row=0, column=0, sticky="W")
        self.cmb_dropdown.grid(row=0, column=1, sticky="EW")
        self.grid_columnconfigure(1, weight=1)


class AutoNextController:
    def __init__(self, default: bool = False) -> None:
        self._value = default

    def get(self) -> bool:
        return self._value

    def set(self, value: bool) -> None:
        self._value = value

    def get_config_string(self) -> str:
        return "true" if self._value else "false"

    def select_by_config(self, config_string: str) -> None:
        self._value = config_string.lower() == "true"


class AutoNextSelectionFrame(ttk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        controller: AutoNextController,
    ) -> None:
        super().__init__(parent)
        self.controller = controller
        self.var = tk.BooleanVar(value=controller.get())
        self.chk = ttk.Checkbutton(
            self,
            text="Automatically go to next problem after solving",
            variable=self.var,
            command=self._on_change,
        )
        self.chk.grid(row=0, column=0, sticky="W")

    def _on_change(self) -> None:
        self.controller.set(self.var.get())

    def sync_from_controller(self) -> None:
        self.var.set(self.controller.get())
