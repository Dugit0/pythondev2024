import sys
import argparse
import cowsay

# cowsay [-e eye_string] [-f cowfile] [-h] [-l] [-n] [-T tongue_string] [-W column] [-bdgpstwy]

parser = argparse.ArgumentParser(prog='cowsay', description='configurable speaking/thinking cow (and a bit more)')
parser.add_argument('-e', metavar='eye_string')
parser.add_argument('-f', metavar='cowfile')
parser.add_argument('-l', action='store_true')
parser.add_argument('-n', action='store_true')
parser.add_argument('-T', metavar='tongue_string')
parser.add_argument('-W', metavar='column', type=int)

# -bdgpstwy
# В оригинальном cowsay эти опции не взаимоисключающие, однако используемой библиотеке невозможно полностью имитировать особенности исходной реализации
group = parser.add_mutually_exclusive_group()
group.add_argument("-b", action="store_true")
group.add_argument("-d", action="store_true")
group.add_argument("-g", action="store_true")
group.add_argument("-p", action="store_true")
group.add_argument("-s", action="store_true")
group.add_argument("-t", action="store_true")
group.add_argument("-w", action="store_true")
group.add_argument("-y", action="store_true")

parser.add_argument('message', nargs='?')

# cowsay.cowsay()
args = parser.parse_args()

# List cows
if args.l:
    print(*cowsay.list_cows(), sep='\n')
    sys.exit(0)

eyes = args.e if args.e is not None else cowsay.Option.eyes
cow = args.f if args.f is not None else 'default'
tongue = args.T if args.T is not None else cowsay.Option.tongue
width = args.W if args.W is not None else 40
message = args.message if args.message is not None else sys.stdin.read()

preset_template = "bdgpstwy"
preset = None
for c in preset_template:
    if getattr(args, c):
        preset = c
        break

if args.n:
    lines = message.split('\n')
    wrap_text = False
else:
    # В оригинальном cowsay добавляются лишние пробелы в начале сообщения, если подать на вход несколько символов '\n', но при этом корректно обрезаются в конце
    message = message.strip()
    message = "\n".join(([" ".join(line.split()) for line in message.split('\n')]))
    wrap_text = True

if cow in cowsay.list_cows():
    print(cowsay.cowsay(message, cow=cow, preset=preset, eyes=eyes, tongue=tongue, width=width, wrap_text=wrap_text))
else:
    with open(cow) as f_inp:
        custom_cow = cowsay.read_dot_cow(f_inp)
    print(cowsay.cowsay(message, preset=preset, eyes=eyes, tongue=tongue, width=width, wrap_text=wrap_text, cowfile=custom_cow))

