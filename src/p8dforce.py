import re
import sys

def compile_p8d(source_path):
    with open(source_path, 'r') as f:
        source = f.read()

    # 1. 提取铭牌 (Machine Plate)
    hatches = re.findall(r'8\[H(\d):(.*?)\]D', source)
    logic = re.sub(r'8\[H\d:.*?\]D|//.*', '', source).strip()

    # 2. 词法拆解 (Tokenization)
    token_re = r'(~~|~)?(8[=\.]*[D>\}]|<[=\.]*8|8\*D|8\[=*\]D|8\{)(~~|~)?'
    tokens = re.findall(token_re, logic)

    # 3. 核心预处理：计算逻辑空腔跳转地址 (Jump Map)
    jump_map = {}
    stack = []
    for i, (_, body, _) in enumerate(tokens):
        if body == "8{":
            stack.append(i)
        elif body == "}D":
            if not stack: raise SyntaxError("空腔闭合异常: }D 缺少匹配的 8{")
            start = stack.pop()
            jump_map[start] = i
            jump_map[i] = start

    # 4. 生成 C 代码
    c_code = [
        "#include <stdio.h>\n#include <stdlib.h>",
        "unsigned char m[65536] = {0};",
        "unsigned int ptr = 0, pc = 0;",
        "FILE* h[10] = {NULL}; int cur = 0;",
        "int main() {"
    ]

    # 初始化轨道
    for hid, path in hatches:
        mode = "rb" if int(hid) == 0 else "wb"
        c_code.append(f'    h[{hid}] = fopen("{path}", "{mode}");')

    c_code.append(f"    while(pc < {len(tokens)}) {{")
    c_code.append("        switch(pc) {")

    # 5. 指令转译逻辑
    for i, (prefix, body, suffix) in enumerate(tokens):
        instr = []
        
        # --- 前缀吸入 ---
        if prefix == "~~":
            instr.append("m[ptr] = (h[cur]) ? fgetc(h[cur]) : 0; if(m[ptr]==255) m[ptr]=0;")
        elif prefix == "~":
            instr.append("m[ptr] = getchar();")

        # --- 机体动作 ---
        if "8[" in body: # 换挡
            instr.append(f"cur = {body.count('=')};")
        elif "8*" in body: # 动态弹射 (自举核心)
            instr.append("pc = m[ptr]; continue;")
        elif body == "8{": # 腔体开启
            instr.append(f"if(!m[ptr]) {{ pc = {jump_map[i]}; continue; }}")
        elif body == "}D": # 腔体封闭
            instr.append(f"if(m[ptr]) {{ pc = {jump_map[i]}; continue; }}")
        elif "8" in body and "D" in body: # 压力操作
            v = body.count('=') - body.count('.')
            if v != 0: instr.append(f"m[ptr] += {v};")
        elif ">" in body: # 右推
            instr.append(f"ptr = (ptr + {body.count('=')+1}) % 65536;")
        elif "<" in body: # 左溯
            instr.append(f"ptr = (ptr - {body.count('=')+1} + 65536) % 65536;")

        # --- 后缀灌注 ---
        if suffix == "~~":
            instr.append("if(h[cur]) { fputc(m[ptr], h[cur]); fflush(h[cur]); }")
        elif suffix == "~":
            instr.append("putchar(m[ptr]);")

        c_code.append(f"            case {i}: {' '.join(instr)} pc++; break;")

    c_code.append("        }\n    }")
    c_code.append("    for(int i=0; i<10; i++) if(h[i]) fclose(h[i]);\n    return 0;\n}")
    
    return "\n".join(c_code)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(compile_p8d(sys.argv[1]))
