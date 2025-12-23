from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
import sqlite3
import sessao
from database import hash_senha


class TelaUsuarios(QWidget):
    def __init__(self):
        super().__init__()

        # 🔒 PERMISSÃO: SOMENTE ADMIN
        if sessao.usuario_logado != "admin":
            QMessageBox.warning(
                self,
                "Acesso negado",
                "Apenas o administrador pode cadastrar usuários."
            )
            self.close()
            return

        self.setWindowTitle("Cadastro de Usuários")
        self.setFixedSize(300, 260)

        layout = QVBoxLayout()

        titulo = QLabel("Cadastro de Usuários")
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

        self.confirmar = QLineEdit()
        self.confirmar.setPlaceholderText("Confirmar Senha")
        self.confirmar.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirmar)

        btn = QPushButton("Cadastrar Usuário")
        btn.clicked.connect(self.cadastrar)
        layout.addWidget(btn)

        self.setLayout(layout)

    def cadastrar(self):
        usuario = self.usuario.text()
        senha = self.senha.text()
        confirmar = self.confirmar.text()

        if not usuario or not senha:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos")
            return

        if senha != confirmar:
            QMessageBox.warning(self, "Erro", "As senhas não conferem")
            return

        conn = sqlite3.connect("adega.db")
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
                (usuario, hash_senha(senha))
            )
            conn.commit()
            QMessageBox.information(self, "Sucesso", "Usuário cadastrado")
            self.close()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Erro", "Usuário já existe")

        conn.close()
