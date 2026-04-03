import re
import sys
import subprocess
import os
import platform

class Pink8DNativeCompiler:
    def __init__(self, code):
        self.code = code
        self.instructions = []
        self._tokenize()

    def _tokenize(self):
        # Pattern matching for Pink8D morphological syntax
        pattern = r'~?8[=.]*D[~*]*|[=]*>|<[=]*8|8\{|\}D'
        self.instructions = re.findall(pattern, self.code)

    def generate_c(self):
        # 1MB memory pool with cyclic buffer protection
        c_code = [
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "",
            "#define MEM_SIZE 1000000",
            "unsigned char m[MEM_SIZE] = {0};",
            "",
            "int main() {",
            "    int i = 0; // Data pointer index",
            "    /* Enable line buffering for real-time output */",
            "    setvbuf(stdout, NULL, _IOLBF, 1024);",
            "",
            "    /* --- Pink8D Execution Logic --- */"
        ]
        
        for inst in self.instructions:
            if '8' in inst and 'D' in inst:
                v = inst.count('=') - inst.count('.')
                if '~' in inst: 
                    c_code.append("    putchar(m[i]);")
                elif inst.startswith('~'): 
                    c_code.append("    m[i] = getchar();")
                elif '*' in inst:
                    c_code.append("    i = m[i] % MEM_SIZE;")
                else:
                    if v > 0: c_code.append(f"    m[i] += {v};")
                    elif v < 0: c_code.append(f"    m[i] -= {abs(v)};")
            elif inst.endswith('>'):
                c_code.append(f"    i = (i + {inst.count('=')}) % MEM_SIZE;")
            elif inst.startswith('<'):
                c_code.append(f"    i = (i - {inst.count('=')} + MEM_SIZE) % MEM_SIZE;")
            elif inst == "8{":
                c_code.append("    while (m[i]) {")
            elif inst == "}D":
                c_code.append("    }")

        c_code.append("    /* --- End of Logic --- */")
        c_code.append("    return 0;")
        c_code.append("}")
        return "\n".join(c_code)

def main():
    if len(sys.argv) < 2:
        print("Pink8D Native Forge")
        print("Usage: python3 p8dforce.py <source.8d>")
        return

    input_file = sys.argv[1]
    base_name = os.path.splitext(input_file)[0]
    c_file = base_name + ".c"
    
    # Binary extension (empty for Linux/Termux, .exe for Windows)
    ext = ".exe" if platform.system() == "Windows" else ""
    output_bin = base_name + ext

    # 1. Transpilation phase
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            compiler = Pink8DNativeCompiler(f.read())
        with open(c_file, 'w', encoding='utf-8') as f:
            f.write(compiler.generate_c())
        print(f"[*] Generated C source: {c_file}")
    except Exception as e:
        print(f"[-] Transpilation failed: {e}")
        return

    # 2. Compilation phase (Prioritize clang on Termux)
    is_termux = "com.termux" in os.environ.get("PREFIX", "")
    compilers = ["clang", "gcc"] if is_termux else ["gcc", "clang"]

    success = False
    for cc in compilers:
        try:
            print(f"[*] Compiling with {cc} (-O3 optimization)...")
            subprocess.run([cc, "-O3", c_file, "-o", output_bin], check=True)
            success = True
            print(f"[+] Native binary forged: ./{output_bin}")
            break
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue

    # 3. Cleanup phase
    if success:
        if os.path.exists(c_file):
            os.remove(c_file)
            print(f"[*] Temporary file {c_file} cleaned.")
    else:
        print("[-] Error: No C compiler found. Please install clang or gcc.")

if __name__ == "__main__":
    main()
