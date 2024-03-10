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

    def _compl_cow_saythink(self, text, line, begidx, endidx):
        params = {'message', 'cow', 'eyes', 'tongue'}
        splited_line = shlex.split(line)
        if len(shlex.split(line[:endidx] + '.')) % 2 == 0:
            # New argument
            return [c for c in (params - (set(splited_line[1::2]) & params)) if c.startswith(text)]
        else:
            # Complete last argument
            last_arg = shlex.split(line[:endidx] + '.')[-2]
            match last_arg:
                case 'cow':
                    return [c for c in cowsay.list_cows() if c.startswith(text)]
                case 'eyes':
                    return [c for c in ['==', 'XX', '--', 'OO', '@@'] if c.startswith(text)]
                case 'tongue':
                    return [c for c in ['U ', 'UU', 'YY'] if c.startswith(text)]

    def complete_cowsay(self, text, line, begidx, endidx):
        return self._compl_cow_saythink(text, line, begidx, endidx)
    
    def complete_cowthink(self, text, line, begidx, endidx):
        return self._compl_cow_saythink(text, line, begidx, endidx)


if __name__ == "__main__":
    cow_cmd().cmdloop()

