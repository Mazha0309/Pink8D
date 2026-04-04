import sys
import re
import os

def run_p8d(file_path):
    if not os.path.exists(file_path):
        print(f"Error: Script {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()

    # 1. 工业级 Token 扫描器 (匹配所有活塞指令)
    # 涵盖：轨道声明、轨道切换、IO吸入/灌注、压力调节、循环判定、指针位移
    pattern = r'8\[H\d:.*?\]D|8\[[=]*\]D|~~8D|8D~~|8[=.]*D|8\{|\}D|~|8>|8<'
    tokens = re.findall(pattern, source)

    # 2. 预扫描：建立跳转表 (解决 KeyError)
    jmp = {}
    stack = []
    for i, token in enumerate(tokens):
        if token == "8{":
            stack.append(i)
        elif token == "}D":
            if stack:
                start = stack.pop()
                jmp[start] = i
                jmp[i] = start
            else:
                print(f"Error: Orphaned }}D at index {i}")
                return

    # 3. 运行环境初始化 (虚拟机状态)
    m = [0] * 65536  # 64KB 内存空间
    ptr = 0          # 内存指针
    pc = 0           # 指令指针
    hatches = {}     # 文件轨道句柄池 (H0, H1...)
    current_hatch = None

    # 4. 指令执行循环
    while pc < len(tokens):
        token = tokens[pc]

        # --- 轨道声明 8[H0:filename]D ---
        if "H" in token and ":" in token:
            match = re.search(r'H(\d):(.*)\]', token)
            if match:
                h_idx, h_path = match.groups()
                # H0 默认为输入 (rb)，其他为输出 (wb)
                mode = 'rb' if h_idx == '0' else 'wb'
                try:
                    hatches[h_idx] = open(h_path, mode)
                    # 【工业预载】如果是 H0，初始化时先吸一口流体
                    if h_idx == '0':
                        char = hatches[h_idx].read(1)
                        m[ptr] = ord(char) if char else 0
                except Exception as e:
                    print(f"Hatch Error: {e}")

        # --- 轨道切换 8[]D, 8[=]D, 8[==]D ---
        elif token.startswith("8[") and token.endswith("]D") and ":" not in token:
            # 统计中间 '=' 的数量作为索引 (0, 1, 2...)
            idx = str(token.count('='))
            current_hatch = hatches.get(idx)

        # --- 灌注动作 8D~~ (fputc) ---
        elif token == "8D~~":
            if current_hatch and 'w' in current_hatch.mode:
                current_hatch.write(bytes([m[ptr]]))
                current_hatch.flush() # 立即排气，确保数据写入磁盘

        # --- 吸入动作 ~~8D (fgetc) ---
        elif token == "~~8D":
            if current_hatch and 'r' in current_hatch.mode:
                char = current_hatch.read(1)
                m[ptr] = ord(char) if char else 0

        # --- 终端标准吸入 ~ ---
        elif token == "~":
            char = sys.stdin.read(1)
            m[ptr] = ord(char) if char else 0

        # --- 指针位移 8> / 8< ---
        elif token == "8>":
            ptr = (ptr + 1) % 65536
        elif token == "8<":
            ptr = (ptr - 1) % 65536

        # --- 压力增减 8===D / 8...D ---
        elif token.startswith("8") and token.endswith("D") and ("=" in token or "." in token):
            diff = token.count('=') - token.count('.')
            m[ptr] = (m[ptr] + diff) % 256

        # --- 循环逻辑 8{ / }D ---
        elif token == "8{":
            if m[ptr] == 0:
                pc = jmp[pc]  # 压力为0，直接跳到出口
        elif token == "}D":
            if m[ptr] != 0:
                pc = jmp[pc]  # 还有残压，回卷到入口

        pc += 1

    # 5. 关闭所有阀门，清理现场
    for h in hatches.values():
        h.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_p8d(sys.argv[1])
    else:
        print("Usage: python3 p8d.py <script.8d>")
