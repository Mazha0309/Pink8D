import re
import sys
import pickle # 用于序列化字节码

class Pink8DCompiler:
    def __init__(self, code):
        self.code = code
        # 定义 Opcode (操作码)
        self.OP = {
            'ADD': 0x01, 'SUB': 0x02, 'RIGHT': 0x03, 'LEFT': 0x04,
            'OPEN': 0x05, 'CLOSE': 0x06, 'OUT': 0x07, 'IN': 0x08, 'JMP': 0x09
        }

    def compile(self, output_file):
        # 1. 词法分析
        pattern = r'~?8[=.]*D[~*]*|[=]*>|<[=]*8|8\{|\}D'
        tokens = re.findall(pattern, self.code)
        
        bytecode = []
        for inst in tokens:
            if '8' in inst and 'D' in inst:
                if inst.startswith('~'): bytecode.append((self.OP['IN'], 0))
                elif '~' in inst: bytecode.append((self.OP['OUT'], 0))
                elif '*' in inst: bytecode.append((self.OP['JMP'], 0))
                else:
                    val = inst.count('=') - inst.count('.')
                    op = self.OP['ADD'] if val >= 0 else self.OP['SUB']
                    bytecode.append((op, abs(val)))
            elif inst.endswith('>'): bytecode.append((self.OP['RIGHT'], inst.count('=')))
            elif inst.startswith('<'): bytecode.append((self.OP['LEFT'], inst.count('=')))
            elif inst == "8{": bytecode.append((self.OP['OPEN'], 0))
            elif inst == "}D": bytecode.append((self.OP['CLOSE'], 0))

        # 2. 持久化为 .ejac 文件
        with open(output_file, 'wb') as f:
            pickle.dump(bytecode, f)
        print(f"Compilation Complete: {output_file} (The Essence is preserved.)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 p8cc.py <file.8d>")
    else:
        with open(sys.argv[1], 'r') as f:
            Pink8DCompiler(f.read()).compile(sys.argv[1].replace('.8d', '.ejac'))
