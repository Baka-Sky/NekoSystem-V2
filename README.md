# NekoSystem-V2
基于Python打造的原版MC监控软件 -Wells,Jiang用心制作




![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![Minecraft](https://img.shields.io/badge/Minecraft-Java%20Edition-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

基于Python打造的原版MC监控软件  
**Wells,Jiang用心制作**

## 项目简介

NekoSystem-V2 是一个功能强大的Minecraft服务器监控系统，专为原版Minecraft服务器设计。它能够实时监控服务器运行状态，提供详细的系统性能报告，并通过游戏内聊天命令或控制台命令进行交互控制。

## 功能特色

### 系统监控
- **CPU监控** - 实时监控CPU使用率，智能状态评估
- **内存监控** - 监控内存使用情况，预警内存压力
- **网络监控** - 自动ping测试，评估网络连接质量
- **句柄数统计** - 监控系统资源使用情况

### 游戏内交互
- **彩色显示** - 在Minecraft聊天中使用彩色状态显示
- **智能评估** - 自动生成系统状态总结
- **实时报告** - 可配置的定时报告间隔
- **命令控制** - 通过聊天命令完全控制系统

### 控制台支持
- **双端控制** - 支持游戏内和控制台双重命令输入
- **实时交互** - 无需切换界面即可管理系统
- **详细日志** - 完整的运行日志和错误报告

## 安装指南

### 环境要求
- Python 3.7 或更高版本
- Minecraft Java Edition
- 支持Raspberry Jam Mod的Minecraft客户端

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/NekoSystem-V2.git
   cd NekoSystem-V2
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置Minecraft**
   - 确保Minecraft已安装Raspberry Jam Mod
   - 启动Minecraft并进入一个世界

4. **运行监控系统**
   ```bash
   python neko_system.py
   ```

## 使用方法

### 启动系统
```bash
python neko_system.py
```

系统将自动连接到Minecraft服务器并开始监控。

### 命令列表

#### 游戏内命令（在Minecraft聊天中输入）
| 命令 | 功能描述 | 示例 |
|------|----------|------|
| `neko` 或 `nekosystem` | 显示帮助信息 | `neko` |
| `neko reboot` | 重启监控系统 | `neko reboot` |
| `neko off` | 关闭监控系统 | `neko off` |
| `neko per` | 立即查看系统性能 | `neko per` |
| `neko status` | 查看监控系统状态 | `neko status` |

#### 控制台命令（在Python控制台输入）
直接在控制台输入上述命令即可：
```text
neko status
neko per
neko reboot
```

### 配置说明

在代码中修改以下参数来自定义系统行为：

```python
# 修改报告间隔（分钟）
monitor = NekoSystemMonitor(mc, interval_minutes=30)

# 修改连接地址和端口
mc = minecraft.Minecraft.create(address="home.bakasky.top", port=4711)
```

## 项目结构

```
NekoSystem-V2/
├── neko_system.py    # 主程序文件
├── requirements.txt  # 依赖包列表
├── README.md         # 项目说明
└── LICENSE           # 许可证文件
```

## 依赖包

- `mcpi` - Minecraft Pi Edition API
- `psutil` - 系统监控库
- 其他Python标准库

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

本项目采用MIT许可证 - 查看LICENSE文件了解详情

## 致谢

感谢所有为此项目做出贡献的开发者！

---

**🐱 由 Wells, Jiang 用心制作 🐱**'''

print(markdown_content)
```

这是完整的Python代码，输出的是格式正确的Markdown文档。所有代码块都正确使用了反引号标记，格式完整且没有语法错误。
