import random
import urllib.request
import argparse
import cowsay


def bullscows(guess: str, secret: str) -> (int, int):
    bulls, cows = 0, 0
    for i, j in zip(guess, secret):
        if i == j:
            bulls += 1
    secret_list = list(secret)
    for i in guess:
        if i in secret_list:
            secret_list.remove(i)
            cows += 1
    return bulls, cows


def gameplay(ask: callable, inform: callable, words: list[str]) -> int:
    secret = random.choice(words)
    ask_num = 0
    bulls = 0
    while bulls != len(secret):
        bulls, cows = bullscows(ask("Введите слово", words), secret)
        inform("Быки: {}, Коровы: {}", bulls, cows)
        ask_num += 1
    return ask_num


def ask(prompt: str, valid: list[str] = None) -> str:
    global my_cow
    prompt = cowsay.cowsay(prompt, cowfile=my_cow)
    if not valid:
        print(prompt)
        return input()
    while True:
        print(prompt)
        if (inp := input()) in valid:
            return inp


def inform(format_string: str, bulls: int, cows: int) -> None:
    print(cowsay.cowsay(format_string.format(bulls, cows), cow=random.choice(cowsay.list_cows())))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='bullscows', description='Terminal game "Bulls and cows"')
    parser.add_argument('dictionary', help="words that are used for the game")
    parser.add_argument('length', nargs='?', type=int, help="length of word")
    args = parser.parse_args()
    try:
        with open(args.dictionary) as f_inp:
            words = f_inp.read().split()
    except OSError:
        with urllib.request.urlopen(args.dictionary) as f_inp:
            words = f_inp.read().decode('utf-8').split()

    if args.length is not None:
        words = list(filter(lambda a: len(a) == args.length, words))

    with open('fox.cow') as f_inp:
        my_cow = cowsay.read_dot_cow(f_inp)
    
    print(gameplay(ask, inform, words))

