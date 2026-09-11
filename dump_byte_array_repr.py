import sys


with open(sys.argv[1], 'rb') as f:
    data = f.read()

print(''.join(f'\\x{x:02x}' for x in data))