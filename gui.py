"""Desktop GUI for the Voice Assistant for Multimedia Controls project.

Uses Tkinter for the interface and reuses the project's existing command,
media-key, microphone, and gesture-recognition modules.
"""

from __future__ import annotations

import queue
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import ttk


# Dark, high-contrast palette.
BG = "#0b1020"
PANEL = "#121a2d"
PANEL_ALT = "#172239"
BORDER = "#263550"
TEXT = "#edf3ff"
MUTED = "#92a1bc"
ACCENT = "#73e0c1"
ACCENT_DARK = "#193e43"
BLUE = "#83a9ff"
BLUE_DARK = "#1b2c50"
PURPLE = "#c3a4ff"
PURPLE_DARK = "#302647"
RED = "#ff7f91"
GREEN = "#70e1a1"


class GUIFeedback:
    """Thread-safe feedback adapter for the GUI and optional speech output."""

    def __init__(self, app: "AssistantGUI") -> None:
        self.app = app
        self.speech_enabled = threading.Event()
        self.speech_enabled.set()
        self.speech_queue: queue.Queue[str | None] = queue.Queue()
        self.speech_thread = threading.Thread(
            target=self._speech_worker, name="assistant-speech", daemon=True
        )
        self.speech_thread.start()

    def say(self, message: str) -> str:
        if not isinstance(message, str) or not message.strip():
            return ""
        message = message.strip()
        self.app.add_log(message, kind="assistant")
        if self.speech_enabled.is_set():
            self.speech_queue.put(message)
        return message

    def set_speech_enabled(self, enabled: bool) -> None:
        if enabled:
            self.speech_enabled.set()
        else:
            self.speech_enabled.clear()

    def _speech_worker(self) -> None:
        """Run TTS on one thread so microphone and gesture workers never race."""
        engine = None
        try:
            import pyttsx3

            engine = pyttsx3.init()
        except Exception:
            engine = None

        while True:
            message = self.speech_queue.get()
            if message is None:
                break
            if engine is None or not self.speech_enabled.is_set():
                continue
            try:
                engine.say(message)
                engine.runAndWait()
            except Exception:
                # Speech is an optional convenience; the GUI log remains usable.
                pass

        if engine is not None:
            try:
                engine.stop()
            except Exception:
                pass

    def close(self) -> None:
        self.speech_queue.put(None)


