import grpc
import calculadora_pb2
import calculadora_pb2_grpc


def main(porta: int = 50051):
    with grpc.insecure_channel(f"localhost:{porta}") as canal:
        stub = calculadora_pb2_grpc.CalculadoraStub(canal)

        print("=== Chamadas gRPC para o servico Calculadora ===\n")

        saude = stub.VerificarSaude(calculadora_pb2.RequisicaoSaude())
        print(f"  Status: {saude.status} | Versao: {saude.versao}\n")

        chamadas = [
            ("soma", 10.0, 3.0),
            ("subtracao", 10.0, 3.0),
            ("multiplicacao", 4.0, 7.0),
            ("divisao", 22.0, 7.0),
        ]
        for op, a, b in chamadas:
            req = calculadora_pb2.RequisicaoCalculo(operacao=op, a=a, b=b)
            try:
                resp = stub.Calcular(req)
                print(f"  {resp.descricao}")
            except grpc.RpcError as e:
                print(f"  Erro gRPC [{e.code()}]: {e.details()}")

        print("\n  Testando divisao por zero:")
        try:
            stub.Calcular(
                calculadora_pb2.RequisicaoCalculo(operacao="divisao", a=10.0, b=0.0)
            )
        except grpc.RpcError as e:
            print(f"  Erro capturado: [{e.code()}] {e.details()}")

        print("\n  Testando operacao invalida ('raiz_quadrada'):")
        try:
            stub.Calcular(
                calculadora_pb2.RequisicaoCalculo(
                    operacao="raiz_quadrada", a=9.0, b=0.0
                )
            )
        except grpc.RpcError as e:
            print(f"  Erro capturado: [{e.code()}] {e.details()}")


if __name__ == "__main__":
    try:
        main()
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            print("Servidor nao disponivel.")
            print("Execute primeiro: python servidor_grpc.py")
