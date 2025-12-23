import sys
import os

def caminho_relativo(caminho):
    """
    Retorna o caminho correto tanto no modo Python normal
    quanto quando o sistema está rodando como .exe (PyInstaller)
    """
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, caminho)
    return os.path.join(os.path.abspath("."), caminho)
