import sys

def run_vm(bytecode):
    mem = [0] * 65536
    ptr = 0
    pc = 0
    
    # 预加载循环索引
    stack, loops = [], {}
    i = 0
    while i < len(bytecode):
        op = bytecode[i] & 0x7F
        if op == 0x01: stack.append(i)
        elif op == 0x02:
            start = stack.pop()
            loops[start], loops[i] = i, start
        if op in [0x04, 0x05, 0x06, 0x07]: i += 1 # 跳过操作数
        i += 1

    while pc < len(bytecode):
        raw_op = bytecode[pc]
        op = raw_op & 0x7F
        eject = raw_op & 0x80
        
        if op == 0x01: # 8{
            if mem[ptr] == 0: pc = loops[pc]
        elif op == 0x02: # }D
            if mem[ptr] != 0: pc = loops[pc]
        elif op == 0x03: # ~
            mem[ptr] = ord(sys.stdin.read(1))
        else:
            pc += 1
            val = bytecode[pc]
            if op == 0x04: mem[ptr] = (mem[ptr] + val) % 256 # ADD
            elif op == 0x05: mem[ptr] = (mem[ptr] - val) % 256 # SUB
            elif op == 0x06: ptr = (ptr + val) % len(mem) # MOV_R
            elif op == 0x07: ptr = (ptr - val) % len(mem) # MOV_L
            
            if eject: print(chr(mem[ptr]), end='', flush=True)
        pc += 1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "rb") as f: run_vm(f.read())