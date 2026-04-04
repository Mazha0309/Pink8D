import sys
import re
import shutil
import subprocess

def compile_to_c(source_code):
    c_code = """#include <stdio.h>
#include <stdlib.h>

unsigned char m[65536] = {0};
unsigned short ptr = 0;
FILE* current_hatch = NULL;
FILE* h0 = NULL, *h1 = NULL, *h2 = NULL, *h3 = NULL;

int main() {
"""
    # 核心：正则顺序必须从长到短，防止 ~~ 被拆成 ~ 和 ~
    pattern = r'8\[H\d:.*?\]D|8\[=*\]D|~~8D|8D~~|8[=.]*D~?|8[=]*>~?|<[=]*8~?|8\{|\}D|8\*D|~'
    tokens = re.findall(pattern, source_code)

    for token in tokens:
        # 1. 铭牌声明 (8[H0:file]D)
        if 'H' in token and '[' in token:
            m_hatch = re.search(r'H(\d)', token).group(1)
            m_path = re.search(r':(.*?)\]', token).group(1)
            
            c_code += f"    h{m_hatch} = fopen(\"{m_path}\", \"rb+\");\n"
            c_code += f"    if (!h{m_hatch}) h{m_hatch} = fopen(\"{m_path}\", \"wb+\");\n"
            

            if m_hatch == '0':
                c_code += "    current_hatch = h0;\n"
                c_code += "    if (h0) { int c = fgetc(h0); m[ptr] = (c == EOF) ? 0 : (unsigned char)c; }\n"
            continue

        # 2. 轨道切换 (8[=]D)
        elif re.match(r'8\[=*\]D', token):
            idx = token.count('=')
            c_code += f"    current_hatch = h{idx};\n"
            continue

        # 3. 强力吸入 (~~8D)
        elif token == '~~8D':
            c_code += "    if (current_hatch) { int c = fgetc(current_hatch); m[ptr] = (c == EOF) ? 0 : (unsigned char)c; }\n"
            continue

        # 4. 强力灌注 (8D~~) -> 写入文件轨道的唯一方式
        elif token == '8D~~':
            c_code += "    if (current_hatch) { fputc(m[ptr], current_hatch); fflush(current_hatch); }\n"
            continue

        # 5. 即时喷射 (v2.0 后缀 ~) -> 只去 stdout
        eject = token.endswith('~') and not token.endswith('~~')
        cmd = token[:-1] if eject else token

        # 基础指令处理...
        if cmd == '8{':
            c_code += "    while(m[ptr]) {\n"
        elif cmd == '}D':
            c_code += "    }\n"
        elif cmd.startswith('8') and cmd.endswith('D'):
            val = cmd.count('=') - cmd.count('.')
            if val != 0: c_code += f"    m[ptr] {'+=' if val > 0 else '-='} {abs(val)};\n"
        elif cmd.startswith('8') and cmd.endswith('>'):
            c_code += f"    ptr += {cmd.count('=') + 1};\n"
        elif cmd.startswith('<') and cmd.endswith('8'):
            c_code += f"    ptr -= {cmd.count('=') + 1};\n"
        elif cmd == '~':
            c_code += "    m[ptr] = getchar();\n"

        if eject:
            c_code += "    putchar(m[ptr]);\n"

    c_code += """
    if(h0) fclose(h0); if(h1) fclose(h1); if(h2) fclose(h2); if(h3) fclose(h3);
    return 0;
}
"""
    return c_code

def main():
    if len(sys.argv) < 2:
        print("⚙️ Pink8D Force v3.0 | Usage: python3 p8dforce.py <src.8d> [-c]")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        source = f.read()

    c_code = compile_to_c(source)

    if '-c' in sys.argv:
        print(c_code)
        return

    # 自动嗅探编译器 (优先使用 clang，追求最高压入性能)
    compiler = "clang" if shutil.which("clang") else ("gcc" if shutil.which("gcc") else None)
    
    if not compiler:
        print("⚠️ No Industrial Compiler detected. Source Ejected.")
        print(c_code)
        return

    out_bin = sys.argv[1].rsplit('.', 1)[0]
    print(f"⚙️ Probing environment... Using {compiler}")
    
    # 管道直压，-O3 榨取极限性能
    proc = subprocess.Popen([compiler, "-x", "c", "-O3", "-", "-o", out_bin], stdin=subprocess.PIPE)
    proc.communicate(input=c_code.encode('utf-8'))

    if proc.returncode == 0:
        print(f"🚀 Success! Logic injected into: {out_bin}")

if __name__ == "__main__":
    main()
