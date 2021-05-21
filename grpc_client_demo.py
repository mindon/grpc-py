import sys
import grpc

sys.path.append("./proto")
import task_pb2_grpc, task_pb2

_HOST = '127.0.0.1'
_PORT = '50051'

def main():
  with grpc.insecure_channel("{0}:{1}".format(_HOST, _PORT)) as channel:
    client = task_pb2_grpc.TaskStub(channel=channel)

    resp = client.Run(task_pb2.TaskRequest(func="world", name="hello", input="<mindon.lab>"))
    print("received: {} {} - {}".format(resp.output, resp.error, resp.stop_at - resp.start_at))

if __name__ == '__main__':
  main()


# https://chai2010.cn/advanced-go-programming-book/ch4-rpc/ch4-05-grpc-hack.html

# with open('roots.pem', 'rb') as f:
#     creds = grpc.ssl_channel_credentials(f.read())
# channel = grpc.secure_channel('myservice.example.com:443', creds)
# stub = helloworld_pb2.GreeterStub(channel)


# server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
# with open('key.pem', 'rb') as f:
#     private_key = f.read()
# with open('chain.pem', 'rb') as f:
#     certificate_chain = f.read()
# server_credentials = grpc.ssl_server_credentials( ( (private_key, certificate_chain), ) )
# # Adding GreeterServicer to server omitted
# server.add_secure_port('myservice.example.com:443', server_credentials)
# server.start()


# creds, _ := credentials.NewClientTLSFromFile(certFile, "")
# conn, _ := grpc.Dial("localhost:50051", grpc.WithTransportCredentials(creds))
# // error handling omitted
# client := pb.NewGreeterClient(conn)


# creds, _ := credentials.NewServerTLSFromFile(certFile, keyFile)
# s := grpc.NewServer(grpc.Creds(creds))
# lis, _ := net.Listen("tcp", "localhost:50051")
# // error handling omitted
# s.Serve(lis)


# conn, _ := grpc.Dial("localhost:50051", grpc.WithInsecure())
# // error handling omitted
# client := pb.NewGreeterClient(conn)
# // ...

# s := grpc.NewServer()
# lis, _ := net.Listen("tcp", "localhost:50051")
# // error handling omitted
# s.Serve(lis)
