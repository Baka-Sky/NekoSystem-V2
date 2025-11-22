import mcpi.minecraft as minecraft
import psutil
import time
import subprocess
import platform
import threading
import re
import sys
import select

class NekoSystemMonitor:
    def __init__(self, mc_connection, interval_minutes=30):
        self.mc = mc_connection
        self.interval = interval_minutes * 60  # 转换为秒
        self.running = False
        self.monitor_thread = None
        self.command_thread = None
        self.console_thread = None
        self.last_report_time = 0
        self.report_count = 0
        self.restart_requested = False
        self.shutdown_requested = False
        
        # 颜色代码映射
        self.color_codes = {
            "black": "§0",
            "dark_blue": "§1",
            "dark_green": "§2",
            "dark_aqua": "§3",
            "dark_red": "§4",
            "dark_purple": "§5",
            "gold": "§6",
            "gray": "§7",
            "dark_gray": "§8",
            "blue": "§9",
            "green": "§a",
            "aqua": "§b",
            "red": "§c",
            "light_purple": "§d",
            "yellow": "§e",
            "white": "§f"
        }
    
    def get_color_by_percentage(self, percentage):
        """根据百分比返回颜色"""
        if percentage < 30:
            return self.color_codes["green"]  # 绿色
        elif percentage < 70:
            return self.color_codes["yellow"]  # 黄色
        else:
            return self.color_codes["red"]  # 红色
    
    def get_color_by_status(self, status):
        """根据状态返回颜色"""
        status_colors = {
            "非常好": self.color_codes["green"],
            "好": self.color_codes["green"],
            "良好": self.color_codes["aqua"],
            "中": self.color_codes["yellow"],
            "差": self.color_codes["gold"],
            "较差": self.color_codes["red"],
            "极差": self.color_codes["dark_red"],
            "轻松": self.color_codes["green"],
            "上压力了": self.color_codes["yellow"],
            "燃尽了": self.color_codes["red"],
            "极好": self.color_codes["green"],
            "很好": self.color_codes["green"],
            "良好": self.color_codes["aqua"],
            "一般": self.color_codes["yellow"],
            "差": self.color_codes["gold"],
            "极差": self.color_codes["red"],
            "未知": self.color_codes["gray"]
        }
        return status_colors.get(status, self.color_codes["white"])
    
    def get_cpu_status(self):
        """获取CPU状态"""
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent < 30:
            status = "轻松"
        elif cpu_percent < 70:
            status = "上压力了"
        else:
            status = "燃尽了"
        return cpu_percent, status
    
    def get_handle_count(self):
        """获取句柄数"""
        try:
            if platform.system() == "Windows":
                # Windows系统获取句柄数
                handle_count = 0
                for proc in psutil.process_iter(['pid', 'num_handles']):
                    try:
                        handle_count += proc.info['num_handles']
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                return handle_count
            else:
                # Linux/Mac系统获取文件描述符数
                result = subprocess.run(['lsof', '-n'], capture_output=True, text=True)
                return len(result.stdout.splitlines())
        except:
            return "未知"
    
    def get_memory_status(self):
        """获取内存状态"""
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        if memory_percent < 50:
            status = "轻松"
        elif memory_percent < 80:
            status = "上压力了"
        else:
            status = "燃尽了"
        return memory_percent, status
    
    def get_network_status(self):
        """获取网络状态 - 修复版本"""
        try:
            # 使用更可靠的方法ping百度
            param = "-n" if platform.system().lower() == "windows" else "-c"
            command = ["ping", param, "4", "www.baidu.com"]
            
            # 执行ping命令
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=15  # 增加超时时间
            )
            
            # 检查是否成功
            if result.returncode == 0:
                # 解析ping结果获取延迟
                output = result.stdout
                
                # 使用正则表达式提取延迟时间
                time_pattern = r"时间[=<](\d+)ms" if "时间" in output else r"time[=<](\d+)ms"
                matches = re.findall(time_pattern, output)
                
                if matches:
                    # 计算平均延迟
                    latencies = [int(match) for match in matches]
                    avg_latency = sum(latencies) / len(latencies)
                    
                    if avg_latency < 50:
                        return avg_latency, "极好"
                    elif avg_latency < 100:
                        return avg_latency, "很好"
                    elif avg_latency < 200:
                        return avg_latency, "良好"
                    elif avg_latency < 300:
                        return avg_latency, "一般"
                    elif avg_latency < 500:
                        return avg_latency, "差"
                    else:
                        return avg_latency, "极差"
                else:
                    # 如果没有找到延迟数据，但命令成功执行，说明网络正常但无法解析延迟
                    return "正常", "良好"
            else:
                return "失败", "未知"
                
        except subprocess.TimeoutExpired:
            return "超时", "未知"
        except Exception as e:
            print(f"网络检测错误: {e}")
            return "错误", "未知"
    
    def get_overall_status(self, cpu_status, memory_status, network_status):
        """获取总体状态"""
        status_mapping = {
            "轻松": 1, "上压力了": 2, "燃尽了": 3,
            "极好": 1, "很好": 1, "良好": 2, "一般": 3, "差": 4, "极差": 5, "未知": 4
        }
        
        scores = [
            status_mapping.get(cpu_status, 3),
            status_mapping.get(memory_status, 3),
            status_mapping.get(network_status, 3)
        ]
        
        avg_score = sum(scores) / len(scores)
        
        if avg_score < 1.5:
            return "非常好"
        elif avg_score < 2:
            return "好"
        elif avg_score < 2.5:
            return "良好"
        elif avg_score < 3:
            return "中"
        elif avg_score < 4:
            return "差"
        elif avg_score < 5:
            return "较差"
        else:
            return "极差"
    
    def send_system_report(self):
        """发送系统报告到Minecraft"""
        # 防止重复发送
        current_time = time.time()
        if current_time - self.last_report_time < 5:  # 5秒内不重复发送
            return
            
        self.last_report_time = current_time
        self.report_count += 1  # 增加计数器
        
        try:
            # 获取系统信息
            cpu_percent, cpu_status = self.get_cpu_status()
            handle_count = self.get_handle_count()
            memory_percent, memory_status = self.get_memory_status()
            network_latency, network_status = self.get_network_status()
            
            # 计算总体状态
            overall_status = self.get_overall_status(cpu_status, memory_status, network_status)
            
            # 获取颜色
            cpu_color = self.get_color_by_percentage(cpu_percent)
            cpu_status_color = self.get_color_by_status(cpu_status)
            memory_color = self.get_color_by_percentage(memory_percent)
            memory_status_color = self.get_color_by_status(memory_status)
            network_status_color = self.get_color_by_status(network_status)
            overall_color = self.get_color_by_status(overall_status)
            
            # 发送到Minecraft
            self.mc.postToChat("§6=== NekoSystem v2 ===")
            
            # CPU信息 - 百分比和状态都有颜色
            cpu_percent_str = f"{cpu_percent:.1f}%"
            self.mc.postToChat(f"§fCPU: {cpu_color}{cpu_percent_str} §f({cpu_status_color}{cpu_status}§f)")
            
            # 句柄数
            self.mc.postToChat(f"§fCPU句柄数: {handle_count}")
            
            # 内存信息 - 百分比和状态都有颜色
            memory_percent_str = f"{memory_percent:.1f}%"
            self.mc.postToChat(f"§fRAM: {memory_color}{memory_percent_str} §f({memory_status_color}{memory_status}§f)")
            
            # 网络信息
            if isinstance(network_latency, (int, float)):
                self.mc.postToChat(f"§fNetwork: {network_latency:.1f}ms ({network_status_color}{network_status}§f)")
            else:
                self.mc.postToChat(f"§fNetwork: {network_latency} ({network_status_color}{network_status}§f)")
                
            # 总结 - 有颜色
            self.mc.postToChat(f"§f总结: {overall_color}{overall_status}")
            self.mc.postToChat("§6====================")
            
            # 在Python后台输出这是第几次报告
            print(f"第 {self.report_count} 次系统报告已发送 - CPU: {cpu_percent:.1f}%, RAM: {memory_percent:.1f}%, 网络: {network_status}")
            
        except Exception as e:
            print(f"发送系统报告时出错: {e}")
    
    def send_help(self, source="console"):
        """发送帮助信息"""
        help_messages = [
            "§6=== NekoSystem v2 帮助 ===",
            "§fneko 或 nekosystem §7- 显示此帮助信息",
            "§fneko reboot §7- 重启监控系统",
            "§fneko off §7- 关闭监控系统",
            "§fneko per §7- 立即查看系统性能",
            "§fneko status §7- 查看监控系统状态",
            "§6========================"
        ]
        
        if source == "console":
            for msg in help_messages:
                # 移除颜色代码，在控制台显示
                clean_msg = re.sub(r'§.', '', msg)
                print(clean_msg)
        else:
            for msg in help_messages:
                self.mc.postToChat(msg)
    
    def send_status(self, source="console"):
        """发送系统状态"""
        status = "运行中" if self.running else "已停止"
        interval_minutes = self.interval / 60
        
        if source == "console":
            print(f"NekoSystem 状态: {status}")
            print(f"报告间隔: {interval_minutes} 分钟")
            print(f"已发送报告: {self.report_count} 次")
        else:
            self.mc.postToChat(f"§6NekoSystem 状态: §a{status}")
            self.mc.postToChat(f"§6报告间隔: §a{interval_minutes} 分钟")
            self.mc.postToChat(f"§6已发送报告: §a{self.report_count} 次")
    
    def process_command(self, message, source="game"):
        """处理聊天命令"""
        command = message.strip().lower()
        
        if command in ["neko", "nekosystem"]:
            self.send_help(source)
        elif command == "neko reboot":
            if source == "console":
                print("NekoSystem 重启中...")
            else:
                self.mc.postToChat("§6NekoSystem 重启中...")
            self.restart_requested = True
        elif command == "neko off":
            if source == "console":
                print("NekoSystem 关闭中...")
            else:
                self.mc.postToChat("§6NekoSystem 关闭中...")
            self.shutdown_requested = True
        elif command == "neko per":
            if source == "console":
                print("立即生成系统性能报告...")
            else:
                self.mc.postToChat("§6立即生成系统性能报告...")
            self.send_system_report()
        elif command == "neko status":
            self.send_status(source)
        else:
            if source == "console":
                print("未知命令，输入 'neko' 查看帮助")
            else:
                self.mc.postToChat("§c未知命令，输入 'neko' 查看帮助")
    
    def command_listener(self):
        """监听聊天命令"""
        print("游戏命令监听器已启动")
        while self.running:
            try:
                # 检查是否有重启或关闭请求
                if self.restart_requested:
                    self._perform_restart()
                    continue
                elif self.shutdown_requested:
                    self._perform_shutdown()
                    break
                
                # 获取聊天消息
                events = self.mc.events.pollChatPosts()
                for event in events:
                    message = event.message
                    # 检查是否是命令
                    if message.lower().startswith(('neko', 'nekosystem')):
                        print(f"收到游戏命令: {message}")
                        self.process_command(message, "game")
                time.sleep(1)  # 每秒检查一次
            except Exception as e:
                print(f"游戏命令监听错误: {e}")
                time.sleep(5)  # 出错时等待5秒再继续
    
    def console_listener(self):
        """监听控制台命令"""
        print("控制台命令监听器已启动")
        print("输入 'neko' 查看可用命令")
        
        while self.running:
            try:
                # 检查是否有重启或关闭请求
                if self.restart_requested:
                    self._perform_restart()
                    continue
                elif self.shutdown_requested:
                    self._perform_shutdown()
                    break
                
                # 检查控制台输入
                if sys.platform == "win32":
                    # Windows 平台使用 msvcrt
                    import msvcrt
                    if msvcrt.kbhit():
                        command = input().strip()
                        if command:
                            print(f"收到控制台命令: {command}")
                            self.process_command(command, "console")
                else:
                    # Unix/Linux 平台使用 select
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        command = sys.stdin.readline().strip()
                        if command:
                            print(f"收到控制台命令: {command}")
                            self.process_command(command, "console")
                
                time.sleep(0.1)  # 减少CPU占用
            except Exception as e:
                print(f"控制台命令监听错误: {e}")
                time.sleep(5)  # 出错时等待5秒再继续
    
    def _perform_restart(self):
        """执行重启操作"""
        try:
            # 停止监控线程
            self.running = False
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5)
            
            # 重置状态
            self.running = True
            self.restart_requested = False
            
            # 重新启动监控线程
            self.monitor_thread = threading.Thread(target=self.monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            self.mc.postToChat("§aNekoSystem 重启完成！")
            print("NekoSystem 重启完成")
            
            # 重启后立即发送一次报告
            time.sleep(2)
            self.send_system_report()
        except Exception as e:
            print(f"重启错误: {e}")
            self.mc.postToChat("§c重启失败，请检查控制台")
    
    def _perform_shutdown(self):
        """执行关闭操作"""
        try:
            # 停止所有线程
            self.running = False
            self.shutdown_requested = False
            
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5)
            
            self.mc.postToChat("§cNekoSystem 已关闭")
            print("NekoSystem 已关闭")
        except Exception as e:
            print(f"关闭错误: {e}")
    
    def monitor_loop(self):
        """监控循环"""
        while self.running:
            self.send_system_report()
            # 等待指定间隔
            for _ in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def start(self):
        """开始监控"""
        if self.running:
            print("监控已经在运行中")
            return
        
        self.running = True
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        # 启动游戏命令监听线程
        self.command_thread = threading.Thread(target=self.command_listener)
        self.command_thread.daemon = True
        self.command_thread.start()
        
        # 启动控制台命令监听线程
        self.console_thread = threading.Thread(target=self.console_listener)
        self.console_thread.daemon = True
        self.console_thread.start()
        
        print(f"NekoSystem v2 已启动，每 {self.interval/60} 分钟报告一次")
        self.mc.postToChat(f"§aNekoSystem v2 已启动，每 {self.interval/60} 分钟报告一次")
        self.mc.postToChat("§a输入 'neko' 查看可用命令")
    
    def stop(self):
        """停止监控"""
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        if self.command_thread and self.command_thread.is_alive():
            self.command_thread.join(timeout=5)
        if self.console_thread and self.console_thread.is_alive():
            self.console_thread.join(timeout=5)
        print(f"NekoSystem v2 已停止，共发送了 {self.report_count} 次报告")
    
    def set_interval(self, minutes):
        """设置报告间隔"""
        old_interval = self.interval
        self.interval = minutes * 60
        print(f"报告间隔已从 {old_interval/60} 分钟改为 {minutes} 分钟")
        self.mc.postToChat(f"§6报告间隔已从 {old_interval/60} 分钟改为 {minutes} 分钟")
    
    def get_report_count(self):
        """获取当前报告次数"""
        return self.report_count

# 使用示例
if __name__ == "__main__":
    try:
        # 连接到Minecraft
        mc = minecraft.Minecraft.create(address="xxx.xxx.xxx", port=4711)
        # mc = minecraft.Minecraft.create()  # 本地连接
        
        # 创建监控系统
        monitor = NekoSystemMonitor(mc, interval_minutes=30)  # 默认30分钟
        
        # 启动监控
        monitor.start()
        
        # 保持程序运行
        print("监控系统正在运行，按 Ctrl+C 停止")
        print("可以在 Minecraft 聊天栏或此控制台输入命令")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在停止监控...")
            monitor.stop()
            
    except Exception as e:

        print(f"连接失败: {e}")
