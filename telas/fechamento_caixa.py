from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QDateEdit
)
from PySide6.QtCore import Qt, QDate
import sqlite3
from datetime import datetime


class TelaFechamentoCaixa(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Fechamento de Caixa")
        self.setFixedSize(420, 360)

        layout = QVBoxLayout()

        # ===== TÍTULO =====
        titulo = QLabel("Fechamento de Caixa")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        # ===== FILTRO DE DATA =====
        filtro_layout = QHBoxLayout()

        filtro_layout.addWidget(QLabel("Data inicial:"))
        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate())
        filtro_layout.addWidget(self.data_inicio)

        filtro_layout.addWidget(QLabel("Data final:"))
        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate())
        filtro_layout.addWidget(self.data_fim)

        layout.addLayout(filtro_layout)

        # ===== BOTÕES RÁPIDOS =====
        botoes = QHBoxLayout()

        btn_hoje = QPushButton("Hoje")
        btn_hoje.clicked.connect(self.filtro_hoje)
        botoes.addWidget(btn_hoje)

        btn_mes = QPushButton("Este Mês")
        btn_mes.clicked.connect(self.filtro_mes)
        botoes.addWidget(btn_mes)

        layout.addLayout(botoes)

        # ===== TOTAIS =====
        self.lbl_total_vendas = QLabel("Total de Vendas: R$ 0.00")
        self.lbl_total_vendas.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.lbl_total_vendas)

        linha_contado = QHBoxLayout()
        linha_contado.addWidget(QLabel("Valor contado (R$):"))

        self.input_contado = QLineEdit()
        self.input_contado.setPlaceholderText("Ex: 150.00")
        linha_contado.addWidget(self.input_contado)

        layout.addLayout(linha_contado)

        self.lbl_diferenca = QLabel("Diferença: R$ 0.00")
        layout.addWidget(self.lbl_diferenca)

        # ===== BOTÕES =====
        btn_calcular = QPushButton("Calcular Diferença")
        btn_calcular.clicked.connect(self.calcular_diferenca)
        layout.addWidget(btn_calcular)

        btn_fechar = QPushButton("Confirmar Fechamento")
        btn_fechar.clicked.connect(self.confirmar_fechamento)
        layout.addWidget(btn_fechar)

        self.setLayout(layout)

        self.total_vendas = 0.0
        self.filtro_hoje()  # padrão ao abrir

    # --------------------------------------------------
    # FILTROS RÁPIDOS
    # --------------------------------------------------

    def filtro_hoje(self):
        hoje = QDate.currentDate()
        self.data_inicio.setDate(hoje)
        self.data_fim.setDate(hoje)
        self.carregar_total_vendas()

    def filtro_mes(self):
        hoje = QDate.currentDate()
        primeiro_dia = QDate(hoje.year(), hoje.month(), 1)
        self.data_inicio.setDate(primeiro_dia)
        self.data_fim.setDate(hoje)
        self.carregar_total_vendas()

    # --------------------------------------------------

    def carregar_total_vendas(self):
        data_inicio = self.data_inicio.date().toString("dd/MM/yyyy")
        data_fim = self.data_fim.date().toString("dd/MM/yyyy")

        conn = sqlite3.connect("adega.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT SUM(total)
            FROM vendas
            WHERE substr(data_hora, 1, 10) BETWEEN ? AND ?
        """, (data_inicio, data_fim))

        resultado = cur.fetchone()[0]
        self.total_vendas = resultado if resultado else 0.0

        self.lbl_total_vendas.setText(
            f"Total de Vendas: R$ {self.total_vendas:.2f}"
        )

        self.lbl_diferenca.setText("Diferença: R$ 0.00")
        conn.close()

    # --------------------------------------------------

    def calcular_diferenca(self):
        try:
            total_contado = float(self.input_contado.text().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Erro", "Informe um valor válido.")
            return

        diferenca = total_contado - self.total_vendas
        self.lbl_diferenca.setText(f"Diferença: R$ {diferenca:.2f}")

    # --------------------------------------------------

    def confirmar_fechamento(self):
        try:
            total_contado = float(self.input_contado.text().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Erro", "Informe um valor válido.")
            return

        diferenca = total_contado - self.total_vendas
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        conn = sqlite3.connect("adega.db")
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO fechamentos_caixa
            (data_hora, total_vendas, total_contado, diferenca)
            VALUES (?, ?, ?, ?)
        """, (data_hora, self.total_vendas, total_contado, diferenca))

        conn.commit()
        conn.close()

        QMessageBox.information(
            self,
            "Fechamento Realizado",
            "Fechamento de caixa salvo com sucesso!"
        )

        self.close()
