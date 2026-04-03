import re
import sys
import subprocess
import os

class Pink8DForge:
    def __init__(self, code):
        self.code = code
        self.instructions = []
        self._tokenize()

    def _tokenize(self):
        # 匹配规则：
        # 1. 8[=.]*D(~)? -> 赋值
        # 2. 8[=]*> (~)? -> 右移
        # 3. <[=]*8 (~)? -> 左移
        # 4. 8{ / }D / ~ -> 循环与输入
        pattern = r'8[=.]*D~?|8[=]*>~?|<[=]*8~?|8\{|\}D|~'
        self.instructions = re.findall(pattern, self.code)

    def generate_c(self):
        c_code = [
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#define MEM_SIZE 1000000",
            "unsigned char m[MEM_SIZE] = {0};",
            "int main() {",
            "    int i = 0;",
            "    setvbuf(stdout, NULL, _IOLBF, 1024);",
            "    /* --- Pink8D Hardware-Level Execution --- */"
        ]
        
        for inst in self.instructions:
            has_eject = inst.endswith('~')
            clean_inst = inst.rstrip('~')

            # 1. 循环与基础 IO
            if inst == "8{":
                c_code.append("    while (m[i]) {")
            elif inst == "}D":
                c_code.append("    }")
            elif inst == "~":
                c_code.append("    m[i] = getchar();")

            # 2. 右向位移: 8====>
            elif clean_inst.startswith('8') and clean_inst.endswith('>'):
                power = clean_inst.count('=') + 1 # 连同箭头本身至少移1位
                c_code.append(f"    i = (i + {power}) % MEM_SIZE;")
                if has_eject: c_code.append("    putchar(m[i]);")

            # 3. 左向位移: <====8
            elif clean_inst.startswith('<') and clean_inst.endswith('8'):
                power = clean_inst.count('=') + 1
                c_code.append(f"    i = (i - {power} + MEM_SIZE) % MEM_SIZE;")
                if has_eject: c_code.append("    putchar(m[i]);")

            # 4. 压力赋值: 8====D / 8....D
            elif clean_inst.startswith('8') and clean_inst.endswith('D'):
                core = clean_inst[1:-1]
                val = core.count('=') - core.count('.')
                c_code.append(f"    m[i] += {val};")
                if has_eject: c_code.append("    putchar(m[i]);")

        c_code.append("    return 0;\n}")
        return "\n".join(c_code)

def main():
    if len(sys.argv) < 2:
        print("Pink8D Forge v2.0 [Native Arch Linux]")
        return
    
    input_file = sys.argv[1]
    base_name = os.path.splitext(input_file)[0]
    c_file = base_name + ".c"

    with open(input_file, 'r') as f:
        forge = Pink8DForge(f.read())
    
    with open(c_file, 'w') as f:
        f.write(forge.generate_c())

    # 调用 Arch 上的 Clang 进行优化编译
    subprocess.run(["clang", "-O3", c_file, "-o", base_name])
    os.remove(c_file) # 保持目录整洁
    print(f"[*] success! {base_name} compiled successfully.")

if __name__ == "__main__":
    main()