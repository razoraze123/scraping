from __future__ import annotations

import subprocess
import sys

from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ScraperGUI(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Scraper Ultime")
        layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL de la collection")
        layout.addWidget(QLabel("URL:"))
        layout.addWidget(self.url_input)

        self.dynamic_mode = QCheckBox("Mode dynamique (JavaScript)")
        layout.addWidget(self.dynamic_mode)

        self.format_dropdown = QComboBox()
        self.format_dropdown.addItems(["csv", "json", "xlsx"])
        layout.addWidget(QLabel("Format de sortie:"))
        layout.addWidget(self.format_dropdown)

        self.scrape_button = QPushButton("Lancer le scraper")
        self.scrape_button.clicked.connect(self.run_scraper)
        layout.addWidget(self.scrape_button)

        self.setLayout(layout)

    def run_scraper(self) -> None:
        url = self.url_input.text()
        is_dynamic = self.dynamic_mode.isChecked()
        output_format = self.format_dropdown.currentText()

        if not url:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une URL.")
            return

        cmd = [
            sys.executable,
            "-m",
            "scraper_ultime.main",
            "--config",
            "scraper_ultime/config.yaml",
        ]
        # Update config.yaml dynamically
        import yaml

        with open("scraper_ultime/config.yaml", "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        cfg["url"] = url
        cfg["mode"] = "dynamic" if is_dynamic else "static"
        cfg["output_format"] = output_format
        with open("scraper_ultime/config.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(cfg, f)

        QMessageBox.information(self, "Info", f"Scraping de {url} en cours...")
        subprocess.Popen(cmd)


def main() -> None:
    app = QApplication(sys.argv)
    gui = ScraperGUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
