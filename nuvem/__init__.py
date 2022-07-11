"""Módulo para obtenção e manipulação de dados dos principais centros meteorológicos/hidrológicos."""
import os

# * Configuração de processamento com xarray
os.environ["NUMEXPR_MAX_THREADS"] = "16"
os.environ["NUMEXPR_NUM_THREADS"] = "8"