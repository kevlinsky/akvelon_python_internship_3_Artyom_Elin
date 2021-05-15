import sys


def fibonacci(n: int):
    a = 0
    b = 1
    for i in range(n):
        a, b = b, a + b
    return a


if __name__ == '__main__':
    args = sys.argv

    if len(args) != 3:
        arg = 'help'
    else:
        arg = args[2]

    if arg == 'help':
        print('Example: python utils.py fibonacci 13')
    else:
        try:
            arg = int(arg)
            print(fibonacci(arg))
        except ValueError:
            print('Example: python utils.py fibonacci 13')