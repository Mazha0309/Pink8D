import re, sys

def run_p8d(source_path):
    with open(source_path, 'r') as f: source = f.read()
    # 1. 轨道与逻辑分离
    hatches = {int(h): open(p, "rb" if int(h)==0 else "wb") for h, p in re.findall(r'8\[H(\d):(.*?)\]D', source)}
    logic = re.sub(r'8\[H\d:.*?\]D|//.*', '', source).strip()
    tokens = re.findall(r'(~~|~)?(8[=\.]*[D>\}]|<[=\.]*8|8\*D|8\[=*\]D|8\{)(~~|~)?', logic)

    # 2. 跳转预解析 (Jump Table)
    stack, jmp = [], {}
    for i, (_, body, _) in enumerate(tokens):
        if body == "8{": stack.append(i)
        elif body == "}D": start = stack.pop(); jmp[start], jmp[i] = i, start

    # 3. 运行环境
    m, ptr, pc, cur = [0]*65536, 0, 0, 0
    while pc < len(tokens):
        pre, body, suf = tokens[pc]
        # --- 吸入 ---
        if pre == "~~": m[ptr] = hatches[cur].read(1)[0] if cur in hatches else 0
        elif pre == "~": m[ptr] = ord(sys.stdin.read(1) or '\0')
        if pre and m[ptr] == 255: m[ptr] = 0 # EOF 处理

        # --- 动作 ---
        if "8[" in body: cur = body.count('=')
        elif "8*" in body: pc = m[ptr]; continue
        elif body == "8{" and m[ptr] == 0: pc = jmp[pc]
        elif body == "}D" and m[ptr] != 0: pc = jmp[pc]
        elif "8" in body and "D" in body: m[ptr] = (m[ptr] + body.count('=') - body.count('.')) % 256
        elif ">" in body: ptr = (ptr + body.count('=') + 1) % 65536
        elif "<" in body: ptr = (ptr - body.count('=') - 1) % 65536

        # --- 灌注 ---
        if suf == "~~": 
            if cur in hatches: hatches[cur].write(bytes([m[ptr]])); hatches[cur].flush()
        elif suf == "~": sys.stdout.write(chr(m[ptr])); sys.stdout.flush()
        pc += 1
    for f in hatches.values(): f.close()

if __name__ == "__main__": run_p8d(sys.argv[1])
