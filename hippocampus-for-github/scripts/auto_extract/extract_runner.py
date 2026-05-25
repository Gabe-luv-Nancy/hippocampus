import sys
import yaml
from pathlib import Path
from datetime import datetime

# 导入 backup_engine（直接运行时用这个 import，直接 import 而非相对 import）
try:
    from .backup_engine import backup_file, BACKUP_ROOT
except ImportError:
    from backup_engine import backup_file, BACKUP_ROOT

BASE_SCHEMA_PATH = Path(__file__).parent / "base_schema.yaml"
USER_SCHEMA_PATH = Path(__file__).parent / "user_schema.yaml"
DRY_RUN = "--dry-run" in sys.argv

def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_schema_paths(schema: dict) -> set:
    """从 schema 中提取所有路径"""
    paths = set()
    for item in schema.get("paths", []):
        p = item.get("path", "")
        if p.startswith("~"):
            p = str(Path(p).expanduser())
        paths.add(p)
    return paths

def run_extract(dry_run: bool = False):
    """
    主流程：
    1. 加载 base_schema.yaml（官方路径）
    2. 加载 user_schema.yaml（用户实际路径）
    3. 差异 = user_paths - base_paths
    4. 对差异文件分类：new（全新）vs modified（同名的已修改文件）
    5. 执行备份（或 dry-run 预览）
    """
    print("=" * 50)
    print(f"HIPPO Auto-Extract  {'[DRY-RUN]' if dry_run else ''}")
    print("=" * 50)

    # 加载
    if not BASE_SCHEMA_PATH.exists():
        print(f"❌ base_schema.yaml 不存在: {BASE_SCHEMA_PATH}")
        return
    if not USER_SCHEMA_PATH.exists():
        print(f"❌ user_schema.yaml 不存在，请先运行 schema_generator.py")
        return

    base_schema = load_yaml(BASE_SCHEMA_PATH)
    user_schema = load_yaml(USER_SCHEMA_PATH)

    base_paths = get_schema_paths(base_schema)
    user_paths = get_schema_paths(user_schema)

    # 差异
    diff_paths = user_paths - base_paths
    print(f"\n📊 扫描结果：")
    print(f"   官方骨架路径：{len(base_paths)} 个")
    print(f"   用户实际路径：{len(user_paths)} 个")
    print(f"   差异（需备份）：{len(diff_paths)} 个")

    if not diff_paths:
        print("\n✅ 没有新文件需要备份")
        return

    print(f"\n📋 差异列表：")
    for p in sorted(diff_paths):
        print(f"   + {p}")

    if dry_run:
        print(f"\n🔍 DRY-RUN: 跳过备份（共 {len(diff_paths)} 个文件）")
        return

    # 执行备份
    backed_up = []
    for p_str in sorted(diff_paths):
        p = Path(p_str)
        if not p.exists():
            continue

        mode = "modified" if p.name in [Path(bp).name for bp in base_paths] else "new"
        try:
            result = backup_file(p, mode=mode)
            print(f"   ✅ {p.name} → {result.relative_to(BACKUP_ROOT.parent.parent)}")
            backed_up.append(p_str)
        except Exception as e:
            print(f"   ❌ {p.name}: {e}")

    print(f"\n✅ 完成！已备份 {len(backed_up)}/{len(diff_paths)} 个文件")
    print(f"📁 备份目录：{BACKUP_ROOT}")

if __name__ == "__main__":
    run_extract(dry_run=DRY_RUN)
