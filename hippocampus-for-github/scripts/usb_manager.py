#!/usr/bin/env python3
"""
Hippocampus USB Manager
=======================
U盘产品自动运行和管理模块。

功能：
- 检测 U 盘插入
- 自动运行抓取和分析
- 与主机 OpenClaw 交互
- 生成报告
"""

import os
import sys
import json
import platform
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# ============================================================================
# 配置
# ============================================================================

SYSTEM = platform.system()  # Windows | Darwin | Linux

USB_CONFIG = {
    "product_name": "Hippocampus AI Memory Stick",
    "version": "v3.2",
    "autorun_delay": 3,  # 等待秒数
    "capture_on_insert": True,
    "analyze_on_capture": True,
    "generate_report": True,
    "open_on_finish": True,
}


# ============================================================================
# 路径检测
# ============================================================================

def detect_usb_drive() -> Optional[str]:
    """
    检测 U 盘盘符（Windows）
    
    Returns:
        U盘根目录路径，如 "E:\\"
    """
    if SYSTEM == "Windows":
        import string
        # 检查可移动驱动器
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                try:
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    GENERIC_READ = 0x80000000
                    FILE_SHARE_READ = 1
                    FILE_SHARE_WRITE = 2
                    OPEN_EXISTING = 3
                    
                    handle = kernel32.CreateFileA(
                        drive.encode(),
                        GENERIC_READ,
                        FILE_SHARE_READ | FILE_SHARE_WRITE,
                        None,
                        OPEN_EXISTING,
                        0,
                        None
                    )
                    
                    if handle != -1:
                        kernel32.CloseHandle(handle)
                        # 简单判断：检查是否有我们的标志文件
                        if Path(drive, "HIPPOCAMPUS_Marker.txt").exists():
                            return drive
                except:
                    pass
        return None
    
    elif SYSTEM == "Darwin":
        # macOS: 检查 /Volumes
        volumes = Path("/Volumes")
        if volumes.exists():
            for vol in volumes.iterdir():
                marker = vol / "HIPPOCAMPUS_Marker.txt"
                if marker.exists():
                    return str(vol)
        return None
    
    elif SYSTEM == "Linux":
        # Linux: 检查 /media, /mnt, /run/media
        for base in [Path("/media"), Path("/mnt"), Path("/run/media")]:
            if base.exists():
                for vol in base.rglob("*"):
                    marker = vol / "HIPPOCAMPUS_Marker.txt"
                    if marker.exists():
                        return str(vol)
        return None
    
    return None


def is_hippocampus_usb(path: str) -> bool:
    """检查是否是 Hippocampus U 盘"""
    marker = Path(path) / "HIPPOCAMPUS_Marker.txt"
    return marker.exists()


# ============================================================================
# 自动运行
# ============================================================================

