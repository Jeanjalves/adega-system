from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence
import sqlite3
import sessao
from datetime import datetime


class TelaCaixa(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Caixa")
        self.resize(900, 600)

        layout = QVBoxLayout()

        # ================= PESQUISA =================
        self.pesquisa = QLineEdit()
        self.pesquisa.setPlaceholderText("Pesquisar produto por nome ou categoria...")
        self.pesquisa.textChanged.connect(self.filtrar_produtos)
        layout.addWidget(self.pesquisa)

        # ================= TABELA PRODUTOS =================
        self.tabela = QTableWidget(0, 5)
        self.tabela.setHorizontalHeaderLabels(
            ["ID", "Produto", "Categoria", "Preço", "Estoque"]
        )
        self.tabela.setColumnHidden(0, True)
        self.tabela.setColumnWidth(1, 300)
        self.tabela.setColumnWidth(2, 160)
        self.tabela.setColumnWidth(3, 100)
        self.tabela.setColumnWidth(4, 90)
        layout.addWidget(self.tabela)

        # ================= QUANTIDADE =================
        qtd_layout = QHBoxLayout()
        qtd_layout.addWidget(QLabel("Quantidade:"))

        self.qtd = QLineEdit("1")
        self.qtd.setFixedWidth(60)
        qtd_layout.addWidget(self.qtd)

        btn_add = QPushButton("Adicionar (Enter)")
        btn_add.clicked.connect(self.adicionar)
        qtd_layout.addWidget(btn_add)

        layout.addLayout(qtd_layout)

        # ================= CARRINHO =================
        self.carrinho = QTableWidget(0, 4)
        self.carrinho.setHorizontalHeaderLabels(
            ["Produto", "Qtd", "Preço", "Subtotal"]
        )
        self.carrinho.setColumnWidth(0, 350)
        self.carrinho.setColumnWidth(1, 60)
        self.carrinho.setColumnWidth(2, 100)
        self.carrinho.setColumnWidth(3, 120)
        layout.addWidget(self.carrinho)

        # ================= PAGAMENTO =================
        pag_layout = QHBoxLayout()

        pag_layout.addWidget(QLabel("Pagamento:"))
        self.pagamento = QComboBox()
        self.pagamento.addItems(["Dinheiro", "Pix", "Cartão"])
        pag_layout.addWidget(self.pagamento)

        self.lbl_total = QLabel("Total: R$ 0.00")
        self.lbl_total.setStyleSheet("font-size:18px;font-weight:bold")
        pag_layout.addWidget(self.lbl_total)

        btn_finalizar = QPushButton("Finalizar (F2)")
        btn_finalizar.clicked.connect(self.finalizar)
        pag_layout.addWidget(btn_finalizar)

        layout.addLayout(pag_layout)

        self.setLayout(layout)

        self.total = 0
        self.produtos = []

        self.carregar_produtos()

        # ================= ATALHOS =================
        QShortcut(QKeySequence("Return"), self, activated=self.adicionar)
        QShortcut(QKeySequence("F2"), self, activated=self.finalizar)
        QShortcut(QKeySequence("Escape"), self, activated=self.close)

    # ================= BANCO =================
    def carregar_produtos(self):
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
            self.tabela.setItem(i, 0, QTableWidgetItem(str(p[0])))
            self.tabela.setItem(i, 1, QTableWidgetItem(p[1]))
            self.tabela.setItem(i, 2, QTableWidgetItem(p[2] or ""))
            self.tabela.setItem(i, 3, QTableWidgetItem(f"{p[3]:.2f}"))
            self.tabela.setItem(i, 4, QTableWidgetItem(str(p[4])))

    # ================= FILTRO =================
    def filtrar_produtos(self):
        texto = self.pesquisa.text().lower()
        filtrados = [
            p for p in self.produtos
            if texto in p[1].lower()
            or texto in (p[2] or "").lower()
        ]
        self.atualizar_tabela(filtrados)

    # ================= CARRINHO =================
    def adicionar(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um produto")
            return

        try:
            qtd = int(self.qtd.text())
        except ValueError:
            QMessageBox.warning(self, "Erro", "Quantidade inválida")
            return

        estoque = int(self.tabela.item(linha, 4).text())
        if qtd > estoque:
            QMessageBox.warning(self, "Erro", "Estoque insuficiente")
            return

        nome = self.tabela.item(linha, 1).text()
        preco = float(self.tabela.item(linha, 3).text())
        subtotal = preco * qtd

        self.carrinho.insertRow(self.carrinho.rowCount())
        r = self.carrinho.rowCount() - 1
        self.carrinho.setItem(r, 0, QTableWidgetItem(nome))
        self.carrinho.setItem(r, 1, QTableWidgetItem(str(qtd)))
        self.carrinho.setItem(r, 2, QTableWidgetItem(f"{preco:.2f}"))
        self.carrinho.setItem(r, 3, QTableWidgetItem(f"{subtotal:.2f}"))

        self.total += subtotal
        self.lbl_total.setText(f"Total: R$ {self.total:.2f}")

    # ================= FINALIZAR =================
    def finalizar(self):
        if self.total == 0:
            QMessageBox.warning(self, "Erro", "Carrinho vazio")
            return

        data = datetime.now().strftime("%d/%m/%Y %H:%M")
        forma = self.pagamento.currentText()

        self.cur.execute(
            "INSERT INTO vendas (data_hora, total, forma_pagamento, usuario) VALUES (?,?,?,?)",
            (data, self.total, forma, sessao.usuario_logado)
        )
        venda_id = self.cur.lastrowid

        for i in range(self.carrinho.rowCount()):
            nome = self.carrinho.item(i, 0).text()
            qtd = int(self.carrinho.item(i, 1).text())
            subtotal = float(self.carrinho.item(i, 3).text())

            # baixa estoque
            self.cur.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE nome = ?",
                (qtd, nome)
            )

            self.cur.execute(
                "INSERT INTO itens_venda (venda_id, produto, quantidade, subtotal) VALUES (?,?,?,?)",
                (venda_id, nome, qtd, subtotal)
            )

        self.conn.commit()
        QMessageBox.information(self, "Sucesso", "Venda finalizada!")
        self.close()
