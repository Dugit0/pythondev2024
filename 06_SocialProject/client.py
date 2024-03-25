import cowsay
import os
import shlex
import cmd
import typing
import socket
import sys
import threading
import time
import readline

"""
who — просмотр зарегистрированных пользователей
cows — просмотр свободных имён коров
login название_коровы — зарегистрироваться под именем название_коровы
say название_коровы текст сообщения — послать сообщение пользователю название_коровы
yield текст сообщения — послать сообщение всем зарегистрированным пользователям
quit — отключиться

From/to server:

{num:010d}<Message>
0000000000<Message>

"""


response_pool = set()


class my_cmd(cmd.Cmd):
    prompt = ">> "
    
    def __init__(self, socket):
        self.socket = socket
        self.cmd_num = 1
        super().__init__()

    def emptyline(self):
        pass

    # def _send_cmd_to_serv(self, num, message):
    def _exec_cmd_to_serv(self, message):
        my_num = self.cmd_num
        new_command = f"{self.cmd_num:010d}{message}"
        self.socket.sendall(new_command.encode())
        self.cmd_num += 1
        while True:
            flag_break = False
            for i in response_pool:
                if i.startswith(f'{my_num:010d}'):
                    response = i
                    response_pool.remove(i)
                    flag_break = True
                    break
            if flag_break:
                break
        return response[10:]

    
    def do_who(self, arg):
        "List of registered users"
        print(self._exec_cmd_to_serv('who\n'))

    def do_cows(self, arg):
        print(self._exec_cmd_to_serv('cows\n'))

    def do_login(self, arg):
        responce = self._exec_cmd_to_serv(f'login {arg}\n')
        if responce:
            print(responce)

    def do_say(self, arg):
        responce = self._exec_cmd_to_serv(f'say {arg}\n')
        if responce:
            print(responce)

    def do_yield(self, arg):
        responce = self._exec_cmd_to_serv(f'yield {arg}\n')
        if responce:
            print(responce)

    def do_quit(self, arg):
        responce = self._exec_cmd_to_serv(f'quit\n')
        if responce:
            print(responce)
        return 1

    def complete_login(self, text, line, begidx, endidx):
        cmd_len = len(shlex.split(line[:endidx] + '.'))
        responce = self._exec_cmd_to_serv("cows\n")
        responce = shlex.split(responce)
        if cmd_len == 2:
            return [c for c in responce if c.startswith(text)]
    
    def complete_say(self, text, line, begidx, endidx):
        cmd_len = len(shlex.split(line[:endidx] + '.'))
        responce = self._exec_cmd_to_serv("who\n")
        responce = shlex.split(responce)
        if cmd_len == 2:
            return [c for c in responce if c.startswith(text)]


    def do_EOF(self, arg):
        "Finish program"
        return 1



def print_srv_message(socket, stop_event):
    global response_pool
    while not stop_event.wait(1):
        response = socket.recv(8192).rstrip().decode()
        if response.startswith("0"*10):
            print(response[10:])
        else:
            response_pool.add(response)


if __name__ == "__main__":
    host, port = "localhost", 1337
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        soc.connect((host, port))
        cmdline = my_cmd(soc)
        stop_event = threading.Event()
        printer = threading.Thread(target=print_srv_message, args=(soc, stop_event))
        printer.start()
        cmdline.cmdloop()
        stop_event.set()
        printer.join()


