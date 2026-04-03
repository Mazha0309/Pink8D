import pickle
import sys

def run_ejac(file_path):
    with open(file_path, 'rb') as f:
        bytecode = pickle.load(f)

    mem = [0] * 30000
    ptr = 0
    pc = 0
    
    loop_map = {}
    stack = []
    for i, (op, val) in enumerate(bytecode):
        if op == 0x05: stack.append(i) # OPEN
        elif op == 0x06:
            start = stack.pop()
            loop_map[start] = i
            loop_map[i] = start

    while pc < len(bytecode):
        op, val = bytecode[pc]
        if op == 0x01: mem[ptr] = (mem[ptr] + val) % 256
        elif op == 0x02: mem[ptr] = (mem[ptr] - val) % 256
        elif op == 0x03: ptr = (ptr + val) % 30000
        elif op == 0x04: ptr = (ptr - val) % 30000
        elif op == 0x07: sys.stdout.write(chr(mem[ptr])); sys.stdout.flush()
        elif op == 0x08: 
            char = sys.stdin.read(1)
            mem[ptr] = ord(char) if char else 0
        elif op == 0x05 and mem[ptr] == 0: pc = loop_map[pc]
        elif op == 0x06 and mem[ptr] != 0: pc = loop_map[pc]
        elif op == 0x09: ptr = mem[ptr] % 30000
        pc += 1

if __name__ == "__main__":
    run_ejac(sys.argv[1])
