import re
import sys
import struct

# 指令映射表
OP_MAP = { "8{": 0x01, "}D": 0x02, "~": 0x03, "ADD": 0x04, "SUB": 0x05, "MOV_R": 0x06, "MOV_L": 0x07 }

def compile_to_bytecode(source):
    tokens = re.findall(r'8[=.]*D~?|8[=]*>~?|<[=]*8~?|8\{|\}D|~', source)
    bytecode = bytearray()

    for t in tokens:
        has_eject = 0x80 if t.endswith('~') else 0x00
        cmd = t.rstrip('~')
        
        if cmd == "8{": bytecode.append(OP_MAP["8{"])
        elif cmd == "}D": bytecode.append(OP_MAP["}D"])
        elif cmd == "~": bytecode.append(OP_MAP["~"])
        
        # 编码逻辑：操作码 | 喷射位 (High Bit) + 力量值 (Payload)
        elif cmd.startswith('8') and cmd.endswith('>'):
            bytecode.extend([OP_MAP["MOV_R"] | has_eject, cmd.count('=') + 1])
        elif cmd.startswith('<') and cmd.endswith('8'):
            bytecode.extend([OP_MAP["MOV_L"] | has_eject, cmd.count('=') + 1])
        elif cmd.startswith('8') and cmd.endswith('D'):
            core = cmd[1:-1]
            op = OP_MAP["ADD"] if '=' in core or not core else OP_MAP["SUB"]
            val = core.count('=') if op == OP_MAP["ADD"] else core.count('.')
            bytecode.extend([op | has_eject, val])

    return bytecode

if __name__ == "__main__":
    if len(sys.argv) > 1:
        out = compile_to_bytecode(open(sys.argv[1]).read())
        with open(sys.argv[1].split('.')[0] + ".ejac", "wb") as f: f.write(out)