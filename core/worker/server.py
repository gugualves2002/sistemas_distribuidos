import sys
import os

# Adiciona a raiz do projeto e a pasta protos ao sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, 'protos'))

import grpc
from concurrent import futures
import dfs_pb2 as pb2             
import dfs_pb2_grpc as pb2_grpc   
from core.worker.storage import StorageManager

class DataNodeServicer(pb2_grpc.DataNodeServicer):
    def __init__(self):
        self.storage = StorageManager()

    def UploadFile(self, request_iterator, context):
        try:
            first_chunk = next(request_iterator)
            filename = first_chunk.filename

            def chunk_generator():
                yield first_chunk
                for chunk in request_iterator:
                    yield chunk
            self.storage.save_chunks(filename, chunk_generator())
            
            return pb2.UploadStatus(success=True, message=f"Arquivo {filename} salvo com sucesso!")
            
        except StopIteration:
            return pb2.UploadStatus(success=False, message="Stream de dados vazio.")
        except Exception as e:
            return pb2.UploadStatus(success=False, message=str(e))

    def DownloadFile(self, request, context):
        try:
            for data in self.storage.read_chunks(request.filename):
                yield pb2.Chunk(filename=request.filename, payload=data)
        except FileNotFoundError:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Arquivo não encontrado')
            return

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_DataNodeServicer_to_server(DataNodeServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("[DataNode] Servidor rodando na porta 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()