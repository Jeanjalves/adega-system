from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
import sqlite3
import sessao
from database import hash_senha


class TelaLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login do Caixa")
        self.setFixedSize(300, 220)

        layout = QVBoxLayout()

        titulo = QLabel("Login do Caixa")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size:16px;font-weight:bold")
        layout.addWidget(titulo)

        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("Usuário")
        layout.addWidget(self.usuario)

        self.senha = QLineEdit()
        self.senha.setPlaceholderText("Senha")
        self.senha.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.senha)

        btn = QPushButton("Entrar")
        btn.clicked.connect(self.login)
        layout.addWidget(btn)

        self.setLayout(layout)

    def login(self):
        usuario = self.usuario.text()
        senha = hash_senha(self.senha.text())

        conn = sqlite3.connect("adega.db")
        cur = conn.cursor()

        cur.execute(
            "SELECT usuario FROM usuarios WHERE usuario=? AND senha=?",
            (usuario, senha)
        )

        if cur.fetchone():
            sessao.usuario_logado = usuario
            self.close()
        else:
            QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos")

        conn.close()
