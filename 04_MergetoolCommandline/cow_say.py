import sys
import argparse
import cowsay
import shlex
import cmd


class cow_cmd(cmd.Cmd):
    prompt = ">> "

    def do_list_cows(self, arg):
        "Print list of cows"
        print(*cowsay.list_cows(), sep='\n')

    def do_make_bubble(self, arg):
        "Make and print bubble"
        text = " ".join(shlex.split(arg))
        print(cowsay.make_bubble(text))

    def _cow_saythink(self, arg, say=True):
        args = shlex.split(arg)
        params = {'message': None,
                  'cow': 'default',
                  'eyes': cowsay.Option.eyes,
                  'tongue': cowsay.Option.tongue}
        i = 0
        while i < len(args):
            match args[i]:
                case 'message'|'cow'|'eyes'|'tongue' as par:
                    i += 1
                    try:
                        params[par] = args[i]
                    except IndexError:
                        print('Index out of range')
                        return 1
                case _:
                    print('Unexpected arg')
                    return 1
            i += 1
        if params['message'] is None:
            print('Message is required argument')
            return 1
        if params['cow'] not in cowsay.list_cows():
            print('Unexpected cow')
            return 1
        if say:
            return cowsay.cowsay(params['message'], cow=params['cow'], eyes=params['eyes'], tongue=params['tongue'])
        else:
            return cowsay.cowthink(params['message'], cow=params['cow'], eyes=params['eyes'], tongue=params['tongue'])

    def do_cowsay(self, arg):
        """
        Cow says
        Options:
            message <message> - message that the cow says
            cow <cow> - choose a cow picture to use; search in the list cows (see list_cows command)
            eyes <eye_string> - set a eye string
            tongue <tongue_string> - set a tongue string
        """
        print(self._cow_saythink(arg, True))

    def do_cowthink(self, arg):
        """
        Cow think
        Options:
            message <message> - message that the cow says
            cow <cow> - choose a cow picture to use; search in the list cows (see list_cows command)
            eyes <eye_string> - set a eye string
            tongue <tongue_string> - set a tongue string
        """
        print(self._cow_saythink(arg, False))

    def do_EOF(self, arg):
        "Finish program"
        return 1


if __name__ == "__main__":
    cow_cmd().cmdloop()


"""
# cowsay [-e eye_string] [-f cowfile] [-h] [-l] [-n] [-T tongue_string] [-W column] [-bdgpstwy]

parser = argparse.ArgumentParser(prog='cowsay', description='Configurable speaking cow (and a bit more).')
parser.add_argument('-e', metavar='eye_string', help="set a eye string")
parser.add_argument('-f', metavar='cowfile', help="specifies a particular cow picture file (cowfile) to use; by default search in the list cows (see -l option), if it is not found, then open it as a file")
parser.add_argument('-l', action='store_true', help="print list cowfiles")
parser.add_argument('-n', action='store_true', help="use for arbitrary messages with arbitrary whitespace; if it is specified, the given message will not be word-wrapped")
parser.add_argument('-T', metavar='tongue_string', help="set a tongue string")
parser.add_argument('-W', metavar='column', type=int, help="specifies roughly (where the message should be wrapped); the default is equivalent to -W 40 i.e. wrap words at or before the 40th column")

# -bdgpstwy
# В оригинальном cowsay эти опции не взаимоисключающие, однако используемой библиотеке невозможно полностью имитировать особенности исходной реализации
group = parser.add_argument_group("PRESETS", "Presets for eyes and tongue of cow")
exclusive_group = group.add_mutually_exclusive_group()
exclusive_group.add_argument("-b", action="store_true", help="Borg cow")
exclusive_group.add_argument("-d", action="store_true", help="dead cow")
exclusive_group.add_argument("-g", action="store_true", help="greedy cow")
exclusive_group.add_argument("-p", action="store_true", help="paranoia cow")
exclusive_group.add_argument("-s", action="store_true", help="stoned cow")
exclusive_group.add_argument("-t", action="store_true", help="tired cow")
exclusive_group.add_argument("-w", action="store_true", help="wired cow")
exclusive_group.add_argument("-y", action="store_true", help="youthful cow")

parser.add_argument('message', nargs='?', help="message that the cow says")

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
"""
