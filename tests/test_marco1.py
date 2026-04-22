import sys
import os
import hashlib
import time

# Adiciona o diretório raiz ao path para encontrar os módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from client.dfs_client import DFSClient

def calculate_sha256(filepath):
    """Calcula o hash SHA-256 de um arquivo para garantir integridade."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Lê em chunks
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def create_dummy_file(filepath, size_mb):
    """Cria um arquivo de tamanho especificado com dados aleatórios."""
    print(f"[*] Criando arquivo de teste {filepath} ({size_mb}MB)...")
    with open(filepath, "wb") as f:
        f.write(os.urandom(size_mb * 1024 * 1024))

def main():
    print("=== Iniciando Bateria de Testes Automatizados - DFS Marco 1 ===")
    
    client = DFSClient()
    test_filename = "simulacao_carga.bin"
    original_filepath = os.path.join("tests", test_filename)
    download_filepath = os.path.join("client_downloads", test_filename)
    
    os.makedirs("tests", exist_ok=True)
    create_dummy_file(original_filepath, size_mb=15) # Arquivo de 15MB
    
    original_hash = calculate_sha256(original_filepath)
    print(f"[*] Hash SHA-256 Original: {original_hash}")

    print("\n[Teste 1] Iniciando Upload para o DataNode...")
    start_time = time.time()
    client.upload(original_filepath)
    upload_time = time.time() - start_time
    print(f"[*] Upload concluído em {upload_time:.2f} segundos.")

    print("\n[Teste 2] Iniciando Download do DataNode...")
    # Remove o arquivo antigo da pasta de downloads se existir para garantir um teste limpo
    if os.path.exists(download_filepath):
        os.remove(download_filepath)
        
    start_time = time.time()
    client.download(test_filename)
    download_time = time.time() - start_time
    print(f"[*] Download concluído em {download_time:.2f} segundos.")

    print("\n[Teste 3] Verificando Integridade dos Dados (Checksum)...")
    downloaded_hash = calculate_sha256(download_filepath)
    print(f"[*] Hash SHA-256 Baixado: {downloaded_hash}")

    if original_hash == downloaded_hash:
        print("\nSUCESSO: Os arquivos são idênticos! Nenhuma perda de dados no transporte gRPC.")
    else:
        print("\nFALHA: Os arquivos são diferentes. Corrupção de dados detectada.")
        
    print("\n[*] Limpando arquivos temporários locais...")
    os.remove(original_filepath)

if __name__ == "__main__":
    main()