# Reflexao — Roteiro 03 (RPC, REST e gRPC)

## 1) Stubs e skeletons

Na Tarefa 2 dá para enxergar bem o beneficio do RPC, porque o **stub** (lado do cliente) e o **skeleton** (lado do servidor) estão escritos na mão em `t2_stub_manual/stub_manual.py`.
O stub pega uma chamada de alto nível (tipo `somar(7, 5)`), faz **marshalling** (vira JSON), coloca o **framing** (4 bytes com tamanho) e manda via TCP. Do outro lado, o skeleton recebe, faz **unmarshalling**, escolhe a função certa numa tabela (dispatch) e devolve a resposta.
Esses componentes existem para a aplicação não precisar “pensar em rede” o tempo todo: para o cliente, parece uma chamada local, mas por baixo tem serialização, transporte, parsing e tratamento de erros.
Quando a gente usa XML-RPC ou gRPC isso vem pronto: em `t1_xmlrpc/cliente_xmlrpc.py` o `ServerProxy` já é o stub, e em `t4_grpc/cliente_grpc.py` o `CalculadoraStub` cumpre o mesmo papel (só que com contrato `.proto`).


## 2) REST nao e RPC

O que eu senti na prática é que RPC e REST “pensam” diferente. No RPC (Tarefa 1), o cliente chama uma **ação** pelo nome, como `proxy.calcular("soma", 10, 3)` em `t1_xmlrpc/cliente_xmlrpc.py`. A interface fica parecida com uma biblioteca remota: métodos, parâmetros e retorno.
Já no REST (Tarefa 3), a ideia é trabalhar com **recursos**. Em `t3_rest/servidor_rest.py` eu não “chamo uma função”; eu acesso `/produtos` e uso verbos HTTP (`GET`, `POST`, `PUT`, `DELETE`) para listar, criar, atualizar e remover.
É por isso que o Fielding critica RPC sobre HTTP: muitas vezes vira só “HTTP como cano” para invocar método, enquanto REST exige **interface uniforme** e semântica clara nos verbos e nos **códigos de status**.
No meu código isso aparece bem: o cliente `t3_rest/cliente_rest.py` depende dos status `201 Created`, `400 Bad Request` e `404 Not Found` para entender o que aconteceu; no RPC a semântica do erro volta como exceção remota (ex.: `Fault`).


## 3) Evolucao de contrato (.proto vs REST)

No gRPC/Protobuf (Tarefa 4), a compatibilidade gira em torno das **tags** (os números dos campos). Então, para adicionar `unidade: string` em `RespostaCalculo` dentro de `t4_grpc/calculadora.proto`, eu colocaria um campo novo com um número novo (por exemplo `string unidade = 3;`) sem mexer nos campos antigos.
Com isso, clientes antigos que não sabem da `unidade` tendem a ignorar o que não conhecem, e clientes novos conseguem conversar com servidores que ainda não mandam esse campo. Ou seja, dá para evoluir sem quebrar todo mundo de uma vez.
Agora, mudar o tipo de `resultado` (de `double` para `string`) já é outra história: vira uma mudança “quebrante” (breaking change), porque muda a representação que as duas pontas esperam.
No REST (Tarefa 3) não tem um schema obrigatório no protocolo. Em geral, adicionar um campo novo em JSON é ok se o cliente for tolerante, mas isso depende muito de contrato “combinado” (documentação, testes, versionamento de API), não de um compilador como no `.proto`.


## 4) Escolha de tecnologia (externo vs interno)

Para parceiros externos (apps de terceiros), eu escolheria **REST/HTTP** como padrão, parecido com o que fiz em `t3_rest/servidor_rest.py`. O motivo é bem prático: todo mundo fala HTTP, é fácil de testar (Postman/curl), e se encaixa bem em infra web (API gateway, proxies, logs, monitoramento).
Para comunicação interna entre microserviços, eu iria de **gRPC** (como em `t4_grpc/servidor_grpc.py` e `t4_grpc/cliente_grpc.py`), principalmente pelo desempenho (HTTP/2 + Protobuf) e pelo **contrato tipado** do `.proto`, que reduz mal-entendidos entre equipes.
Além disso, o gRPC dá um modelo de erro mais estruturado via status (ex.: `INVALID_ARGUMENT`), o que ajuda bastante em integração interna.
No fim, a combinação faz sentido (e bate com `t5_comparativo/comparativo.py`): REST na borda/publico e gRPC dentro da malha interna.


## 5) Conexao com Labs anteriores (transparencia x armadilhas)

O RPC dá uma sensação forte de **transparência**: em `t1_xmlrpc/cliente_xmlrpc.py` e `t4_grpc/cliente_grpc.py` eu chamo métodos como se fossem locais, mas por trás tem rede, latência variável, serialização e possibilidade de falhas parciais.
O problema é que isso pode enganar no design. Um exemplo clássico: colocar chamada remota dentro de um loop (fazendo N chamadas), achando que “é só uma função”, e aí o desempenho desaba por causa de round-trips e overhead.
Também tem a parte de falhas: em rede existe timeout, indisponibilidade, e às vezes retry. Isso muda a forma de pensar idempotência e efeitos colaterais (o servidor pode receber a mesma operação mais de uma vez).
Então, a transparência é boa para produtividade, mas precisa vir acompanhada de cuidados típicos de distribuídos: timeouts bem definidos, tratamento de erros (`Fault`/`RpcError`) e evitar granularidade fina demais nas chamadas.
