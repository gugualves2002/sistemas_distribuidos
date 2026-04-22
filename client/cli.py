import argparse
from dfs_client import DFSClient

def main():
    parser = argparse.ArgumentParser(description="DFS Client - Marco 1")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # Upload
    upload_parser = subparsers.add_parser("upload", help="Fazer upload de um arquivo")
    upload_parser.add_argument("filepath", help="Caminho do arquivo local")

    # Download
    download_parser = subparsers.add_parser("download", help="Fazer download de um arquivo")
    download_parser.add_argument("filename", help="Nome do arquivo no DFS")

    args = parser.parse_args()
    client = DFSClient()

    if args.command == "upload":
        client.upload(args.filepath)
    elif args.command == "download":
        client.download(args.filename)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()