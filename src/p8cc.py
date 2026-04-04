import re, sys

# Opcode 定义 (严格对应 v3 规范)
OPS = {
    '8{': 0x01, 
    '}D': 0x02, 
    '8D': 0x03, 
    '>': 0x04, 
    '<': 0x05, 
    'SEL': 0x06, 
    'JMP': 0x07,
    'NOP': 0x00
}

def compile_to_bytecode(path):
    with open(path, 'r', encoding='utf-8') as f: 
        source = f.read()
    
    pattern = r'(~~|~)?(8\[H\d:.*?\]D|8\[=*\]D|8[=\.]*[D>]|8\*D|8\{|\}D|<[=\.]*8)(~~|~)?'
    tokens = re.findall(pattern, source)
    
    binary = bytearray()
    for pre, body, suf in tokens:
        # 1. 标志位 (1字节)
        io_flag = (1 if pre=='~' else 2 if pre=='~~' else 0) << 4 | (1 if suf=='~' else 2 if suf=='~~' else 0)
        binary.append(io_flag)
        
        # 2. 指令与参数 (必须占满2字节)
        if "8[H" in body: # 轨道路径定义
            match = re.search(r'H(\d)', body)
            h_idx = int(match.group(1)) if match else 0
            binary.extend([OPS['SEL'], h_idx])
        elif "8[" in body: # 轨道切换
            binary.extend([OPS['SEL'], body.count('=')])
        elif "8*" in body: # 弹射跳转
            binary.extend([OPS['JMP'], 0])
        elif body == "8{": 
            binary.extend([OPS['8{'], 0])
        elif body == "}D": 
            binary.extend([OPS['}D'], 0])
        elif "8" in body and "D" in body: # 压力调节
            val = (body.count('=') - body.count('.')) % 256
            binary.extend([OPS['8D'], val])
        elif ">" in body: # 右移
            binary.extend([OPS['>'], body.count('=')+1])
        elif "<" in body: # 左移
            binary.extend([OPS['<'], body.count('=')+1])
        else:
            # 这里的兜底非常重要，防止字节码对齐崩盘
            binary.extend([OPS['NOP'], 0])
    
    output_path = path.replace('.8d', '.ejac')
    with open(output_path, 'wb') as f: 
        f.write(binary)
    print(f"🔩 Compiled: {path} -> {output_path} ({len(binary)} bytes)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        compile_to_bytecode(sys.argv[1])