class AssistantGUI:
    """Tkinter dashboard for voice, gesture, and manual multimedia control."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Sonic · Multimedia Assistant")
        self.root.geometry("1180x820")
        self.root.minsize(980, 700)
        self.root.configure(bg=BG)

        from src.command_handler import CommandHandler
        from src.multimedia_controller import MultimediaController

        self.controller = MultimediaController()
        self.feedback = GUIFeedback(self)
        self.handler = CommandHandler(self.controller, self.feedback)

        self.voice_thread: threading.Thread | None = None
        self.voice_stop_event: threading.Event | None = None
        self.gesture_thread: threading.Thread | None = None
        self.gesture_stop_event: threading.Event | None = None
        self.gesture_running = False
        self.voice_running = False
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.camera_index = tk.StringVar(value="0")
        self.speech_var = tk.BooleanVar(value=True)
        self.command_var = tk.StringVar()
        self._preview_image = None
        self._closing = False

        self._build_styles()
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(80, self._refresh_preview)
        self.add_log("Ready. Choose a control or enter a command.", kind="system")

    def _build_styles(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Dark.TCombobox",
            fieldbackground=PANEL_ALT,
            background=PANEL_ALT,
            foreground=TEXT,
            arrowcolor=TEXT,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
            padding=6,
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", PANEL_ALT)],
            foreground=[("readonly", TEXT)],
            selectbackground=[("readonly", PANEL_ALT)],
            selectforeground=[("readonly", TEXT)],
        )

    def _build_ui(self) -> None:
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True, padx=24, pady=(20, 18))

        # Header
        header = tk.Frame(outer, bg=BG)
        header.pack(fill="x", pady=(0, 18))
        brand = tk.Frame(header, bg=BG)
        brand.pack(side="left", fill="x", expand=True)
        tk.Label(
            brand, text="SONIC", bg=BG, fg=ACCENT,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")
        tk.Label(
            brand, text="Multimedia Assistant", bg=BG, fg=TEXT,
            font=("Segoe UI", 25, "bold"),
        ).pack(anchor="w", pady=(2, 0))
        tk.Label(
            brand,
            text="Hands-free playback, voice commands and gesture control.",
            bg=BG, fg=MUTED, font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(3, 0))

        self.system_badge = tk.Label(
            header, text="●  SYSTEM READY", bg=ACCENT_DARK, fg=ACCENT,
            padx=14, pady=9, font=("Segoe UI", 9, "bold"),
        )
        self.system_badge.pack(side="right", anchor="n", pady=(10, 0))

        # Status strip
        status_strip = tk.Frame(outer, bg=BG)
        status_strip.pack(fill="x", pady=(0, 16))
        self.voice_status = self._status_tile(status_strip, "VOICE INPUT", "Standby", BLUE)
        self.gesture_status = self._status_tile(status_strip, "GESTURE CAMERA", "Disabled", PURPLE)
        self.media_status = self._status_tile(status_strip, "MEDIA CONTROLS", "Available", ACCENT)

        content = tk.Frame(outer, bg=BG)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=6, uniform="content")
        content.columnconfigure(1, weight=5, uniform="content")
        content.rowconfigure(0, weight=1)

        left = tk.Frame(content, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 9))
        right = tk.Frame(content, bg=BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(9, 0))

        self._build_playback_card(left)
        self._build_command_card(left)
        self._build_shortcuts_card(left)
        self._build_voice_card(right)
        self._build_gesture_card(right)
        self._build_log_card(right)

        footer = tk.Frame(outer, bg=BG)
        footer.pack(fill="x", pady=(13, 0))
        tk.Label(
            footer,
            text="LOCAL CONTROLS  /  MICROPHONE + WEBCAM OPTIONAL  /  BUILT FOR DESKTOP",
            bg=BG, fg="#5e6d87", font=("Segoe UI", 8, "bold"),
        ).pack(side="left")
        tk.Label(
            footer, text="v1.0", bg=BG, fg="#5e6d87",
            font=("Segoe UI", 8),
        ).pack(side="right")

    def _status_tile(self, parent: tk.Widget, title: str, value: str, accent: str) -> tk.Label:
        tile = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        tile.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Frame(tile, bg=accent, width=3).pack(side="left", fill="y")
        body = tk.Frame(tile, bg=PANEL)
        body.pack(side="left", fill="x", expand=True, padx=12, pady=10)
        tk.Label(
            body, text=title, bg=PANEL, fg=MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")
        value_label = tk.Label(
            body, text=value, bg=PANEL, fg=TEXT,
            font=("Segoe UI", 11, "bold"),
        )
        value_label.pack(anchor="w", pady=(3, 0))
        return value_label

    def _card(self, parent: tk.Widget, title: str, subtitle: str | None = None) -> tuple[tk.Frame, tk.Frame]:
        card = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", pady=(0, 12))
        header = tk.Frame(card, bg=PANEL)
        header.pack(fill="x", padx=16, pady=(10, 6))
        tk.Label(
            header, text=title, bg=PANEL, fg=TEXT,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w")
        if subtitle:
            tk.Label(
                header, text=subtitle, bg=PANEL, fg=MUTED,
                font=("Segoe UI", 9),
            ).pack(anchor="w", pady=(3, 0))
        body = tk.Frame(card, bg=PANEL)
        body.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        return card, body

    def _button(
        self, parent: tk.Widget, text: str, command, *, bg: str = PANEL_ALT,
        fg: str = TEXT, active_bg: str | None = None, height: int = 2,
        font_size: int = 10, anchor: str = "center",
    ) -> tk.Button:
        return tk.Button(
            parent, text=text, command=command, bg=bg, fg=fg,
            activebackground=active_bg or bg, activeforeground=fg,
            disabledforeground="#63718a",
            relief="flat", bd=0, highlightthickness=0,
            font=("Segoe UI", font_size, "bold"), cursor="hand2",
            height=height, anchor=anchor, padx=10,
        )

    def _build_playback_card(self, parent: tk.Widget) -> None:
        _, body = self._card(
            parent, "Playback deck", "Control whatever media player is active on your computer."
        )
        transport = tk.Frame(body, bg=PANEL)
        transport.pack(fill="x")
        for i in range(4):
            transport.columnconfigure(i, weight=1, uniform="transport")
        actions = [
            ("|◀\nPREVIOUS", "previous track", PANEL_ALT, TEXT),
            ("▶\nPLAY", "play", ACCENT_DARK, ACCENT),
            ("Ⅱ\nPAUSE", "pause", BLUE_DARK, BLUE),
            ("NEXT\n▶|", "next track", PANEL_ALT, TEXT),
        ]
        for col, (label, action, color, foreground) in enumerate(actions):
            btn = self._button(
                transport, label, lambda a=action: self.execute_command(a, "Manual control"),
                bg=color, fg=foreground, active_bg=color, height=3, font_size=10,
            )
            btn.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 5, 0), ipady=3)

        volume = tk.Frame(body, bg=PANEL)
        volume.pack(fill="x", pady=(14, 0))
        tk.Label(
            volume, text="SYSTEM VOLUME", bg=PANEL, fg=MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(side="left")
        self._button(
            volume, "−  Volume down", lambda: self.execute_command("volume down", "Manual control"),
            bg=PANEL_ALT, height=1, font_size=9,
        ).pack(side="right", padx=(7, 0))
        self._button(
            volume, "+  Volume up", lambda: self.execute_command("volume up", "Manual control"),
            bg=PANEL_ALT, height=1, font_size=9,
        ).pack(side="right")

    def _build_command_card(self, parent: tk.Widget) -> None:
        _, body = self._card(
            parent, "Quick command", "Type a supported phrase and press Enter."
        )
        entry_row = tk.Frame(body, bg=PANEL)
        entry_row.pack(fill="x")
        entry = tk.Entry(
            entry_row, textvariable=self.command_var, bg=PANEL_ALT, fg=TEXT,
            insertbackground=TEXT, relief="flat", bd=0,
            font=("Segoe UI", 10), highlightthickness=1,
            highlightbackground=BORDER, highlightcolor=ACCENT,
        )
        entry.pack(side="left", fill="x", expand=True, ipady=11, padx=(0, 8))
        entry.bind("<Return>", self._submit_command)
        self._button(
            entry_row, "Run command  ↗", self._submit_command,
            bg=ACCENT_DARK, fg=ACCENT, active_bg=ACCENT_DARK,
            height=1, font_size=9,
        ).pack(side="right", fill="y")
        tk.Label(
            body,
            text="Examples: play music · pause · next song · volume up",
            bg=PANEL, fg=MUTED, font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(8, 0))

    def _build_shortcuts_card(self, parent: tk.Widget) -> None:
        _, body = self._card(
            parent, "Command shortcuts", "One click sends the same commands as voice input."
        )
        shortcuts = [
            ("Play music", "play", ACCENT_DARK, ACCENT),
            ("Pause music", "pause", BLUE_DARK, BLUE),
            ("Next song", "next song", PANEL_ALT, TEXT),
            ("Previous song", "previous song", PANEL_ALT, TEXT),
            ("Volume up", "volume up", PANEL_ALT, GREEN),
            ("Volume down", "volume down", PANEL_ALT, RED),
        ]
        for row_index in range(3):
            row = tk.Frame(body, bg=PANEL)
            row.pack(fill="x", pady=(0 if row_index == 0 else 6, 0))
            for column in range(2):
                label, command, color, foreground = shortcuts[row_index * 2 + column]
                self._button(
                    row, label, lambda value=command: self.execute_command(value, "Shortcut"),
                    bg=color, fg=foreground, active_bg=color, height=1, font_size=9,
                ).pack(side="left", fill="x", expand=True, padx=(0 if column == 0 else 7, 0))

    def _build_voice_card(self, parent: tk.Widget) -> None:
        _, body = self._card(
            parent, "Voice assistant", "Listen for spoken commands through your microphone."
        )
        top = tk.Frame(body, bg=PANEL)
        top.pack(fill="x")
        tk.Label(
            top, text="MICROPHONE", bg=PANEL, fg=MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(side="left")
        self.voice_inline_status = tk.Label(
            top, text="●  STANDBY", bg=PANEL, fg=BLUE,
            font=("Segoe UI", 8, "bold"),
        )
        self.voice_inline_status.pack(side="right")
        self.voice_button = self._button(
            body, "🎙   Start listening", self.toggle_voice,
            bg=BLUE_DARK, fg=BLUE, active_bg=BLUE_DARK, height=1,
        )
        self.voice_button.pack(fill="x", pady=(6, 5))
        options = tk.Frame(body, bg=PANEL)
        options.pack(fill="x")
        tk.Checkbutton(
            options, text="Spoken responses", variable=self.speech_var,
            command=self._toggle_speech, bg=PANEL, fg=MUTED,
            activebackground=PANEL, activeforeground=TEXT,
            selectcolor=PANEL_ALT, font=("Segoe UI", 9),
            relief="flat", bd=0,
        ).pack(side="left")

    def _build_gesture_card(self, parent: tk.Widget) -> None:
        _, body = self._card(
            parent, "Gesture controls",
            "Use a webcam to control playback, track navigation and volume."
        )
        config = tk.Frame(body, bg=PANEL)
        config.pack(fill="x")
        tk.Label(
            config, text="CAMERA INDEX", bg=PANEL, fg=MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(side="left")
        selector = ttk.Combobox(
            config, textvariable=self.camera_index, values=("0", "1", "2"),
            state="readonly", width=5, style="Dark.TCombobox",
        )
        selector.pack(side="right")
        self.gesture_button = self._button(
            body, "✋   Enable gesture controls", self.toggle_gestures,
            bg=PURPLE_DARK, fg=PURPLE, active_bg=PURPLE_DARK, height=1,
        )
        self.gesture_button.pack(fill="x", pady=(6, 6))

        self.preview = tk.Label(
            body, text="CAMERA PREVIEW\n\nEnable gesture controls to start the camera.",
            bg="#080d18", fg="#657590", font=("Segoe UI", 9, "bold"),
            justify="center", height=3, bd=0,
        )
        self.preview.pack(fill="x")
        mapping = tk.Frame(body, bg=PANEL)
        mapping.pack(fill="x", pady=(9, 0))
        mappings = [
            ("OPEN PALM", "Play", ACCENT),
            ("FIST", "Pause", TEXT),
            ("THUMBS UP", "Volume +", GREEN),
            ("THUMBS DOWN", "Volume −", RED),
            ("PEACE SIGN", "Next song", ACCENT),
            ("POINT UP", "Previous song", BLUE),
        ]
        for column in range(3):
            mapping.columnconfigure(column, weight=1, uniform="gesture-map")
        for index, (label, action, color) in enumerate(mappings):
            row_index = index // 3
            column_index = index % 3
            chip = tk.Frame(mapping, bg=PANEL_ALT)
            chip.grid(
                row=row_index, column=column_index, sticky="ew",
                padx=(0 if column_index == 0 else 4, 0),
                pady=(0 if row_index == 0 else 4, 0),
            )
            tk.Label(
                chip, text=label, bg=PANEL_ALT, fg=MUTED,
                font=("Segoe UI", 6, "bold"),
            ).pack(anchor="center", pady=(4, 0))
            tk.Label(
                chip, text=action, bg=PANEL_ALT, fg=color,
                font=("Segoe UI", 7, "bold"),
            ).pack(anchor="center", pady=(1, 4))

    def _build_log_card(self, parent: tk.Widget) -> None:
        card = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True)
        header = tk.Frame(card, bg=PANEL)
        header.pack(fill="x", padx=16, pady=(13, 8))
        tk.Label(
            header, text="Activity log", bg=PANEL, fg=TEXT,
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")
        self._button(
            header, "Clear", self.clear_log, bg=PANEL_ALT, fg=MUTED,
            height=1, font_size=8,
        ).pack(side="right")
        log_frame = tk.Frame(card, bg=PANEL)
        log_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.log_text = tk.Text(
            log_frame, bg="#0d1424", fg=TEXT, insertbackground=TEXT,
            relief="flat", bd=0, wrap="word", state="disabled",
            font=("Consolas", 9), padx=10, pady=7, height=4,
            selectbackground="#263b59", highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.log_text.tag_configure("time", foreground="#647694")
        self.log_text.tag_configure("assistant", foreground=ACCENT)
        self.log_text.tag_configure("command", foreground=BLUE)
        self.log_text.tag_configure("system", foreground=MUTED)
        self.log_text.tag_configure("error", foreground=RED)

    def _schedule_ui(self, callback) -> None:
        """Schedule a callback on Tk's thread without failing during shutdown."""
        if self._closing:
            return
        try:
            self.root.after(0, callback)
        except (RuntimeError, tk.TclError):
            pass

    def add_log(self, message: str, kind: str = "system") -> None:
        """Append a timestamped message, scheduling safely when called off-thread."""
        self._schedule_ui(lambda: self._append_log(message, kind))

    def _append_log(self, message: str, kind: str) -> None:
        if self._closing or not self.log_text.winfo_exists():
            return
        stamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{stamp}  ", "time")
        self.log_text.insert("end", f"{message}\n", kind if kind in {"assistant", "command", "system", "error"} else "system")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def clear_log(self) -> None:
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self.add_log("Activity log cleared.", kind="system")

    def _submit_command(self, _event=None) -> None:
        command = self.command_var.get().strip()
        if not command:
            return
        self.command_var.set("")
        self.execute_command(command, "Typed command")

    def execute_command(self, command: str, source: str = "Command") -> None:
        normalized = command.strip().lower()
        self.add_log(f"{source}: {normalized}", kind="command")
        try:
            self.handler.handle(normalized)
        except Exception as error:
            self.add_log(f"Command failed: {error}", kind="error")

    def _toggle_speech(self) -> None:
        enabled = self.speech_var.get()
        self.feedback.set_speech_enabled(enabled)
        self.add_log(
            "Spoken responses enabled." if enabled else "Spoken responses disabled.",
            kind="system",
        )

    def toggle_voice(self) -> None:
        if self.voice_running:
            self._stop_voice()
        else:
            self._start_voice()

    def _start_voice(self) -> None:
        if self.voice_thread is not None and self.voice_thread.is_alive():
            self.add_log("Voice listener is still stopping; try again in a moment.", kind="system")
            return
        stop_event = threading.Event()
        self.voice_stop_event = stop_event
        self.voice_running = True
        self.voice_button.configure(text="■   Stop listening", bg="#462532", fg=RED, activebackground="#462532")
        self.voice_inline_status.configure(text="●  LISTENING", fg=GREEN)
        self.voice_status.configure(text="Listening")
        self.add_log("Voice input starting. Microphone calibration may take a moment.", kind="system")
        self.voice_thread = threading.Thread(
            target=self._voice_worker, args=(stop_event,),
            name="voice-input", daemon=True,
        )
        self.voice_thread.start()

    def _stop_voice(self) -> None:
        if self.voice_stop_event is not None:
            self.voice_stop_event.set()
        self.voice_running = False
        self.voice_button.configure(text="Stopping microphone…", state="disabled")
        self.voice_inline_status.configure(text="●  STOPPING", fg=RED)
        self.voice_status.configure(text="Stopping…")
        self.add_log("Voice listener stop requested.", kind="system")

    def _voice_worker(self, stop_event: threading.Event) -> None:
        try:
            from src.voice_input import VoiceInput

            voice_input = VoiceInput(self.feedback)
            while not stop_event.is_set():
                command = voice_input.listen_for_command()
                if stop_event.is_set():
                    break
                if not command:
                    continue
                command = command.strip().lower()
                if command in {"exit", "exit assistant", "quit"}:
                    self.add_log("Voice exit phrase received; listener stopped.", kind="system")
                    break
                self.execute_command(command, "Voice recognized")
        except Exception as error:
            self.add_log(f"Voice input unavailable: {error}", kind="error")
        finally:
            self._schedule_ui(self._voice_stopped)

    def _voice_stopped(self) -> None:
        self.voice_running = False
        self.voice_button.configure(
            text="🎙   Start listening", state="normal",
            bg=BLUE_DARK, fg=BLUE, activebackground=BLUE_DARK,
        )
        self.voice_inline_status.configure(text="●  STANDBY", fg=BLUE)
        self.voice_status.configure(text="Standby")
        self.add_log("Voice input is off.", kind="system")

    def toggle_gestures(self) -> None:
        if self.gesture_running:
            self._stop_gestures()
        else:
            self._start_gestures()

    def _start_gestures(self) -> None:
        if self.gesture_thread is not None and self.gesture_thread.is_alive():
            self.add_log("Gesture camera is still shutting down; try again shortly.", kind="system")
            return
        stop_event = threading.Event()
        self.gesture_stop_event = stop_event
        self.gesture_running = True
        self.gesture_button.configure(
            text="■   Disable gesture controls", bg="#462532", fg=RED,
            activebackground="#462532",
        )
        self.gesture_status.configure(text="Starting…")
        self.add_log("Starting webcam and loading hand-landmark model…", kind="system")
        self.gesture_thread = threading.Thread(
            target=self._gesture_worker, args=(stop_event, self.camera_index.get()),
            name="gesture-control", daemon=True,
        )
        self.gesture_thread.start()

    def _stop_gestures(self) -> None:
        if self.gesture_stop_event is not None:
            self.gesture_stop_event.set()
        self.gesture_running = False
        self.gesture_button.configure(text="Stopping camera…", state="disabled")
        self.gesture_status.configure(text="Stopping…")
        self.add_log("Gesture camera stop requested.", kind="system")

    def _gesture_worker(self, stop_event: threading.Event, camera_index: str) -> None:
        gesture_control = None
        try:
            import cv2
            from src.gesture_control import GestureControl
            from src.gesture_mapping import GestureMapping

            gesture_control = GestureControl(
                camera_index=int(camera_index), show_window=False
            )
            gesture_control.start_camera()
            mapping = GestureMapping()
            self.add_log("Gesture controls are active. Show a clear hand pose to the camera.", kind="system")
            self._schedule_ui(lambda: self.gesture_status.configure(text="Active"))

            while not stop_event.is_set():
                ok, frame = gesture_control.camera.read()
                if not ok:
                    self.add_log("Camera frame could not be read.", kind="error")
                    break
                frame = cv2.flip(frame, 1)
                gesture = gesture_control.recognize_gesture(frame)
                if gesture:
                    command = mapping.map_gesture(gesture)
                    label = gesture.replace("_", " ")
                    cv2.putText(
                        frame, f"Gesture: {label}", (14, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (95, 235, 190), 2,
                        cv2.LINE_AA,
                    )
                    if command:
                        self.execute_command(command, f"Gesture ({label})")
                    else:
                        self.add_log(f"Gesture recognized but not mapped: {label}", kind="system")
                else:
                    cv2.putText(
                        frame, "Show a clear hand gesture", (14, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (210, 220, 235), 1,
                        cv2.LINE_AA,
                    )
                with self.frame_lock:
                    self.latest_frame = frame.copy()
                time.sleep(0.012)
        except Exception as error:
            self.add_log(f"Gesture controls unavailable: {error}", kind="error")
        finally:
            if gesture_control is not None:
                try:
                    gesture_control.close()
                except Exception as error:
                    self.add_log(f"Camera cleanup warning: {error}", kind="error")
            self._schedule_ui(self._gestures_stopped)

    def _gestures_stopped(self) -> None:
        self.gesture_running = False
        self.gesture_button.configure(
            text="✋   Enable gesture controls", state="normal",
            bg=PURPLE_DARK, fg=PURPLE, activebackground=PURPLE_DARK,
        )
        self.gesture_status.configure(text="Disabled")
        self.preview.configure(
            image="", text="CAMERA PREVIEW\n\nEnable gesture controls to start the camera."
        )
        self.preview.image = None
        self._preview_image = None
        with self.frame_lock:
            self.latest_frame = None
        self.add_log("Gesture controls are off.", kind="system")

    def _refresh_preview(self) -> None:
        if self._closing:
            return
        frame = None
        with self.frame_lock:
            if self.latest_frame is not None:
                frame = self.latest_frame.copy()
        if frame is not None and self.gesture_running:
            try:
                import cv2
                from PIL import Image, ImageTk

                width = max(240, self.preview.winfo_width())
                height = 170
                frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = ImageTk.PhotoImage(Image.fromarray(rgb))
                self._preview_image = image
                self.preview.configure(image=image, text="", height=0)
                self.preview.image = image
            except Exception:
                # Preview is non-critical; recognition may still be running.
                pass
        self.root.after(80, self._refresh_preview)

    def close(self) -> None:
        if self._closing:
            return
        self._closing = True
        if self.voice_stop_event is not None:
            self.voice_stop_event.set()
        if self.gesture_stop_event is not None:
            self.gesture_stop_event.set()
        self.feedback.close()
        self.root.destroy()


def main() -> None:
    """Launch the desktop application."""
    root = tk.Tk()
    AssistantGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
