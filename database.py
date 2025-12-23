import sqlite3
import os
import shutil
from datetime import datetime
import hashlib


def conectar():
    return sqlite3.connect("adega.db")


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # Produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL
        )
    """)

    # Usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    """)

    # Admin padrão (hash)
    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (usuario, senha)
        VALUES (?, ?)
    """, ("admin", hash_senha("admin")))

    # Vendas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT NOT NULL,
            total REAL NOT NULL,
            forma_pagamento TEXT,
            usuario TEXT
        )
    """)

    # Itens da venda
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER,
            produto TEXT,
            quantidade INTEGER,
            preco_unitario REAL,
            subtotal REAL
        )
    """)

    # Fechamento de caixa
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fechamentos_caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT NOT NULL,
            total_vendas REAL NOT NULL,
            total_contado REAL NOT NULL,
            diferenca REAL NOT NULL,
            usuario TEXT
        )
    """)

    conn.commit()
    conn.close()


def backup_automatico():
    if not os.path.exists("adega.db"):
        return

    os.makedirs("backup", exist_ok=True)
    data_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    shutil.copy2("adega.db", f"backup/adega_{data_hora}.db")
