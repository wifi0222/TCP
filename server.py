import socket
import threading

def handle_client(client_socket, client_address):
    print(f"与 {client_address} 建立连接")
    try:
        while True:
            # 接收数据
            data = client_socket.recv(1024)
            if not data:
                break

            # 解析报文
            type = int.from_bytes(data[:2], byteorder='big')
            if type == 1:  # Initialization
                N = int.from_bytes(data[2:6], byteorder='big')
                print(f"回复来自{client_address}的文本共{N}块.")
                # 发送agree报文
                agree_msg = bytearray()
                agree_msg = int(2).to_bytes(2, byteorder='big')
                client_socket.sendall(agree_msg)

            elif type == 3:  # reverseRequest
                length = int.from_bytes(data[2:6], byteorder='big')
                text = data[6:].decode('utf-8')
                reversed_text = text[::-1]  # 反转文本

                # 构建reverseAnswer报文
                answer_msg = bytearray()
                answer_msg += int(4).to_bytes(2, byteorder='big')
                answer_msg += len(reversed_text).to_bytes(4, byteorder='big')
                answer_msg += reversed_text.encode('utf-8')

                # 发送数据
                client_socket.sendall(answer_msg)
                #print(f"发送反转文本: {reversed_text}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print(f"与{client_address} 的连接关闭.")

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen()

    print("TCP服务器已启动，等待客户端连接...")

    try:
        while True:
            client_sock, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_sock, addr))
            client_thread.start()
    finally:
        server_socket.close()

if __name__ == '__main__':
    main()
