import re
import sys

def execute_p8d(source):
    # 匹配 8...D~, 8===>~, <===8~, 8{, }D, ~
    tokens = re.findall(r'8[=.]*D~?|8[=]*>~?|<[=]*8~?|8\{|\}D|~', source)
    mem = [0] * 30000
    ptr = 0
    pc = 0
    
    # 预处理循环
    stack = []
    loops = {}
    for i, t in enumerate(tokens):
        if t == "8{": stack.append(i)
        elif t == "}D":
            start = stack.pop()
            loops[start] = i
            loops[i] = start

    while pc < len(tokens):
        t = tokens[pc]
        has_eject = t.endswith('~')
        cmd = t.rstrip('~')

        # 位移逻辑
        if cmd.startswith('8') and cmd.endswith('>'):
            ptr = (ptr + cmd.count('=') + 1) % len(mem)
            if has_eject: print(chr(mem[ptr]), end='', flush=True)
        elif cmd.startswith('<') and cmd.endswith('8'):
            ptr = (ptr - (cmd.count('=') + 1)) % len(mem)
            if has_eject: print(chr(mem[ptr]), end='', flush=True)
            
        # 赋值逻辑
        elif cmd.startswith('8') and cmd.endswith('D'):
            core = cmd[1:-1]
            mem[ptr] = (mem[ptr] + core.count('=') - core.count('.')) % 256
            if has_eject: print(chr(mem[ptr]), end='', flush=True)
            
        # 基础 IO 与循环
        elif t == "~":
            char = sys.stdin.read(1)
            mem[ptr] = ord(char) if char else 0
        elif t == "8{":
            if mem[ptr] == 0: pc = loops[pc]
        elif t == "}D":
            if mem[ptr] != 0: pc = loops[pc]
            
        pc += 1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f: execute_p8d(f.read())