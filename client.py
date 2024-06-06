import socket
import random

def send_file(client_socket, file_content, lmin, lmax):
    # 计算块数
    chunks = []
    remaining_content = len(file_content)
    while remaining_content > 0:
        chunk_size = min(random.randint(lmin, lmax), remaining_content)
        chunks.append(chunk_size)
        remaining_content -= chunk_size
    N = len(chunks)

    # 发送Initialization报文
    init_msg = bytearray()
    init_msg += int(1).to_bytes(2, byteorder='big')
    init_msg += N.to_bytes(4, byteorder='big')
    client_socket.sendall(init_msg)

    # 接收agree报文
    agree_msg = client_socket.recv(1024)
    assert int.from_bytes(agree_msg[:2], byteorder='big') == 2

    # 发送reverseRequest报文并接收reverseAnswer报文
    reversed_chunks = []
    for i, chunk_size in enumerate(chunks):
        chunk = file_content[:chunk_size]
        file_content = file_content[chunk_size:]

        # 构建reverseRequest报文
        request_msg = bytearray()
        request_msg += int(3).to_bytes(2, byteorder='big')
        request_msg += len(chunk).to_bytes(4, byteorder='big')
        request_msg += chunk.encode('utf-8')

        # 发送数据
        client_socket.sendall(request_msg)

        # 接收数据
        answer_msg = client_socket.recv(1024)
        type = int.from_bytes(answer_msg[:2], byteorder='big')
        assert type == 4
        length = int.from_bytes(answer_msg[2:6], byteorder='big')
        reversed_text = answer_msg[6:6 + length].decode('utf-8')
        reversed_chunks.insert(0, reversed_text)
        print(f"第{i + 1}块: {reversed_text}")

    return ''.join(reversed_chunks)

def main():
    server_ip = input("请输入服务器IP: ")
    server_port = int(input("请输入服务器端口: "))

    # 创建客户端socket并设置超时
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(5)  # 设置5秒超时

    try:
        # 连接服务器
        client_socket.connect((server_ip, server_port))

        # 读取文件内容
        with open('textfile.txt', 'r', encoding='utf-8') as f:
            file_content = f.read()

        # 输入lmin和lmax
        lmin = int(input("请输入Lmin: "))
        lmax = int(input("请输入Lmax: "))

        # 发送文件并接收反转后的内容
        reversed_content = send_file(client_socket, file_content, lmin, lmax)

        # 保存反转后的内容到文件
        with open('reversed_file.txt', 'w', encoding='utf-8') as f:
            f.write(reversed_content)
    except socket.timeout:
        print("连接服务器超时")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        client_socket.close()

if __name__ == '__main__':
    main()
