from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem,
    QPushButton, QDateEdit, QTabWidget
)
from PySide6.QtCore import Qt, QDate
import sqlite3
import sessao


class TelaRelatorios(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Relatórios de Vendas")
        self.resize(1000, 700)
        self.setMinimumSize(850, 600)

        layout_principal = QVBoxLayout()

        # ==================================================
        # TÍTULO
        # ==================================================
        titulo = QLabel("Relatórios de Vendas")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size:18px;font-weight:bold")
        layout_principal.addWidget(titulo)

        # ==================================================
        # FILTRO DE DATA
        # ==================================================
        filtro = QHBoxLayout()

        filtro.addWidget(QLabel("Data inicial:"))
        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate())
        filtro.addWidget(self.data_inicio)

        filtro.addWidget(QLabel("Data final:"))
        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate())
        filtro.addWidget(self.data_fim)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.clicked.connect(self.aplicar_filtro)
        filtro.addWidget(btn_filtrar)

        layout_principal.addLayout(filtro)

        # ==================================================
        # BOTÕES RÁPIDOS
        # ==================================================
        rapidos = QHBoxLayout()

        btn_hoje = QPushButton("Hoje")
        btn_hoje.clicked.connect(self.filtro_hoje)
        rapidos.addWidget(btn_hoje)

        btn_mes = QPushButton("Este Mês")
        btn_mes.clicked.connect(self.filtro_mes)
        rapidos.addWidget(btn_mes)

        layout_principal.addLayout(rapidos)

        # ==================================================
        # ABAS
        # ==================================================
        self.tabs = QTabWidget()

        self.criar_aba_vendas()
        self.criar_aba_produtos()
        self.criar_aba_pagamentos()

        if sessao.usuario_logado == "admin":
            self.criar_aba_operadores()

        layout_principal.addWidget(self.tabs)
        self.setLayout(layout_principal)

        self.filtro_hoje()

    # ==================================================
    # ABAS
    # ==================================================
    def criar_aba_vendas(self):
        aba = QWidget()
        layout = QVBoxLayout()

        self.tabela_vendas = QTableWidget(0, 4)
        self.tabela_vendas.setHorizontalHeaderLabels(
            ["Produtos", "Data / Hora", "Total (R$)", "Operador"]
        )

        self.tabela_vendas.setColumnWidth(0, 350)  # Produtos
        self.tabela_vendas.setColumnWidth(1, 150)  # Data
        self.tabela_vendas.setColumnWidth(2, 110)  # Total (R$)
        self.tabela_vendas.setColumnWidth(3, 120)  # Operador

        layout.addWidget(self.tabela_vendas)

        self.lbl_total = QLabel("Total Geral: R$ 0.00")
        self.lbl_total.setAlignment(Qt.AlignRight)
        self.lbl_total.setStyleSheet("font-weight:bold")
        layout.addWidget(self.lbl_total)

        aba.setLayout(layout)
        self.tabs.addTab(aba, "Vendas Realizadas")

    def criar_aba_produtos(self):
        aba = QWidget()
        layout = QVBoxLayout()

        self.tabela_produtos = QTableWidget(0, 3)
        self.tabela_produtos.setHorizontalHeaderLabels(
            ["Produto", "Qtd Vendida", "Faturamento (R$)"]
        )

        self.tabela_produtos.setColumnWidth(0, 400)  # Produto
        self.tabela_produtos.setColumnWidth(1, 120)  # Quantidade
        self.tabela_produtos.setColumnWidth(2, 140)  # Faturamento

        layout.addWidget(self.tabela_produtos)

        aba.setLayout(layout)
        self.tabs.addTab(aba, "Produtos Mais Vendidos")

    def criar_aba_pagamentos(self):
        aba = QWidget()
        layout = QVBoxLayout()

        self.tabela_pagamento = QTableWidget(0, 2)
        self.tabela_pagamento.setHorizontalHeaderLabels(
            ["Forma de Pagamento", "Total (R$)"]
        )

        self.tabela_pagamento.setColumnWidth(0, 300)  # Forma
        self.tabela_pagamento.setColumnWidth(1, 140)  # Total

        layout.addWidget(self.tabela_pagamento)

        aba.setLayout(layout)
        self.tabs.addTab(aba, "Resumo por Pagamento")

    def criar_aba_operadores(self):
        aba = QWidget()
        layout = QVBoxLayout()

        self.tabela_operador = QTableWidget(0, 3)
        self.tabela_operador.setHorizontalHeaderLabels(
            ["Operador", "Qtd Vendas", "Total Vendido (R$)"]
        )

        self.tabela_operador.setColumnWidth(0, 250)  # Operador
        self.tabela_operador.setColumnWidth(1, 120)  # Quantidade
        self.tabela_operador.setColumnWidth(2, 150)  # Total

        layout.addWidget(self.tabela_operador)

        aba.setLayout(layout)
        self.tabs.addTab(aba, "Relatório por Operador")

    # ==================================================
    # FILTROS
    # ==================================================
    def filtro_hoje(self):
        hoje = QDate.currentDate()
        self.data_inicio.setDate(hoje)
        self.data_fim.setDate(hoje)
        self.aplicar_filtro()

    def filtro_mes(self):
        hoje = QDate.currentDate()
        self.data_inicio.setDate(QDate(hoje.year(), hoje.month(), 1))
        self.data_fim.setDate(hoje)
        self.aplicar_filtro()

    def aplicar_filtro(self):
        inicio = self.data_inicio.date().toString("dd/MM/yyyy")
        fim = self.data_fim.date().toString("dd/MM/yyyy")

        self.carregar_vendas(inicio, fim)
        self.carregar_produtos(inicio, fim)
        self.carregar_pagamentos(inicio, fim)

        if sessao.usuario_logado == "admin":
            self.carregar_operadores(inicio, fim)

    # ==================================================
    # CONSULTAS
    # ==================================================
    def carregar_vendas(self, inicio, fim):
        conn = sqlite3.connect("adega.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT id, data_hora, total, usuario
            FROM vendas
            WHERE substr(data_hora,1,10) BETWEEN ? AND ?
            ORDER BY id DESC
        """, (inicio, fim))

        vendas = cur.fetchall()
        self.tabela_vendas.setRowCount(len(vendas))

        total_geral = 0

        for i, (vid, data, total, usuario) in enumerate(vendas):
            cur.execute("SELECT produto FROM itens_venda WHERE venda_id=?", (vid,))
            produtos = ", ".join([p[0] for p in cur.fetchall()])

            self.tabela_vendas.setItem(i, 0, QTableWidgetItem(produtos))
            self.tabela_vendas.setItem(i, 1, QTableWidgetItem(data))
            self.tabela_vendas.setItem(i, 2, QTableWidgetItem(f"{total:.2f}"))
            self.tabela_vendas.setItem(i, 3, QTableWidgetItem(usuario))

            total_geral += total

        self.lbl_total.setText(f"Total Geral: R$ {total_geral:.2f}")
        conn.close()

    def carregar_produtos(self, inicio, fim):
        conn = sqlite3.connect("adega.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT iv.produto, SUM(iv.quantidade), SUM(iv.subtotal)
            FROM itens_venda iv
            JOIN vendas v ON iv.venda_id = v.id
            WHERE substr(v.data_hora,1,10) BETWEEN ? AND ?
            GROUP BY iv.produto
            ORDER BY SUM(iv.quantidade) DESC
        """, (inicio, fim))

        dados = cur.fetchall()
        self.tabela_produtos.setRowCount(len(dados))

        for i, (produto, qtd, total) in enumerate(dados):
            self.tabela_produtos.setItem(i, 0, QTableWidgetItem(produto))
            self.tabela_produtos.setItem(i, 1, QTableWidgetItem(str(qtd)))
            self.tabela_produtos.setItem(i, 2, QTableWidgetItem(f"{total:.2f}"))

        conn.close()

    def carregar_pagamentos(self, inicio, fim):
        conn = sqlite3.connect("adega.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT forma_pagamento, SUM(total)
            FROM vendas
            WHERE substr(data_hora,1,10) BETWEEN ? AND ?
            GROUP BY forma_pagamento
        """, (inicio, fim))

        dados = cur.fetchall()
        self.tabela_pagamento.setRowCount(len(dados))

        for i, (forma, total) in enumerate(dados):
            self.tabela_pagamento.setItem(i, 0, QTableWidgetItem(forma))
            self.tabela_pagamento.setItem(i, 1, QTableWidgetItem(f"{total:.2f}"))

        conn.close()

    def carregar_operadores(self, inicio, fim):
        conn = sqlite3.connect("adega.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT usuario, COUNT(*), SUM(total)
            FROM vendas
            WHERE substr(data_hora,1,10) BETWEEN ? AND ?
            GROUP BY usuario
            ORDER BY SUM(total) DESC
        """, (inicio, fim))

        dados = cur.fetchall()
        self.tabela_operador.setRowCount(len(dados))

        for i, (user, qtd, total) in enumerate(dados):
            self.tabela_operador.setItem(i, 0, QTableWidgetItem(user))
            self.tabela_operador.setItem(i, 1, QTableWidgetItem(str(qtd)))
            self.tabela_operador.setItem(i, 2, QTableWidgetItem(f"{total:.2f}"))

        conn.close()
