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
    return clients.keys()

def cows():
    return sorted(list(set(cowsay.list_cows()) - set(who())))

async def chat(reader, writer):
    me = "{}:{}".format(*writer.get_extra_info('peername'))
    print(me)
    flag_reg = False
    while not reader.at_eof():
        cmd = await reader.readline()
        match cmd.decode().strip():
            case 'who':
                recv = ' '.join(who()) + '\n'
                writer.write(recv.encode())
                await writer.drain()
            case 'cows':
                recv = ' '.join(cows()) + '\n'
                writer.write(recv.encode())
                await writer.drain()
            case 'quit':
                print(me, "DONE")
                writer.close()
                await writer.wait_closed()
                break
            case _:
                print(cmd)
                writer.write(cmd)
                await writer.drain()
    print('End', me)


    # read_cmd = asyncio.create_task(reader.readline())

    # me = "{}:{}".format(*writer.get_extra_info('peername'))
    # print(me)
    # clients[me] = asyncio.Queue()
    # send = asyncio.create_task(reader.readline())
    # receive = asyncio.create_task(clients[me].get())
    # while not reader.at_eof():
    #     done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)
    #     for q in done:
    #         if q is send:
    #             send = asyncio.create_task(reader.readline())
    #             for out in clients.values():
    #                 if out is not clients[me]:
    #                     await out.put(f"{me} {q.result().decode().strip()}")
    #         elif q is receive:
    #             receive = asyncio.create_task(clients[me].get())
    #             writer.write(f"{q.result()}\n".encode())
    #             await writer.drain()
    # send.cancel()
    # receive.cancel()
    # print(me, "DONE")
    # del clients[me]
    # writer.close()
    # await writer.wait_closed()

async def main():
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())
