"""Water Buddy for Windows - a small animated hydration reminder.

Put optional transparent PNGs named buddy_idle.png and buddy_drink.png in this
folder. Open Settings from the tray icon to choose other image files, change
the reminder timing, or preview the animation.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QSettings, Qt, QTimer
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPainterPath, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QDialog, QFileDialog, QFormLayout, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QMenu, QMessageBox, QPushButton, QSpinBox,
    QStyle, QSystemTrayIcon, QVBoxLayout, QWidget,
)

APP_NAME = "Water Buddy"
HERE = Path(__file__).resolve().parent


def default_path(filename: str) -> str:
    path = HERE / filename
    return str(path) if path.exists() else ""


def make_drop_icon(size: int = 64) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#2FA8E0"))
    painter.setPen(Qt.PenStyle.NoPen)
    path = QPainterPath()
    path.moveTo(size / 2, 5)
    path.cubicTo(size * .22, size * .42, size * .2, size * .7, size / 2, size * .9)
    path.cubicTo(size * .8, size * .7, size * .78, size * .42, size / 2, 5)
    painter.drawPath(path)
    painter.end()
    return QIcon(pixmap)


class SettingsDialog(QDialog):
    def __init__(self, parent: "WaterBuddy"):
        super().__init__(parent)
        self.buddy = parent
        self.setWindowTitle("Water Buddy settings")
        self.setMinimumWidth(460)
        layout = QVBoxLayout(self)
        intro = QLabel("Personalize your buddy and choose when it checks in.")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        form = QFormLayout()
        self.interval = QSpinBox(); self.interval.setRange(1, 720); self.interval.setSuffix(" minutes")
        self.snooze = QSpinBox(); self.snooze.setRange(1, 120); self.snooze.setSuffix(" minutes")
        self.line1 = QLineEdit(); self.line2 = QLineEdit()
        self.idle = QLineEdit(); self.drink = QLineEdit()
        self.interval.setValue(parent.interval_minutes)
        self.snooze.setValue(parent.snooze_minutes)
        self.line1.setText(parent.line1); self.line2.setText(parent.line2)
        self.idle.setText(parent.idle_path); self.drink.setText(parent.drink_path)
        form.addRow("Remind me every", self.interval)
        form.addRow("Snooze for", self.snooze)
        form.addRow("Bubble, first line", self.line1)
        form.addRow("Bubble, second line", self.line2)
        form.addRow("Standing image", self._file_row(self.idle))
        form.addRow("Drinking image", self._file_row(self.drink))
        layout.addLayout(form)

        buttons = QHBoxLayout()
        preview = QPushButton("Preview")
        preview.clicked.connect(self.preview)
        save = QPushButton("Save")
        save.setDefault(True); save.clicked.connect(self.accept)
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject)
        buttons.addWidget(preview); buttons.addStretch(); buttons.addWidget(cancel); buttons.addWidget(save)
        layout.addLayout(buttons)

    def _file_row(self, edit: QLineEdit) -> QWidget:
        box = QWidget(); row = QHBoxLayout(box); row.setContentsMargins(0, 0, 0, 0)
        browse = QPushButton("Browse…")
        browse.clicked.connect(lambda: self.pick_file(edit))
        row.addWidget(edit); row.addWidget(browse)
        return box

    def pick_file(self, edit: QLineEdit) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Choose a transparent avatar PNG", edit.text(), "PNG images (*.png)")
        if path:
            edit.setText(path)

    def preview(self) -> None:
        self.buddy.apply_values(self.values(), save=False)
        self.buddy.show_reminder()

    def values(self) -> dict:
        return {"interval": self.interval.value(), "snooze": self.snooze.value(),
                "line1": self.line1.text().strip() or "Time to drink",
                "line2": self.line2.text().strip() or "water!",
                "idle": self.idle.text().strip(), "drink": self.drink.text().strip()}


class WaterBuddy(QWidget):
    WIDTH, HEIGHT = 320, 485

    def __init__(self) -> None:
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool
        super().__init__(None, flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.settings = QSettings("dayswithriya", "WaterBuddyWindows")
        self.visible_cycle = False
        self.load_settings()
        self.build_ui()
        self.create_tray()
        self.reminder_timer = QTimer(self)
        self.reminder_timer.setSingleShot(True)
        self.reminder_timer.timeout.connect(self.show_reminder)
        QTimer.singleShot(1000, self.show_reminder)

    def load_settings(self) -> None:
        self.interval_minutes = int(self.settings.value("interval", 30))
        self.snooze_minutes = int(self.settings.value("snooze", 5))
        self.line1 = str(self.settings.value("line1", "Time to drink"))
        self.line2 = str(self.settings.value("line2", "water!"))
        self.idle_path = str(self.settings.value("idle", default_path("buddy_idle.png")))
        self.drink_path = str(self.settings.value("drink", default_path("buddy_drink.png")))

    def build_ui(self) -> None:
        root = QVBoxLayout(self); root.setContentsMargins(20, 18, 20, 14); root.setSpacing(8)
        self.avatar = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.avatar.setMinimumHeight(285)
        root.addWidget(self.avatar, 1)
        self.bubble = QFrame(); self.bubble.setObjectName("bubble")
        bubble_layout = QVBoxLayout(self.bubble); bubble_layout.setContentsMargins(18, 10, 18, 10)
        self.bubble_text = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.bubble_text.setWordWrap(True)
        bubble_layout.addWidget(self.bubble_text)
        root.addWidget(self.bubble)
        row = QHBoxLayout(); row.setSpacing(10)
        self.snooze_button = QPushButton("Snooze")
        self.yes_button = QPushButton("Yes, drank it")
        self.snooze_button.clicked.connect(self.snooze)
        self.yes_button.clicked.connect(self.confirm)
        row.addWidget(self.snooze_button); row.addWidget(self.yes_button)
        root.addLayout(row)
        self.setStyleSheet("""
            QFrame#bubble { background: white; border: 2px solid #cbe7f5; border-radius: 22px; }
            QLabel { color: #0f3a52; font-size: 17px; font-weight: 600; }
            QPushButton { border: none; border-radius: 20px; min-height: 40px; padding: 0 13px; font-size: 14px; font-weight: 600; }
            QPushButton#yes { background: #2fa8e0; color: white; }
            QPushButton#snooze { background: #f0f3f5; color: #37627a; }
        """)
        self.yes_button.setObjectName("yes"); self.snooze_button.setObjectName("snooze")
        self.update_content(False)

    def create_tray(self) -> None:
        self.tray = QSystemTrayIcon(make_drop_icon(), self)
        # Keep Python references to the menu and its actions. Without them,
        # Windows can discard the callbacks after garbage collection.
        self.tray_menu = QMenu(self)
        preview = QAction("Show Water Buddy now", self); preview.triggered.connect(self.show_reminder)
        settings = QAction("Settings…", self); settings.triggered.connect(self.open_settings)
        quit_action = QAction("Quit Water Buddy", self); quit_action.triggered.connect(QApplication.quit)
        self.tray_menu.addAction(preview); self.tray_menu.addAction(settings)
        self.tray_menu.addSeparator(); self.tray_menu.addAction(quit_action)
        self.tray.setContextMenu(self.tray_menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.setToolTip("Water Buddy")
        self.tray.show()

    def on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Open settings with a normal left click as well as the right-click menu."""
        if reason in (QSystemTrayIcon.ActivationReason.Trigger,
                      QSystemTrayIcon.ActivationReason.DoubleClick):
            self.open_settings()

    def avatar_pixmap(self, drinking: bool) -> QPixmap:
        path = self.drink_path if drinking else self.idle_path
        pixmap = QPixmap(path) if path and os.path.exists(path) else QPixmap()
        if not pixmap.isNull():
            return pixmap.scaled(250, 280, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        # Friendly built-in placeholder, so the app works before custom PNGs are added.
        pixmap = QPixmap(250, 280); pixmap.fill(Qt.GlobalColor.transparent)
        p = QPainter(pixmap); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor("#f5c6a5")); p.setPen(Qt.PenStyle.NoPen); p.drawEllipse(88, 25, 76, 76)
        p.setBrush(QColor("#54382f")); p.drawPie(82, 12, 88, 60, 0, 180 * 16)
        p.setBrush(QColor("#7ed2f2")); p.drawRoundedRect(77, 100, 98, 120, 35, 35)
        p.setBrush(QColor("#0f3a52")); p.drawRoundedRect(94, 210, 25, 62, 10, 10); p.drawRoundedRect(133, 210, 25, 62, 10, 10)
        if drinking:
            p.setBrush(QColor("#bce8f8")); p.drawRoundedRect(161, 90, 32, 48, 6, 6)
            p.setPen(QColor("#2fa8e0")); p.setFont(QFont("Segoe UI Emoji", 26)); p.drawText(105, 155, "💧")
        p.end(); return pixmap

    def update_content(self, drinking: bool) -> None:
        self.avatar.setPixmap(self.avatar_pixmap(drinking))
        self.bubble_text.setText(f"💧  {self.line1}\n{self.line2}")

    def position_for(self, on_screen: bool) -> None:
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.right() - self.width() - 22 if on_screen else screen.right() + 8
        self.move(x, screen.bottom() - self.height() - 42)

    def show_reminder(self) -> None:
        if self.visible_cycle:
            return
        self.visible_cycle = True
        self.reminder_timer.stop()
        self.update_content(False); self.bubble.hide(); self.snooze_button.hide(); self.yes_button.hide()
        self.position_for(False); self.show()
        self.slide(True, self.start_drink)

    def slide(self, entering: bool, finished) -> None:
        screen = QApplication.primaryScreen().availableGeometry()
        target_x = screen.right() - self.width() - 22 if entering else screen.right() + 8
        animation = QPropertyAnimation(self, b"pos", self)
        animation.setDuration(1300 if entering else 900)
        animation.setStartValue(self.pos()); animation.setEndValue(self.pos() + self.pos().__class__(target_x - self.x(), 0))
        animation.setEasingCurve(QEasingCurve.Type.OutCubic if entering else QEasingCurve.Type.InQuad)
        animation.finished.connect(finished)
        self._animation = animation
        animation.start()

    def start_drink(self) -> None:
        self.update_content(True)
        QTimer.singleShot(1650, self.show_prompt)

    def show_prompt(self) -> None:
        self.update_content(False); self.bubble.show(); self.snooze_button.show(); self.yes_button.show()
        QTimer.singleShot(20000, self.snooze)

    def confirm(self) -> None:
        self.finish_cycle(self.interval_minutes)

    def snooze(self) -> None:
        self.finish_cycle(self.snooze_minutes)

    def finish_cycle(self, minutes: int) -> None:
        if not self.visible_cycle:
            return
        self.bubble.hide(); self.snooze_button.hide(); self.yes_button.hide()
        self.slide(False, lambda: self.after_cycle(minutes))

    def after_cycle(self, minutes: int) -> None:
        self.hide(); self.visible_cycle = False
        self.reminder_timer.start(minutes * 60 * 1000)

    def apply_values(self, values: dict, save: bool = True) -> None:
        self.interval_minutes = values["interval"]; self.snooze_minutes = values["snooze"]
        self.line1 = values["line1"]; self.line2 = values["line2"]
        self.idle_path = values["idle"]; self.drink_path = values["drink"]
        self.update_content(False)
        if save:
            for key, value in values.items(): self.settings.setValue(key, value)

    def open_settings(self) -> None:
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.apply_values(dialog.values())
            if not self.visible_cycle:
                self.reminder_timer.start(self.interval_minutes * 60 * 1000)


def main() -> None:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName(APP_NAME)
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, APP_NAME, "A Windows notification area (system tray) is required.")
        sys.exit(1)
    buddy = WaterBuddy()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
