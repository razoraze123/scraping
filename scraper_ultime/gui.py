from __future__ import annotations

import sys
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QTextEdit,
    QProgressBar,
    QPlainTextEdit,
)

from .main import load_config, save_config, run_scraper, LOGGER


class QtLogHandler(logging.Handler):
    log_signal = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.log_signal.emit(msg)


class ScraperWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, config: dict) -> None:
        super().__init__()
        self.config = config

    def run(self) -> None:
        try:
            run_scraper(self.config)
            self.finished.emit(True, "Scraping terminé")
        except Exception as exc:  # pragma: no cover - GUI thread
            self.finished.emit(False, str(exc))


class ScraperGUI(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Scraper Ultime")
        self.resize(600, 400)

        self.config_path: Optional[Path] = Path(__file__).with_name("config.yaml")
        self.config = load_config(self.config_path.as_posix())

        self.log_handler = QtLogHandler()
        self.log_handler.log_signal.connect(self.append_log)
        LOGGER.addHandler(self.log_handler)

        self.tabs = QTabWidget()
        self.tab_params = QWidget()
        self.tab_scrape = QWidget()
        self.tabs.addTab(self.tab_params, "Paramètres")
        self.tabs.addTab(self.tab_scrape, "Scraping")

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tabs)

        self._init_params_tab()
        self._init_scrape_tab()

    # ------------------ Parameter tab ------------------
    def _init_params_tab(self) -> None:
        layout = QVBoxLayout()

        self.url_input = QLineEdit(self.config.get("url", ""))
        layout.addWidget(QLabel("URL de la collection:"))
        layout.addWidget(self.url_input)

        # output directory
        out_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit(self.config.get("output_dir", ""))
        btn_out = QPushButton("Choisir...")
        btn_out.clicked.connect(self.choose_output_dir)
        out_layout.addWidget(self.output_dir_edit)
        out_layout.addWidget(btn_out)
        layout.addWidget(QLabel("Dossier de sortie:"))
        layout.addLayout(out_layout)

        self.dynamic_box = QCheckBox("Mode dynamique (JavaScript)")
        self.dynamic_box.setChecked(self.config.get("mode", "static") == "dynamic")
        layout.addWidget(self.dynamic_box)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["csv", "json", "xlsx"])
        self.format_combo.setCurrentText(self.config.get("output_format", "csv"))
        layout.addWidget(QLabel("Format de sortie:"))
        layout.addWidget(self.format_combo)

        self.max_pages_spin = QSpinBox()
        self.max_pages_spin.setRange(1, 1000)
        self.max_pages_spin.setValue(self.config.get("max_pages", 10))
        layout.addWidget(QLabel("Nombre max de pages:"))
        layout.addWidget(self.max_pages_spin)

        self.headless_box = QCheckBox("Headless")
        self.headless_box.setChecked(self.config.get("headless", True))
        layout.addWidget(self.headless_box)

        # config file choose
        cfg_layout = QHBoxLayout()
        self.config_edit = QPlainTextEdit()
        self.config_edit.setPlainText(Path(self.config_path).read_text(encoding="utf-8"))
        btn_cfg = QPushButton("Ouvrir config...")
        btn_cfg.clicked.connect(self.choose_config)
        cfg_layout.addWidget(btn_cfg)
        layout.addLayout(cfg_layout)
        layout.addWidget(QLabel("Edition config.yaml:"))
        layout.addWidget(self.config_edit)

        self.tab_params.setLayout(layout)

    def choose_output_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Choisir le dossier de sortie")
        if path:
            self.output_dir_edit.setText(path)

    def choose_config(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Choisir config.yaml", str(self.config_path), "YAML (*.yaml *.yml)")
        if file_path:
            self.config_path = Path(file_path)
            self.config = load_config(file_path)
            self.output_dir_edit.setText(self.config.get("output_dir", ""))
            self.url_input.setText(self.config.get("url", ""))
            self.dynamic_box.setChecked(self.config.get("mode", "static") == "dynamic")
            self.format_combo.setCurrentText(self.config.get("output_format", "csv"))
            self.max_pages_spin.setValue(self.config.get("max_pages", 10))
            self.headless_box.setChecked(self.config.get("headless", True))
            self.config_edit.setPlainText(Path(file_path).read_text(encoding="utf-8"))

    # ------------------ Scraping tab ------------------
    def _init_scrape_tab(self) -> None:
        layout = QVBoxLayout()
        self.start_btn = QPushButton("Lancer le scraping")
        self.start_btn.clicked.connect(self.start_scraping)
        layout.addWidget(self.start_btn)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indefinite
        self.progress.hide()
        layout.addWidget(self.progress)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

        open_out_btn = QPushButton("Ouvrir le dossier de sortie")
        open_out_btn.clicked.connect(self.open_output_dir)
        layout.addWidget(open_out_btn)

        self.tab_scrape.setLayout(layout)

    def append_log(self, text: str) -> None:
        self.log_view.append(text)

    def start_scraping(self) -> None:
        try:
            cfg_text = self.config_edit.toPlainText()
            cfg = load_config(self.config_path.as_posix()) if self.config_path.exists() else {}
            if cfg_text:
                try:
                    import yaml
                    cfg = yaml.safe_load(cfg_text) or {}
                except Exception as exc:
                    QMessageBox.warning(self, "Erreur", f"YAML invalide: {exc}")
                    return
            cfg.update(
                {
                    "url": self.url_input.text(),
                    "output_dir": self.output_dir_edit.text(),
                    "mode": "dynamic" if self.dynamic_box.isChecked() else "static",
                    "output_format": self.format_combo.currentText(),
                    "max_pages": self.max_pages_spin.value(),
                    "headless": self.headless_box.isChecked(),
                }
            )
            save_config(cfg, self.config_path.as_posix())
        except Exception as exc:  # pragma: no cover - GUI path
            QMessageBox.warning(self, "Erreur", str(exc))
            return

        self.progress.show()
        self.log_view.clear()
        self.worker = ScraperWorker(cfg)
        self.worker.finished.connect(self.scrape_finished)
        self.worker.start()

    def scrape_finished(self, ok: bool, message: str) -> None:
        self.progress.hide()
        QMessageBox.information(self, "Terminé" if ok else "Erreur", message)

    def open_output_dir(self) -> None:
        out_dir = Path(self.output_dir_edit.text())
        if out_dir.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(out_dir.as_posix()))
        else:
            QMessageBox.warning(self, "Erreur", "Dossier de sortie introuvable")


def main() -> None:
    app = QApplication(sys.argv)
    gui = ScraperGUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
