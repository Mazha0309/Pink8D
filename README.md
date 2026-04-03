# Pink8D (P8D)

> A morphological programming language with length-variable instructions and deep-probe dereferencing.

Pink8D 是一门形态学编程语言（Esolang），所有语法都围绕 `8====D` 这一视觉形态展开。**杆长即数值**，通过 `=` 的数量来决定运算强度，是 Brainfuck 家族的艺术化扩展。

## 🎯 项目特色

- **形态美学** - 代码本身具有强烈的视觉冲击力
- **极简语法** - 核心指令只有 9 条，学习曲线平缓
- **四套执行引擎** - 解释器、字节码编译器+虚拟机、原生 C 代码转译器
- **高性能选项** - `p8dforce.py` 可将代码转译为优化的 C 代码并编译为原生二进制

## 📦 快速开始

### 环境要求

- Python 3.6+
- GCC 或 Clang 编译器（仅在使用 p8dforce.py 时需要）

### 安装

```bash
git clone https://github.com/your-repo/Pink8D.git
cd Pink8D
```

### 运行示例

```bash
# 使用解释器直接运行
python3 src/p8d.py examples/ok.8d

# 使用字节码编译器 + 虚拟机
python3 src/p8cc.py examples/BG5CRL.8d
python3 src/p8vm.py examples/BG5CRL.ejac

# 使用原生编译器（推荐用于生产环境）
python3 src/p8dforce.py examples/pi.8d
./examples/pi
```

## 🛠️ 工具链详解

### 1. p8d.py - 直接解释器

轻量级解释器，直接解析并执行 `.8d` 源代码。

```bash
python3 src/p8d.py <source.8d>
```

**特点**：
- 启动最快，适合小规模程序调试
- 实时报错，语法错误立即可见
- 内存池：30000 字节

### 2. p8cc.py - 字节码编译器

将 `.8d` 源代码编译为 `.ejac` 字节码文件。

```bash
python3 src/p8cc.py <source.8d>
# 输出：<source>.ejac
```

**特点**：
- 编译过程快速
- 生成的字节码可通过 pickle 反序列化
- 为 `p8vm.py` 提供输入

### 3. p8vm.py - 专用虚拟机

运行由 `p8cc.py` 生成的 `.ejac` 字节码文件。

```bash
python3 src/p8vm.py <source.ejac>
```

**特点**：
- 比解释器执行效率更高
- 内存池：30000 字节
- 支持完整的循环和控制流

### 4. p8dforce.py - 原生转译编译器（旗舰产品）⭐

将 `.8d` 代码转译为优化的 C 代码，并通过 GCC/Clang 编译为原生二进制。

```bash
python3 src/p8dforce.py <source.8d>
# 自动生成并执行：<source> (Linux/macOS) 或 <source>.exe (Windows)
```

**特点**：
- 性能最佳，执行速度接近原生 C 程序
- 自动调用编译器（优先 clang，fallback 到 gcc）
- **自动清理**中间 `.c` 文件
- 内存池：**1MB**（比解释器大 33 倍）
- 支持 Termux 环境（自动优先使用 clang）

**示例**：
```bash
# 编译 Pi 计算器（800+ 位）
python3 src/p8dforce.py examples/pi.8d
./examples/pi
# 输出：3.1415926535...
```

## 📚 示例程序

| 文件 | 说明 | 输出 |
|------|------|------|
| [BG5CRL.8d](examples/BG5CRL.8d) | 无线电呼号 | `BG5CRL\n` |
| [ok.8d](examples/ok.8d) | 基础示例 | `OK\n` |
| [pi.8d](examples/pi.8d) | Pi 计算器（800+ 位）| `3.141592...` |

## 🔧 核心指令

| 指令 | 形态 | 语义 |
|------|------|------|
| **ADD** | `8========D` | 当前内存值 += `=` 的数量 |
| **SUB** | `8....D` | 当前内存值 -= `.` 的数量 |
| **RIGHT** | `===>` | 指针右移 `=` 的数量 |
| **LEFT** | `<===8` | 指针左移 `=` 的数量 |
| **OUT** | `8D~` | 输出当前内存的 ASCII 字符 |
| **IN** | `~8D~` | 输入字符到当前内存 |
| **OPEN** | `8{` | 当指针值 != 0 时循环 |
| **CLOSE** | `}D` | 循环结束标记 |
| **JMP** | `8D*` | 深度跳转（指针 = 内存值）|

## 🎨 视觉语法

Pink8D 的语法设计强调**形态可读性**：

```8d
// 输出 "P" (ASCII 80)
8========D 8========D 8========D
8========D 8========D 8========D
8========D 8========D 8========D
8D~
```

- `8` = 内存操作起点
- `=` = 加法计数（每个 = 代表 +1）
- `D` = 指令终点
- `~` = IO 操作标记

## 📊 性能对比

| 引擎 | 执行速度 | 内存 | 启动时间 | 适用场景 |
|------|----------|------|----------|----------|
| p8d.py | 慢 | 30KB | < 0.1s | 快速测试/调试 |
| p8cc.py + p8vm.py | 中等 | 30KB | 0.1-0.5s | 生产环境（兼容性）|
| p8dforce.py | **快** | **1MB** | 1-3s | **高性能计算** |

## 🛠️ 开发指南

### 添加新的执行引擎

所有引擎都遵循相同的词法分析模式：

```python
pattern = r'~?8[=.]*D[~*]*|[=]*>|<[=]*8|8\{|\}D'
```

### 内存模型

- 默认内存池：30000 字节（`p8dforce.py` 为 1MB）
- 环形缓冲区：指针越界时自动环绕
- 数值范围：0-255（8 位溢出回绕）

## 📝 项目结构

```
Pink8D/
├── README.md              # 本文件
├── LANGSPEC.md            # 语言详细规范
├── examples/              # 示例程序
│   ├── BG5CRL.8d          # 无线电呼号
│   ├── ok.8d              # 基础示例
│   └── pi.8d              # Pi 计算器
└── src/                   # 工具链源码
    ├── p8d.py              # 解释器
    ├── p8cc.py             # 字节码编译器
    ├── p8vm.py             # 虚拟机
    └── p8dforce.py         # 原生转译编译器
```

## 🌟 未来规划

- [ ] VS Code 插件（语法高亮 + 文件关联）
- [ ] Web 在线 Playground
- [ ] 标准库扩展（文件 IO、网络）
- [ ] 性能基准测试套件

## 📜 许可证

MIT License

## 🎙️ 73!

> "The Essence is preserved."

**BG5CRL** | Mazha0309 | 2026
