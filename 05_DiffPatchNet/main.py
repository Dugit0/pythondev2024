import asyncio
import cowsay
import shlex

"""
who — просмотр зарегистрированных пользователей
cows — просмотр свободных имён коров
login название_коровы — зарегистрироваться под именем название_коровы
say название_коровы текст сообщения — послать сообщение пользователю название_коровы
yield текст сообщения — послать сообщение всем зарегистрированным пользователям
quit — отключиться
"""

clients = {}

def who():
    global clients
    return sorted(list(clients.keys()))

def cows():
    return sorted(list(set(cowsay.list_cows()) - set(who())))

async def chat(reader, writer):
    global clients
    # Unregistered user loop
    while not reader.at_eof():
        cmd = await reader.readline()
        match shlex.split(cmd.decode().strip()):
            case ['who']:
                writer.write((' '.join(who()) + '\n').encode())
                await writer.drain()
            case ['cows']:
                writer.write((' '.join(cows()) + '\n').encode())
                await writer.drain()
            case ['login', cowname]:
                if cowname not in cows():
                    writer.write('Incorrect name\n'.encode())
                    await writer.drain()
                else:
                    me = cowname
                    break
            case ['quit']:
                writer.close()
                await writer.wait_closed()
                return
            case _:
                writer.write('Unknown command\n'.encode())
                await writer.drain()
    
    # Registered user cmd parce
    async def parce_command(cmd):
        global clients
        nonlocal me, reader, writer, send, receive, flag_quit
        match shlex.split(cmd):
            case ['who']:
                writer.write((' '.join(who()) + '\n').encode())
                await writer.drain()
            case ['cows']:
                writer.write((' '.join(cows()) + '\n').encode())
                await writer.drain()
            case ['login', cowname]:
                writer.write('You are already logged in\n'.encode())
                await writer.drain()
            case ['say', cowname, message]:
                if cowname not in who():
                    writer.write(f'{cowname} is not logged in\n'.encode())
                    await writer.drain()
                else:
                    await clients[cowname].put(cowsay.cowsay(message, cow=me))
            case ['yield', message]:
                for other in who():
                    if other is not me:
                        await clients[other].put(cowsay.cowsay(message, cow=me))
            case ['quit']:
                send.cancel()
                receive.cancel()
                del clients[me]
                writer.close()
                await writer.wait_closed()
                flag_quit = True
                return
            case _:
                writer.write('Unknown command\n'.encode())
                await writer.drain()

    # Registered user loop
    clients[me] = asyncio.Queue()
    flag_quit = False
    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(clients[me].get())
    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)
        for q in done:
            if q is send:
                send = asyncio.create_task(reader.readline())
                cmd = q.result().decode().strip()
                await parce_command(cmd)
                if flag_quit:
                    break
            elif q is receive:
                receive = asyncio.create_task(clients[me].get())
                writer.write(f"{q.result()}\n".encode())
                await writer.drain()
        if flag_quit:
            break

async def main():
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())
