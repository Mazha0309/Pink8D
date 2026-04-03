import re
import sys
import argparse

class Pink8DInterpreter:
    def __init__(self, code, memory_size=30000):
        """
        Initialize the Pink8D Interpreter.
        初始化 Pink8D 解释器。
        """
        self.code = code
        self.memory = [0] * memory_size
        self.ptr = 0  # Data Pointer (DP) | 数据指针
        self.pc = 0   # Program Counter (IP) | 程序计数器
        self.instructions = []
        self.loop_map = {}
        
        self._tokenize()
        self._build_loop_map()

    def _tokenize(self):
        """
        Morphological Lexer: Matches instructions based on visual patterns.
        形态学词法分析器：基于视觉模式匹配指令。
        """
        # Optimized Pattern: Supports single '=' or '.' and optional prefixes/suffixes.
        # 优化后的模式：支持单个 '=' 或 '.'，以及可选的前后缀。
        # Matches: ~8=D, 8.D*, ===>, <===8, 8{, }D
        pattern = r'~?8[=.]*D[~*]*|[=]*>|<[=]*8|8\{|\}D'
        self.instructions = re.findall(pattern, self.code)

    def _build_loop_map(self):
        """
        Pre-computes the jump positions for loops.
        预计算循环跳转位置。
        """
        stack = []
        for i, inst in enumerate(self.instructions):
            if inst == "8{":
                stack.append(i)
            elif inst == "}D":
                if not stack:
                    raise SyntaxError(f"Extra }}D at index {i} | 索引 {i} 处存在多余的 }}D")
                start = stack.pop()
                self.loop_map[start] = i
                self.loop_map[i] = start
        if stack:
            raise SyntaxError("Unclosed 8{ loop | 存在未闭合的 8{ 循环")

    def run(self):
        """
        Execution Engine | 执行引擎
        """
        while self.pc < len(self.instructions):
            inst = self.instructions[self.pc]
            
            # --- 1. Increment / Input / Output (The Shaft) ---
            # --- 1. 增加 / 输入 / 输出 ---
            if '8' in inst and 'D' in inst:
                # Count intensity | 计算强度
                plus_count = inst.count('=')
                minus_count = inst.count('.')
                
                if inst.startswith('~'):    # Input | 输入
                    char = sys.stdin.read(1)
                    self.memory[self.ptr] = ord(char) if char else 0
                elif '~' in inst:           # Output | 输出
                    sys.stdout.write(chr(self.memory[self.ptr]))
                    sys.stdout.flush()
                elif '*' in inst:           # Jump DP | 跳转指针
                    self.ptr = self.memory[self.ptr] % len(self.memory)
                else:                       # Calculation | 数值运算
                    self.memory[self.ptr] = (self.memory[self.ptr] + plus_count - minus_count) % 256

            # --- 2. Pointer Movement ---
            # --- 2. 指针位移 ---
            elif inst.endswith('>'):
                self.ptr = (self.ptr + inst.count('=')) % len(self.memory)
            elif inst.startswith('<'):
                self.ptr = (self.ptr - inst.count('=')) % len(self.memory)

            # --- 3. Control Flow ---
            # --- 3. 控制流 ---
            elif inst == "8{":
                if self.memory[self.ptr] == 0:
                    self.pc = self.loop_map[self.pc]
            elif inst == "}D":
                if self.memory[self.ptr] != 0:
                    self.pc = self.loop_map[self.pc]

            self.pc += 1

def main():
    parser = argparse.ArgumentParser(description="Pink8D Interpreter v1.2")
    parser.add_argument("file", help="Source file (.8d)")
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()

    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            code = f.read()
        interpreter = Pink8DInterpreter(code)
        interpreter.run()
    except Exception as e:
        print(f"Runtime Error | 运行时错误: {e}")

if __name__ == "__main__":
    main()
