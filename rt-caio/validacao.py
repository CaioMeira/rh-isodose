import pydicom
from pydicom.errors import InvalidDicomError
import os

def validar_dicoms(folder):
    arquivos_invalidos = []

    for root, _, files in os.walk(folder):
        for file in files:
            caminho = os.path.join(root, file)
            try:
                ds = pydicom.dcmread(caminho, stop_before_pixels=True)
            except (InvalidDicomError, Exception) as e:
                print(f"❌ Arquivo inválido: {file} — {e}")
                arquivos_invalidos.append(file)

    return arquivos_invalidos

# Uso:
invalidos = validar_dicoms("/var/data/dcm/prostate")
print(f"\nTotal de inválidos: {len(invalidos)}\n")
