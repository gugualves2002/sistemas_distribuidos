Relatório Técnico - Marco 1: Fundação do Sistema de Arquivos Distribuídos (DFS)
1. Arquitetura do Sistema (Estado Atual)
Neste primeiro marco, a arquitetura estabelece a fundação de comunicação e persistência do sistema, operando temporariamente em uma topologia Cliente-Servidor com um único nó de armazenamento (DataPlane).

Os componentes atuais são:

  DFS Client (client/dfs_client.py e CLI): Interface do usuário que abstrai a complexidade da rede. É responsável por ler arquivos locais, particioná-los em blocos (chunks) e transmiti-los via rede.

  DataNode Server (core/worker/server.py): O servidor do trabalhador que escuta requisições na porta 50051. Atua como o Data Plane, recebendo blocos de dados pela rede.

  Storage Manager (core/worker/storage.py): Módulo de I/O isolado responsável por interagir diretamente com o sistema de arquivos local do hospedeiro, garantindo a gravação sequencial e leitura dos chunks.

  Protocolo de Comunicação (protos/dfs.proto): O contrato estrito que define as interfaces RPC e o formato binário das mensagens trafegadas.

2. Decisões de Projeto e Justificativas Arquiteturais
  Para garantir que o sistema escale sem gargalos até o Marco 5, as seguintes decisões foram tomadas na fundação:

    gRPC vs. REST para Transferência de Dados: Optou-se pelo gRPC (baseado em HTTP/2 e Protocol Buffers) ao invés do tradicional REST (HTTP/1.1 + JSON). A justificativa reside na natureza binária dos arquivos: o REST exigiria codificação Base64 para tráfego seguro de binários (aumentando o payload em cerca de 33%) e possui limitações severas para streaming bidirecional. O gRPC transmite bytes puros com alta eficiência de CPU e rede.

    Streaming e Particionamento Local (Chunks de 1MB): O sistema não carrega o arquivo inteiro na memória RAM em nenhum momento. Foi implementada uma arquitetura de leitura e gravação orientada a Streams baseada em generators do Python. Isso previne o erro clássico de Out Of Memory (OOM). Se o cliente enviar um arquivo de 5GB, o sistema usará constantemente apenas ~1MB de RAM por conexão, processando o fluxo de forma sequencial.

    Isolamento de Contratos (Protobuf): O uso de um arquivo .proto como fonte da verdade previne falhas de integração no futuro. Qualquer alteração na API de comunicação gerará um erro de compilação imediato, facilitando a governança do código conforme novos nós (como o NameNode) forem adicionados nos próximos marcos.

3. Experimentos Realizados
  Durante a homologação do Marco 1, os seguintes experimentos empíricos foram validados:

    I/O Assíncrono da Rede para o Disco: Um arquivo de 5MB gerado randomicamente (/dev/urandom) foi submetido via CLI. Observou-se a reconstrução perfeita do arquivo no diretório data_storage/ do DataNode.
    
    Recuperação e Reconstrução: Solicitou-se o download do mesmo arquivo pelo cliente. O sistema leu o disco, fez o stream reverso via gRPC e o cliente salvou os dados na pasta client_downloads/. A integridade dos dados foi mantida (validável via verificação de checksum no script de testes automatizados).
    
    Tratamento de Exceções Base: Requisições de download para arquivos inexistentes foram testadas, garantindo que o servidor não sofra crash e retorne corretamente o status grpc.StatusCode.NOT_FOUND.
