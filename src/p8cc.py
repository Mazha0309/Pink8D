import re, sys

# Opcode 定义 (严格对应 v3 规范)
OPS = {
    "8{": 0x01,
    "}D": 0x02,
    "8D": 0x03,
    ">": 0x04,
    "<": 0x05,
    "SEL": 0x06,
    "JMP": 0x07,
    "NOP": 0x00,
}


def compile_to_bytecode(path):
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    pattern = (
        r"(~~|~)?(8\[H\d:.*?\]D|8\[=*\]D|8[=\.]*[D>]|8\*D|8\{|\}D|<[=\.]*8)(~~|~)?"
    )
    tokens = re.findall(pattern, source)

    binary = bytearray()
    for pre, body, suf in tokens:
        # 1. 前缀/后缀标志位：前缀作用在第一条指令之前，后缀作用在最后一条之后
        pre_bits = (1 if pre == "~" else 2 if pre == "~~" else 0) << 4
        suf_bits = 1 if suf == "~" else 2 if suf == "~~" else 0

        # 2. 把 body 展开为一条或多条 (opcode, operand) 指令
        insts = []
        if "8[H" in body:  # 轨道路径定义
            match = re.search(r"H(\d)", body)
            h_idx = int(match.group(1)) if match else 0
            insts.append((OPS["SEL"], h_idx))
        elif "8[" in body:  # 轨道切换
            insts.append((OPS["SEL"], body.count("=")))
        elif "8*" in body:  # 弹射跳转
            insts.append((OPS["JMP"], 0))
        elif body == "8{":
            insts.append((OPS["8{"], 0))
        elif body == "}D":
            insts.append((OPS["}D"], 0))
        elif "8" in body and "D" in body:
            # 压力调节 (16-bit 格；操作数为 8-bit 补码，超长行程自动拆分)
            val = body.count("=") - body.count(".")
            if val == 0:
                insts.append((OPS["8D"], 0))
            else:
                while val != 0:
                    step = max(-127, min(127, val))
                    insts.append((OPS["8D"], step & 0xFF))
                    val -= step
        elif ">" in body:  # 右移
            insts.append((OPS[">"], body.count("=") + 1))
        elif "<" in body:  # 左移
            insts.append((OPS["<"], body.count("=") + 1))
        else:
            # 这里的兜底非常重要，防止字节码对齐崩盘
            insts.append((OPS["NOP"], 0))

        # 3. 落盘：每条指令固定 3 字节 [io_flag, opcode, operand]
        for k, (op, val) in enumerate(insts):
            flag = 0
            if k == 0:
                flag |= pre_bits
            if k == len(insts) - 1:
                flag |= suf_bits
            binary.append(flag)
            binary.extend([op, val])

    output_path = path.replace(".8d", ".ejac")
    with open(output_path, "wb") as f:
        f.write(binary)
    print(f"🔩 Compiled: {path} -> {output_path} ({len(binary)} bytes)")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        compile_to_bytecode(sys.argv[1])
