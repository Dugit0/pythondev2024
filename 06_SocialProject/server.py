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
    print("New unregistered user")
    while not reader.at_eof():
        cmd = await reader.readline()
        print(f"New cmd {cmd}")
        cmd = cmd.decode().strip() 
        prefix, cmd = cmd[:10], cmd[10:]
        cmd = shlex.split(cmd)
        match cmd:
            case ['who']:
                print("Unregistered who")
                writer.write((prefix + ' '.join(who()) + '\n').encode())
                await writer.drain()
            case ['cows']:
                print("Unregistered cows")
                writer.write((prefix + ' '.join(cows()) + '\n').encode())
                await writer.drain()
            case ['login', cowname]:
                print("Unregistered login")
                if cowname not in cows():
                    writer.write(f'{prefix}Incorrect name\n'.encode())
                    await writer.drain()
                else:
                    me = cowname
                    writer.write(f'{prefix}Succes login!\n'.encode())
                    await writer.drain()
                    break
            case ['quit']:
                print("Unregistered quit")
                writer.write(f'{prefix}\n'.encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                return
            case _:
                writer.write(f'{prefix}Unknown command\n'.encode())
                await writer.drain()
    
    # Registered user cmd parce
    async def parce_command(cmd):
        global clients
        nonlocal me, reader, writer, send, receive, flag_quit
        print(f"{cmd = }")
        prefix, cmd = cmd[:10], cmd[10:]
        print(f"{prefix = }{cmd = }")
        cmd = shlex.split(cmd)
        print(f"{cmd = }")
        match cmd:
            case ['who']:
                print(f"{me} who")
                writer.write((prefix + ' '.join(who()) + '\n').encode())
                await writer.drain()
            case ['cows']:
                print(f"{me} cows")
                writer.write((prefix + ' '.join(cows()) + '\n').encode())
                await writer.drain()
            case ['login', cowname]:
                print(f"{me} login")
                writer.write(f'{prefix}You are already logged in\n'.encode())
                await writer.drain()
            case ['say', cowname, message]:
                print(f"{me} say {cowname} {message}")
                if cowname not in who():
                    writer.write(f'{prefix}{cowname} is not logged in\n'.encode())
                    await writer.drain()
                else:
                    writer.write(f'{prefix}\n'.encode())
                    await writer.drain()
                    await clients[cowname].put(cowsay.cowsay(message, cow=me))
            case ['yield', message]:
                print(f"{me} yield {message}")
                for other in who():
                    if other is not me:
                        await clients[other].put(cowsay.cowsay(message, cow=me))
                writer.write(f'{prefix}\n'.encode())
                await writer.drain()
            case ['quit']:
                print(f"{me} quit")
                send.cancel()
                receive.cancel()
                del clients[me]
                writer.write(f'{prefix}\n'.encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                flag_quit = True
                return
            case _:
                writer.write(f'{prefix}Unknown command\n'.encode())
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
                prefix = '0'*10
                writer.write(f"{prefix}{q.result()}\n".encode())
                await writer.drain()
        if flag_quit:
            break

async def main():
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())