class USBAutoRunner:
    """U盘自动运行管理器"""
    
    def __init__(self, usb_root: str):
        self.usb_root = Path(usb_root)
        self.capture_dir = self.usb_root / "capture"
        self.output_dir = self.usb_root / "output"
        self.db_dir = self.usb_root / "db"
        self.log_file = self.usb_root / "activity.log"
        
        # 确保目录存在
        self.capture_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db_dir.mkdir(parents=True, exist_ok=True)
    
    def log(self, message: str):
        """记录活动日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except:
            pass
        
        print(log_entry.strip())
    
    def run_capture(self) -> Dict[str, Any]:
        """运行抓取"""
        self.log("开始抓取 AI 记忆文件...")
        
        capture_script = self.usb_root / "scripts" / "capture.py"
        
        if not capture_script.exists():
            return {"error": "capture.py not found"}
        
        try:
            result = subprocess.run(
                [sys.executable, str(capture_script), "-o", str(self.capture_dir)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            self.log(f"抓取完成: {result.stdout}")
            if result.stderr:
                self.log(f"抓取警告: {result.stderr}")
            
            return {"success": True, "output": result.stdout}
        except subprocess.TimeoutExpired:
            return {"error": "Capture timeout"}
        except Exception as e:
            return {"error": str(e)}
    
    def run_analyze(self) -> Dict[str, Any]:
        """运行分析"""
        self.log("开始分析记忆...")
        
        analyze_script = self.usb_root / "scripts" / "analyzer.py"
        
        if not analyze_script.exists():
            return {"error": "analyzer.py not found"}
        
        try:
            # 索引
            subprocess.run(
                [sys.executable, str(analyze_script), "-b", str(self.usb_root), "-i"],
                capture_output=True,
                timeout=120
            )
            
            # 生成报告
            result = subprocess.run(
                [sys.executable, str(analyze_script), "-b", str(self.usb_root), "-r", "markdown"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            self.log(f"分析完成")
            return {"success": True, "output": result.stdout}
        except Exception as e:
            return {"error": str(e)}
    
    def open_output(self):
        """打开输出目录"""
        if SYSTEM == "Windows":
            os.startfile(self.output_dir)
        elif SYSTEM == "Darwin":
            subprocess.run(["open", self.output_dir])
        elif SYSTEM == "Linux":
            subprocess.run(["xdg-open", self.output_dir])
    
    def run_full_cycle(self) -> Dict[str, Any]:
        """运行完整周期"""
        self.log("=" * 50)
        self.log(f"Hippocampus AI Memory Stick {USB_CONFIG['version']} 启动")
        self.log(f"U盘路径: {self.usb_root}")
        self.log("=" * 50)
        
        results = {}
        
        # 抓取
        if USB_CONFIG.get("capture_on_insert", True):
            capture_result = self.run_capture()
            results["capture"] = capture_result
            if "error" in capture_result:
                self.log(f"抓取出错: {capture_result['error']}")
        
        # 分析
        if USB_CONFIG.get("analyze_on_capture", True) and "error" not in results.get("capture", {}):
            analyze_result = self.run_analyze()
            results["analyze"] = analyze_result
            if "error" in analyze_result:
                self.log(f"分析出错: {analyze_result['error']}")
        
        # 报告
        if USB_CONFIG.get("generate_report", True):
            self.log("报告已生成在 output/ 目录")
        
        # 打开输出
        if USB_CONFIG.get("open_on_finish", True):
            self.open_output()
        
        self.log("处理完成！")
        self.log("=" * 50)
        
        return results


# ============================================================================
# OpenClaw 交互协议
# ============================================================================

class OpenClawBridge:
    """
    OpenClaw 交互桥接
    
    通过文件协议与主机上的 OpenClaw 通信：
    - 读取主机的记忆文件 → 写入 U 盘
    - U 盘分析结果 → 提供给主机 OpenClaw 使用
    """
    
    def __init__(self, usb_root: str, host_config: Dict = None):
        self.usb_root = Path(usb_root)
        self.host_config = host_config or {}
        self.protocol_dir = self.usb_root / "protocol"
        self.protocol_dir.mkdir(parents=True, exist_ok=True)
    
    def write_request(self, request_type: str, data: Dict) -> str:
        """
        写入请求文件
        
        Args:
            request_type: "capture" | "analyze" | "query"
            data: 请求数据
            
        Returns:
            请求文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        request_file = self.protocol_dir / f"request_{request_type}_{timestamp}.json"
        
        with open(request_file, 'w', encoding='utf-8') as f:
            json.dump({
                "type": request_type,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }, f, indent=2, ensure_ascii=False)
        
        return str(request_file)
    
    def read_response(self, timeout: int = 60) -> Optional[Dict]:
        """
        读取响应文件
        
        Args:
            timeout: 超时秒数
            
        Returns:
            响应数据或 None
        """
        response_dir = self.protocol_dir / "responses"
        
        if not response_dir.exists():
            return None
        
        # 查找最新的响应文件
        responses = list(response_dir.glob("response_*.json"))
        if not responses:
            return None
        
        latest = max(responses, key=lambda p: p.stat().st_mtime)
        
        # 检查是否超时
        mtime = datetime.fromtimestamp(latest.stat().st_mtime)
        age = (datetime.now() - mtime).total_seconds()
        
        if age > timeout:
            return None
        
        with open(latest, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def exchange(self, request_type: str, data: Dict, timeout: int = 60) -> Optional[Dict]:
        """
        交换协议：写请求 → 等待响应
        
        Returns:
            响应数据
        """
        self.write_request(request_type, data)
        return self.read_response(timeout)


# ============================================================================
# USB 状态检查
# ============================================================================

def check_usb_status(usb_root: str = None) -> Dict[str, Any]:
    """
    检查 U 盘状态
    
    Returns:
        状态信息字典
    """
    if usb_root is None:
        usb_root = detect_usb_drive()
    
    if usb_root is None:
        return {
            "connected": False,
            "message": "未检测到 Hippocampus U 盘"
        }
    
    if not is_hippocampus_usb(usb_root):
        return {
            "connected": False,
            "message": "U盘不是 Hippocampus 产品"
        }
    
    usb_path = Path(usb_root)
    
    # 检查各个目录
    status = {
        "connected": True,
        "usb_root": usb_root,
        "version": USB_CONFIG["version"],
        "directories": {
            "capture": (usb_path / "capture").exists(),
            "output": (usb_path / "output").exists(),
            "db": (usb_path / "db").exists(),
            "scripts": (usb_path / "scripts").exists(),
        },
        "files": {
            "capture_py": (usb_path / "scripts" / "capture.py").exists(),
            "analyzer_py": (usb_path / "scripts" / "analyzer.py").exists(),
            "autorun": (usb_path / "autorun.bat").exists() or (usb_path / "autorun.sh").exists(),
        },
        "last_activity": None
    }
    
    # 读取最近活动
    log_file = usb_path / "activity.log"
    if log_file.exists():
        try:
            lines = log_file.read_text(encoding='utf-8').strip().split('\n')
            if lines:
                status["last_activity"] = lines[-1]
        except:
            pass
    
    return status


# ============================================================================
# 命令行接口
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Hippocampus USB Manager")
    parser.add_argument("--detect", "-d", action="store_true", help="检测 U 盘")
    parser.add_argument("--status", "-s", action="store_true", help="检查状态")
    parser.add_argument("--run", "-r", action="store_true", help="运行完整周期")
    parser.add_argument("--usb", "-u", default=None, help="指定 U 盘路径")
    parser.add_argument("--capture", "-c", action="store_true", help="仅运行抓取")
    parser.add_argument("--analyze", "-a", action="store_true", help="仅运行分析")
    
    args = parser.parse_args()
    
    if args.detect:
        usb = detect_usb_drive()
        if usb:
            print(f"✓ 检测到 Hippocampus U 盘: {usb}")
        else:
            print("✗ 未检测到 Hippocampus U 盘")
        return
    
    if args.status:
        status = check_usb_status(args.usb)
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return
    
    if args.run or args.capture or args.analyze:
        usb_path = args.usb or detect_usb_drive()
        
        if not usb_path:
            print("错误: 未检测到 U 盘，请使用 --usb 指定路径")
            return
        
        runner = USBAutoRunner(usb_path)
        
        if args.capture:
            runner.run_capture()
        elif args.analyze:
            runner.run_analyze()
        else:
            runner.run_full_cycle()
        return
    
    # 默认：检测并提示
    usb = detect_usb_drive()
    if usb:
        print(f"✓ U 盘已就绪: {usb}")
        status = check_usb_status(usb)
        print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
        print("未检测到 U 盘")
        print("\n使用方法:")
        print("  --detect    检测 U 盘")
        print("  --status     检查 U 盘状态")
        print("  --run        运行完整处理周期")


if __name__ == "__main__":
    main()
