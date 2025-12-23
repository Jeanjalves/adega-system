from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox
)
from PySide6.QtGui import QShortcut, QKeySequence
import sqlite3


class TelaProdutos(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Produtos")
        self.resize(780, 540)

        layout = QVBoxLayout()

        # ================= PESQUISA =================
        self.pesquisa = QLineEdit()
        self.pesquisa.setPlaceholderText("Pesquisar por nome ou categoria...")
        self.pesquisa.textChanged.connect(self.filtrar)
        layout.addWidget(self.pesquisa)

        # ================= TABELA =================
        self.tabela = QTableWidget(0, 5)
        self.tabela.setHorizontalHeaderLabels(
            ["ID", "Nome", "Categoria", "Preço", "Estoque"]
        )
        self.tabela.setColumnHidden(0, True)
        self.tabela.setColumnWidth(1, 250)
        self.tabela.setColumnWidth(2, 150)
        self.tabela.itemSelectionChanged.connect(self.selecionar)
        layout.addWidget(self.tabela)

        # ================= FORM =================
        form = QHBoxLayout()

        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Produto")

        self.categoria = QComboBox()
        self.categoria.addItems([
            "Cerveja", "Destilado", "Vinho",
            "Refrigerante", "Energético", "Outros"
        ])

        self.preco = QLineEdit()
        self.preco.setPlaceholderText("Preço")

        self.estoque = QLineEdit()
        self.estoque.setPlaceholderText("Estoque")

        form.addWidget(self.nome)
        form.addWidget(self.categoria)
        form.addWidget(self.preco)
        form.addWidget(self.estoque)

        layout.addLayout(form)

        # ================= BOTÕES =================
        botoes = QHBoxLayout()

        btn_salvar = QPushButton("Salvar (Ctrl+S)")
        btn_salvar.clicked.connect(self.salvar)

        btn_atualizar = QPushButton("Atualizar (Ctrl+U)")
        btn_atualizar.clicked.connect(self.atualizar)

        btn_excluir = QPushButton("Excluir (Del)")
        btn_excluir.clicked.connect(self.excluir)

        botoes.addWidget(btn_salvar)
        botoes.addWidget(btn_atualizar)
        botoes.addWidget(btn_excluir)
        layout.addLayout(botoes)

        self.setLayout(layout)

        self.id_sel = None
        self.carregar()

        # ================= ATALHOS =================
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self.limpar)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self.salvar)
        QShortcut(QKeySequence("Ctrl+U"), self, activated=self.atualizar)
        QShortcut(QKeySequence("Delete"), self, activated=self.excluir)

    def carregar(self):
        self.conn = sqlite3.connect("adega.db")
        self.cur = self.conn.cursor()
        self.cur.execute(
            "SELECT id, nome, categoria, preco, estoque FROM produtos"
        )
        self.produtos = self.cur.fetchall()
        self.atualizar_tabela(self.produtos)

    def atualizar_tabela(self, lista):
        self.tabela.setRowCount(len(lista))
        for i, p in enumerate(lista):
            for j, v in enumerate(p):
                self.tabela.setItem(i, j, QTableWidgetItem(str(v)))

    def filtrar(self):
        t = self.pesquisa.text().lower()
        filtrados = [
            p for p in self.produtos
            if t in p[1].lower() or t in (p[2] or "").lower()
        ]
        self.atualizar_tabela(filtrados)

    def selecionar(self):
        r = self.tabela.currentRow()
        if r < 0:
            return
        self.id_sel = int(self.tabela.item(r, 0).text())
        self.nome.setText(self.tabela.item(r, 1).text())
        self.categoria.setCurrentText(self.tabela.item(r, 2).text())
        self.preco.setText(self.tabela.item(r, 3).text())
        self.estoque.setText(self.tabela.item(r, 4).text())

    def salvar(self):
        self.cur.execute(
            "INSERT INTO produtos (nome, categoria, preco, estoque) VALUES (?,?,?,?)",
            (
                self.nome.text(),
                self.categoria.currentText(),
                float(self.preco.text()),
                int(self.estoque.text())
            )
        )
        self.conn.commit()
        QMessageBox.information(self, "OK", "Produto cadastrado")
        self.limpar()
        self.carregar()

    def atualizar(self):
        if not self.id_sel:
            return
        self.cur.execute(
            "UPDATE produtos SET nome=?, categoria=?, preco=?, estoque=? WHERE id=?",
            (
                self.nome.text(),
                self.categoria.currentText(),
                float(self.preco.text()),
                int(self.estoque.text()),
                self.id_sel
            )
        )
        self.conn.commit()
        QMessageBox.information(self, "OK", "Produto atualizado")
        self.limpar()
        self.carregar()

    def excluir(self):
        if not self.id_sel:
            return
        self.cur.execute("DELETE FROM produtos WHERE id=?", (self.id_sel,))
        self.conn.commit()
        QMessageBox.information(self, "OK", "Produto excluído")
        self.limpar()
        self.carregar()

    def limpar(self):
        self.nome.clear()
        self.preco.clear()
        self.estoque.clear()
        self.id_sel = None
