import sys

def run_vm(bin_path):
    with open(bin_path, 'rb') as f: code = f.read()
    m, ptr, pc, cur = bytearray(65536), 0, 0, 0
    # 模拟 H0/H1，实际应由 header 定义
    hatches = {0: sys.stdin.buffer, 1: sys.stdout.buffer} 

    while pc < len(code):
        io = code[pc]
        op = code[pc+1]
        val = code[pc+2]
        
        # --- IO 吸入 (前 4 位) ---
        pre = io >> 4
        if pre == 1: m[ptr] = ord(sys.stdin.read(1) or '\0')
        elif pre == 2: m[ptr] = hatches[0].read(1)[0] if 0 in hatches else 0

        # --- 执行 OP ---
        if op == 0x03: m[ptr] = (m[ptr] + val) % 256 # 压力操作
        elif op == 0x04: ptr = (ptr + val) % 65536 # 右移
        elif op == 0x05: ptr = (ptr - val + 65536) % 65536 # 左移
        elif op == 0x06: cur = val # 换挡
        elif op == 0x07: pc = m[ptr] * 3; continue # 动态弹射 (3字节对齐)

        # --- IO 灌注 (后 4 位) ---
        suf = io & 0x0F
        if suf == 1: sys.stdout.write(chr(m[ptr])); sys.stdout.flush()
        elif suf == 2: hatches[1].write(bytes([m[ptr]])); hatches[1].flush()
        
        pc += 3 # 指令步进

if __name__ == "__main__": run_vm(sys.argv[1])
