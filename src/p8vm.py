import sys
import os

def run_vm(bin_path):
    if not os.path.exists(bin_path): return
    with open(bin_path, 'rb') as f: code = f.read()

    m, ptr, pc, cur = bytearray(65536), 0, 0, 0
    hatches = {}

    # --- 1. 预扫描：构建 3 字节对齐跳转表 ---
    jmp = {}
    stack = []
    for i in range(0, len(code), 3):
        op = code[i+1]
        if op == 0x01: stack.append(i)
        elif op == 0x02 and stack:
            start = stack.pop()
            jmp[start], jmp[i] = i, start

    # --- 2. 运行内核 ---
    try:
        while pc < len(code):
            io, op, val = code[pc], code[pc+1], code[pc+2]

            # 前置吸入
            pre = io >> 4
            if pre == 1:
                char = sys.stdin.read(1)
                m[ptr] = ord(char) if char else 0
            elif pre == 2 and cur in hatches:
                data = hatches[cur].read(1)
                m[ptr] = data[0] if data else 0

            # 指令逻辑
            if op == 0x01: # 8{
                if m[ptr] == 0: pc = jmp[pc]
            elif op == 0x02: # }D
                if m[ptr] != 0: pc = jmp[pc]
            elif op == 0x03: m[ptr] = (m[ptr] + val) % 256 # 8D
            elif op == 0x04: ptr = (ptr + val) % 65536 # >
            elif op == 0x05: ptr = (ptr - val + 65536) % 65536 # <
            elif op == 0x06: # SEL & 自动引流
                cur = val
                if cur not in hatches:
                    if cur == 0: # 默认读 data.bin
                        if os.path.exists("data.bin"):
                            hatches[0] = open("data.bin", "rb")
                            # 工业预载：打开瞬间吸入首字节，确保 8{ 不为空
                            first = hatches[0].read(1)
                            m[ptr] = first[0] if first else 0
                    elif cur == 1: # 默认写 log.txt
                        hatches[1] = open("log.txt", "wb")
            elif op == 0x07: # JMP
                pc = m[ptr] * 3
                continue

            # 后置灌注
            suf = io & 0x0F
            if suf == 1:
                sys.stdout.write(chr(m[ptr]))
                sys.stdout.flush()
            elif suf == 2 and cur in hatches:
                hatches[cur].write(bytes([m[ptr]]))
                hatches[cur].flush()

            pc += 3
    finally:
        for h in hatches.values(): h.close()

if __name__ == "__main__":
    if len(sys.argv) > 1: run_vm(sys.argv[1])
