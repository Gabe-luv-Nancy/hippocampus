"""
Cline 任务执行器

用于自动化调用 Windows 上的 Cline (GLM-5) 执行代码任务
"""

import subprocess
import os
import json
import time
from typing import Optional, Dict, Any


# PowerShell 路径
POWERSHELL = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"


class ClineRunner:
    """
    Cline 任务执行器
    
    用于在我的环境中通过 PowerShell 调用 Windows 上的 Cline
    """
    
    def __init__(self, workspace: str = None):
        """
        初始化
        
        Args:
            workspace: 工作目录，默认为 X:\\LOTT
        """
        # 默认工作目录
        if workspace is None:
            self.workspace = "X:\\LOTT"
        else:
            self.workspace = workspace
            
        self.powershell = POWERSHELL
    
    def _run_command(self, cmd: str, timeout: int = 300) -> Dict[str, Any]:
        """
        运行 PowerShell 命令
        
        Args:
            cmd: 命令字符串
            timeout: 超时时间（秒）
            
        Returns:
            结果字典
        """
        try:
            result = subprocess.run(
                [self.powershell, "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Timeout",
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": str(e)
            }
    
    def ask(self, prompt: str, timeout: int = 600) -> Dict[str, Any]:
        """
        发送任务给 Cline 执行
        
        Args:
            prompt: 任务描述（完整的提示词）
            timeout: 超时时间（秒）
            
        Returns:
            执行结果
        """
        # 转义引号
        escaped_prompt = prompt.replace('"', '\\"')
        
        # 构建命令
        cmd = f'cd /d {self.workspace}; cline ask "{escaped_prompt}"'
        
        print(f"[ClineRunner] 执行任务: {prompt[:80]}...")
        
        result = self._run_command(cmd, timeout)
        
        if result["success"]:
            print(f"[ClineRunner] 任务完成")
        else:
            print(f"[ClineRunner] 任务失败: {result.get('error', 'unknown')}")
        
        return result
    
    def check_status(self) -> Dict[str, Any]:
        """检查 Cline 状态"""
        result = self._run_command("cline --version")
        return result


# ==================== 便捷函数 ====================

def run_cline_task(prompt: str, workspace: str = "X:\\LOTT", timeout: int = 600) -> Dict[str, Any]:
    """
    快速执行 Cline 任务
    
    Args:
        prompt: 任务描述
        workspace: 工作目录
        timeout: 超时时间
        
    Returns:
        执行结果
    """
    runner = ClineRunner(workspace)
    return runner.ask(prompt, timeout)


# ==================== 测试 ====================

if __name__ == "__main__":
    # 测试
    runner = ClineRunner()
    
    # 检查状态
    print("检查 Cline 状态...")
    status = runner.check_status()
    print(f"状态: {status}")
