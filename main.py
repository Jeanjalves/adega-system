import sys
import sessao

from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from database import criar_tabelas, backup_automatico
from utils import caminho_relativo

from telas.splash import SplashScreen
from telas.login import TelaLogin
from telas.usuarios import TelaUsuarios
from produtos import TelaProdutos
from telas.caixa import TelaCaixa
from telas.relatorios import TelaRelatorios
from telas.fechamento_caixa import TelaFechamentoCaixa


class JanelaPrincipal(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Adega System")
        self.setFixedSize(360, 450)
        self.setWindowIcon(QIcon(caminho_relativo("icons/caixa.png")))

        layout = QVBoxLayout()

        titulo = QLabel("Adega System")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size:22px;font-weight:bold")
        layout.addWidget(titulo)

        botoes = [
            ("Produtos", "icons/produtos.png", self.abrir_produtos),
            ("Caixa", "icons/caixa.png", self.abrir_caixa),
            ("Relatórios", "icons/relatorios.png", self.abrir_relatorios),
            ("Fechamento de Caixa", "icons/fechamento.png", self.abrir_fechamento),
        ]

        for texto, icone, acao in botoes:
            btn = QPushButton(texto)
            btn.setIcon(QIcon(caminho_relativo(icone)))
            btn.setIconSize(QSize(20, 20))
            btn.setMinimumHeight(40)
            btn.clicked.connect(acao)
            layout.addWidget(btn)

        if sessao.usuario_logado == "admin":
            btn_usuarios = QPushButton("Usuários")
            btn_usuarios.setIcon(QIcon(caminho_relativo("icons/usuarios.png")))
            btn_usuarios.setIconSize(QSize(20, 20))
            btn_usuarios.setMinimumHeight(40)
            btn_usuarios.clicked.connect(self.abrir_usuarios)
            layout.addWidget(btn_usuarios)

        btn_sair = QPushButton("Sair")
        btn_sair.setIcon(QIcon(caminho_relativo("icons/sair.png")))
        btn_sair.setIconSize(QSize(20, 20))
        btn_sair.setMinimumHeight(40)
        btn_sair.clicked.connect(self.close)
        layout.addWidget(btn_sair)

        self.setLayout(layout)

    def abrir_produtos(self):
        self.tela = TelaProdutos()
        self.tela.show()

    def abrir_caixa(self):
        self.tela = TelaCaixa()
        self.tela.show()

    def abrir_relatorios(self):
        self.tela = TelaRelatorios()
        self.tela.show()

    def abrir_fechamento(self):
        self.tela = TelaFechamentoCaixa()
        self.tela.show()

    def abrir_usuarios(self):
        self.tela = TelaUsuarios()
        self.tela.show()


if __name__ == "__main__":
    criar_tabelas()
    backup_automatico()

    app = QApplication(sys.argv)

    # ===== TEMA =====
    with open(caminho_relativo("estilo/tema.qss"), "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    # ===== SPLASH =====
    splash = SplashScreen()
    splash.show()
    app.processEvents()

    while splash.isVisible():
        app.processEvents()

    # ===== LOGIN =====
    login = TelaLogin()
    login.show()
    app.exec()

    if sessao.usuario_logado:
        janela = JanelaPrincipal()
        janela.show()
        sys.exit(app.exec())
