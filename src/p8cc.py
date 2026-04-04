import re, sys, struct

# Opcode 定义
OPS = {'8{': 0x01, '}D': 0x02, '8D': 0x03, '>': 0x04, '<': 0x05, 'SEL': 0x06, 'JMP': 0x07}

def compile_to_bytecode(path):
    with open(path, 'r') as f: source = f.read()
    tokens = re.findall(r'(~~|~)?(8[=\.]*[D>\}]|<[=\.]*8|8\*D|8\[=*\]D|8\{)(~~|~)?', source)
    
    binary = bytearray()
    for pre, body, suf in tokens:
        # 编码标记位: 00(无), 01(细管~), 10(粗管~~)
        io_flag = (1 if pre=='~' else 2 if pre=='~~' else 0) << 4 | (1 if suf=='~' else 2 if suf=='~~' else 0)
        binary.append(io_flag)
        
        # 指令编码
        if "8[" in body: binary.extend([OPS['SEL'], body.count('=')])
        elif "8*" in body: binary.extend([OPS['JMP'], 0])
        elif body == "8{": binary.extend([OPS['8{'], 0]) # 占位符，由 VM 处理跳转
        elif body == "}D": binary.extend([OPS['}D'], 0])
        elif "8" in body and "D" in body: binary.extend([OPS['8D'], (body.count('=') - body.count('.')) % 256])
        elif ">" in body: binary.extend([OPS['>'], body.count('=')+1])
        elif "<" in body: binary.extend([OPS['<'], body.count('=')+1])
    
    with open(path.replace('.8d', '.ejac'), 'wb') as f: f.write(binary)

if __name__ == "__main__": compile_to_bytecode(sys.argv[1])
