from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedSize(420, 260)

        # Janela sem bordas e sempre à frente
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )

        layout = QVBoxLayout()

        titulo = QLabel("Adega System")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size:30px; font-weight:bold;")

        subtitulo = QLabel("Controle de Estoque e Vendas")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("font-size:14px; opacity:0.85;")

        carregando = QLabel("Carregando...")
        carregando.setAlignment(Qt.AlignCenter)
        carregando.setStyleSheet(
            "font-size:12px; margin-top:20px; opacity:0.7;"
        )

        layout.addStretch()
        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addWidget(carregando)
        layout.addStretch()

        self.setLayout(layout)

        # Fecha automaticamente após 2 segundos
        QTimer.singleShot(2000, self.close)
