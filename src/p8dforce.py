import sys
import re
import shutil
import subprocess

def compile_to_c(source_code):
    # 初始化 C 语言模板
    # 利用 unsigned char 和 unsigned short 的天然溢出特性，完美模拟活塞环绕
    c_code = """#include <stdio.h>

unsigned char m[65536] = {0};
unsigned short ptr = 0;

int main() {
"""
    # 核心形态学正则 (兼容即时喷射)
    pattern = r'8[=.]*D~?|8[=]*>~?|<[=]*8~?|8\{|\}D|~'
    tokens = re.findall(pattern, source_code)

    for token in tokens:
        # 判定是否带有即时喷射后缀
        eject = token.endswith('~')
        cmd = token[:-1] if eject else token

        if cmd.startswith('8') and cmd.endswith('D') and '{' not in cmd and '}' not in cmd:
            # 赋值指令
            eq_count = cmd.count('=')
            dot_count = cmd.count('.')
            val = eq_count - dot_count
            if val > 0:
                c_code += f"    m[ptr] += {val};\n"
            elif val < 0:
                c_code += f"    m[ptr] -= {abs(val)};\n"
        
        elif cmd.startswith('8') and cmd.endswith('>'):
            # 右向位移
            dist = cmd.count('=') + 1
            c_code += f"    ptr += {dist};\n"
            
        elif cmd.startswith('<') and cmd.endswith('8'):
            # 左向回溯
            dist = cmd.count('=') + 1
            c_code += f"    ptr -= {dist};\n"
            
        elif cmd == '8{':
            # 空腔开启
            c_code += "    while(m[ptr]) {\n"
            
        elif cmd == '}D':
            # 空腔封闭
            c_code += "    }\n"
            
        elif cmd == '~':
            # 单独吸入
            c_code += "    m[ptr] = getchar();\n"

        # 触发即时喷射
        if eject:
            c_code += "    putchar(m[ptr]);\n"

    c_code += """
    return 0;
}
"""
    return c_code

def main():
    if len(sys.argv) < 2:
        print("⚙️ Usage: python3 p8dforce.py <source.8d> [-c/--c-only]")
        sys.exit(1)

    source_file = sys.argv[1]
    c_only = len(sys.argv) > 2 and sys.argv[2] in ['-c', '--c-only']

    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"❌ Piston Jammed: File '{source_file}' not found.")
        sys.exit(1)

    # 1. 转译为 C 代码
    c_code = compile_to_c(source)

    # 如果用户只想要 C 源码（比如为了调试）
    if c_only:
        print(c_code)
        sys.exit(0)

    # 2. 自动嗅探工业级编译器 (优先 clang)
    compiler = "clang" if shutil.which("clang") else ("gcc" if shutil.which("gcc") else None)
    
    if not compiler:
        print("⚠️ No clang or gcc detected! Ejecting C code instead:")
        print(c_code)
        sys.exit(1)

    out_bin = source_file.rsplit('.', 1)[0]
    # Windows 环境下加上 .exe 后缀
    if sys.platform == "win32":
        out_bin += ".exe"
        
    print(f"⚙️ Force Ejecting with {compiler} (-O3)...")
    
    # 3. 管道直压编译，不产生临时 .c 文件
    process = subprocess.Popen(
        [compiler, "-x", "c", "-O3", "-", "-o", out_bin],
        stdin=subprocess.PIPE
    )
    process.communicate(input=c_code.encode('utf-8'))

    if process.returncode == 0:
        print(f"🚀 Success! Logic injected into: {out_bin}")
    else:
        print("❌ Compilation jammed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
