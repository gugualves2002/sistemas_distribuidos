import os

class StorageManager:
    def __init__(self, storage_dir="data_storage"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def get_file_path(self, filename):
        return os.path.join(self.storage_dir, filename)

    def save_chunks(self, filename, chunk_iterator):
        """Lê os chunks do gRPC e salva no disco local."""
        filepath = self.get_file_path(filename)
        print(f"[Storage] Gravando arquivo em: {filepath}")
        
        with open(filepath, "wb") as f:
            for chunk in chunk_iterator:
                f.write(chunk.payload)
        return True

    def read_chunks(self, filename, chunk_size=1024 * 1024):
        """Lê o arquivo do disco local e gera pedaços (chunks) de 1MB."""
        filepath = self.get_file_path(filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Arquivo {filename} não encontrado no disco.")
            
        print(f"[Storage] Lendo arquivo de: {filepath}")
        with open(filepath, "rb") as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                yield data