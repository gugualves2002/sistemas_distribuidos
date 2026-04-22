import sys
import os

# Adiciona a raiz do projeto e a pasta protos ao sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, 'protos'))

import grpc
import dfs_pb2 as pb2             
import dfs_pb2_grpc as pb2_grpc   

class DFSClient:
    def __init__(self, worker_address='localhost:50051'):
        self.channel = grpc.insecure_channel(worker_address)
        self.stub = pb2_grpc.DataNodeStub(self.channel)

    def upload(self, local_filepath):
        filename = os.path.basename(local_filepath)
        
        def generate_chunks():
            # Lê o arquivo em chunks de 1MB para não estourar a RAM
            with open(local_filepath, "rb") as f:
                while True:
                    data = f.read(1024 * 1024)
                    if not data:
                        break
                    yield pb2.Chunk(filename=filename, payload=data)
        
        try:
            response = self.stub.UploadFile(generate_chunks())
            print(f"Status: {response.message}")
        except grpc.RpcError as e:
            print(f"Erro no Upload: {e.details()}")

    def download(self, filename, output_dir="client_downloads"):
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)
        
        try:
            request = pb2.FileRequest(filename=filename)
            responses = self.stub.DownloadFile(request)
            
            with open(output_path, "wb") as f:
                for chunk in responses:
                    f.write(chunk.payload)
            print(f"Download concluído: {output_path}")
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                print("Erro: Arquivo não existe no DFS.")
            else:
                print(f"Erro no Download: {e.details()}")