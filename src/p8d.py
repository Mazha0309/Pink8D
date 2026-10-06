import sys
import re
import os


def run_p8d(file_path):
    if not os.path.exists(file_path):
        print(f"Error: Script {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    # 1. 工业级 Token 扫描器 (匹配所有活塞指令)
    # 顺序必须从长到短，保证 ~~ 不会被拆成两个 ~：
    #   铭牌声明 -> 舱门切换 -> 强力流体 -> 压力(含喷射后缀) -> 位移(含喷射后缀)
    #   -> 动态弹射 -> 空腔 -> 标准吸入
    pattern = (
        r"8\[H\d:.*?\]D|8\[=*\]D|~~8D|8D~~|8[=.]*D~?|8[=]*>~?|<[=]*8~?|8\*D|8\{|\}D|~"
    )
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
    if stack:
        print(f"Error: Unclosed 8{{ at index {stack[-1]}")
        return

    # 3. 运行环境初始化 (虚拟机状态)
    m = [0] * 65536  # 64KB 内存空间，16-bit 压力值 (0-65535)
    ptr = 0  # 内存指针
    pc = 0  # 指令指针
    hatches = {}  # 文件轨道句柄池 (H0, H1...)
    current_hatch = None

    def eject():
        # 即时喷射：向 STDOUT 压入 1 字节 (取 16-bit 压力的低 8 位)
        sys.stdout.write(chr(m[ptr] & 0xFF))
        sys.stdout.flush()

    # 4. 指令执行循环
    while pc < len(tokens):
        token = tokens[pc]

        # --- 轨道声明 8[H0:filename]D ---
        if "H" in token and ":" in token:
            match = re.search(r"H(\d):(.*)\]", token)
            if match:
                h_idx, h_path = match.groups()
                # H0 默认为输入 (rb)，其他为输出 (wb)
                mode = "rb" if h_idx == "0" else "wb"
                try:
                    hatches[h_idx] = open(h_path, mode)
                    # 【工业预载】如果是 H0，初始化时先吸一口流体
                    if h_idx == "0":
                        current_hatch = hatches[h_idx]
                        char = hatches[h_idx].read(1)
                        m[ptr] = char[0] if char else 0
                except Exception as e:
                    print(f"Hatch Error: {e}")

        # --- 轨道切换 8[]D, 8[=]D, 8[==]D ---
        elif token.startswith("8[") and token.endswith("]D") and ":" not in token:
            # 统计中间 '=' 的数量作为索引 (0, 1, 2...)
            idx = str(token.count("="))
            current_hatch = hatches.get(idx)

        # --- 灌注动作 8D~~ (fputc) ---
        elif token == "8D~~":
            if current_hatch and "w" in current_hatch.mode:
                current_hatch.write(bytes([m[ptr] & 0xFF]))
                current_hatch.flush()  # 立即排气，确保数据写入磁盘

        # --- 吸入动作 ~~8D (fgetc) ---
        elif token == "~~8D":
            if current_hatch and "r" in current_hatch.mode:
                char = current_hatch.read(1)
                m[ptr] = char[0] if char else 0

        # --- 终端标准吸入 ~ ---
        elif token == "~":
            char = sys.stdin.read(1)
            m[ptr] = ord(char) if char else 0

        # --- 动态弹射 8*D：指令指针跳转到当前格存储的地址 (自举核心) ---
        elif token == "8*D":
            pc = m[ptr]
            continue

        # --- 循环逻辑 8{ / }D ---
        elif token == "8{":
            if m[ptr] == 0:
                pc = jmp[pc]  # 压力为0，直接跳到出口
        elif token == "}D":
            if m[ptr] != 0:
                pc = jmp[pc]  # 还有残压，回卷到入口

        else:
            # --- 位移与压力 (可能带 ~ 喷射后缀) ---
            eject_flag = token.endswith("~")
            cmd = token[:-1] if eject_flag else token

            if cmd.startswith("8") and cmd.endswith(">"):
                # 动力右喷：距离 = '=' 数量 + 1
                ptr = (ptr + cmd.count("=") + 1) % 65536
            elif cmd.startswith("<") and cmd.endswith("8"):
                # 动力左喷：距离 = '=' 数量 + 1
                ptr = (ptr - cmd.count("=") - 1) % 65536
            elif cmd.startswith("8") and cmd.endswith("D"):
                # 压力增减：值 = '=' 数量 - '.' 数量
                diff = cmd.count("=") - cmd.count(".")
                m[ptr] = (m[ptr] + diff) % 65536

            if eject_flag:
                eject()

        pc += 1

    # 5. 关闭所有阀门，清理现场
    for h in hatches.values():
        h.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_p8d(sys.argv[1])
    else:
        print("Usage: python3 p8d.py <script.8d>")
