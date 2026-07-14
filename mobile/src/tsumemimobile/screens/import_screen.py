from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from tsumemimobile.storage.kifu_storage import import_demo_kifus, resource_path

if TYPE_CHECKING:
    from tsumemimobile.session import MobileSession


class ImportScreen(Screen):
    """Import KIF/KIFU files into local storage."""

    def __init__(
        self,
        session: MobileSession,
        on_ready: Callable[[], None],
        **kwargs: object,
    ) -> None:
        super().__init__(name="import", **kwargs)
        self.session = session
        self.on_ready = on_ready
        root = BoxLayout(orientation="vertical", padding=16, spacing=12)
        root.add_widget(
            Label(
                text="Tsumemi Mobile\nOffline tsumeshogi speedrun",
                halign="center",
                valign="middle",
            )
        )
        self.status = Label(text="", halign="center", size_hint_y=0.2)
        root.add_widget(self.status)
        demo_btn = Button(text="Import demo set (3 problems)", size_hint_y=0.15)
        demo_btn.bind(on_release=lambda _x: self._import_demo())
        root.add_widget(demo_btn)
        folder_btn = Button(
            text="Pick folder (desktop dev)", size_hint_y=0.15
        )
        folder_btn.bind(on_release=lambda _x: self._pick_folder())
        root.add_widget(folder_btn)
        start_btn = Button(text="Start speedrun", size_hint_y=0.15)
        start_btn.bind(on_release=lambda _x: self._try_start())
        root.add_widget(start_btn)
        self.add_widget(root)
        self._refresh_status()

    def on_enter(self, *_args: object) -> None:
        self._refresh_status()

    def _refresh_status(self) -> None:
        count = self.session.reload_problem_list()
        self.status.text = f"{count} problem(s) in library\n{self.session.library_dir}"

    def _import_demo(self) -> None:
        demo_dir = resource_path("demo_kifus")
        imported = import_demo_kifus(demo_dir, self.session.library_dir)
        self._refresh_status()
        self.status.text += f"\nImported {len(imported)} demo file(s)"

    def _pick_folder(self) -> None:
        try:
            from tkinter import Tk, filedialog

            root = Tk()
            root.withdraw()
            folder = filedialog.askdirectory(title="Select KIF folder")
            root.destroy()
        except Exception:
            self.status.text = "Folder picker unavailable on this platform"
            return
        if not folder:
            return
        from tsumemi.src.tsumemi import files

        paths = list(files.get_kif_files(folder, recursive=False))
        from tsumemimobile.storage.kifu_storage import import_kifu_files

        imported = import_kifu_files(paths, self.session.library_dir)
        self._refresh_status()
        self.status.text += f"\nImported {len(imported)} file(s)"

    def _try_start(self) -> None:
        if self.session.problem_list.is_empty():
            self.status.text = "Import problems first"
            return
        self.on_ready()
