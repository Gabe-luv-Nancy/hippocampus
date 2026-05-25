#!/usr/bin/env python3
"""
AnswerSheet CLI — 命令行工具
用法: python cli.py <command> <file> [options]
"""

import sys
import argparse
from answersheet import (
    AnswerSheetParser, AnswerSheetValidator,
    AnswerSheetFiller, InductionEngine, parse_file
)


def cmd_validate(args):
    """验证 AnswerSheet 文件"""
    try:
        sheet = parse_file(args.file)
        validator = AnswerSheetValidator()
        result = validator.validate(sheet, actor_module=args.module or "")
        
        print(f"📄 文件: {args.file}")
        print(f"📌 标题: {sheet.meta.get('title', 'N/A')}")
        print(f"👤 Modules: {', '.join(m.name for m in sheet.modules)}")
        print(f"📝 Slots: {len(sheet.slots)} 个")
        
        filled = sum(1 for s in sheet.slots if s.value is not None)
        print(f"✍️  已填写: {filled}/{len(sheet.slots)}")
        
        supervised = [s for s in sheet.slots if s.verify.value == "supervised"]
        induction = [s for s in sheet.slots if s.verify.value == "induction"]
        print(f"🔒 有监督: {len(supervised)} | 🧪 无监督(induction): {len(induction)}")
        
        print()
        if result["valid"]:
            print("✅ 验证通过")
        else:
            print("❌ 验证失败:")
            for err in result["errors"]:
                print(f"   • {err}")
        
        if result["warnings"]:
            print("⚠️  警告:")
            for w in result["warnings"]:
                print(f"   • {w}")
        
        return 0 if result["valid"] else 1
    except Exception as e:
        print(f"❌ 解析错误: {e}")
        return 2


def cmd_fill(args):
    """填充 slot"""
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filler = AnswerSheetFiller()
        new_content = filler.fill(content, args.slot, args.value)
        
        with open(args.file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ 已填充 slot '{args.slot}' = '{args.value}'")
        return 0
    except Exception as e:
        print(f"❌ 填充失败: {e}")
        return 2


def cmd_verify(args):
    """验证单个 slot 的填写值"""
    try:
        sheet = parse_file(args.file)
        validator = AnswerSheetValidator()
        result = validator.validate(sheet, actor_module=args.module or "")
        
        # 找到目标 slot
        slot = next((s for s in sheet.slots if s.name == args.slot), None)
        if not slot:
            print(f"❌ 找不到 slot: {args.slot}")
            return 2
        
        print(f"📝 Slot: {slot.name}")
        print(f"🔒 Module: {slot.module}")
        print(f"📊 验证模式: {slot.verify.value}")
        print(f"📋 规则: {slot.rule or '无'}")
        print(f"✍️  值: {slot.value or '未填写'}")
        
        # 检查这个 slot 是否有错误
        slot_errors = [e for e in result["errors"] if args.slot in e]
        if slot_errors:
            print("❌ 验证失败:")
            for e in slot_errors:
                print(f"   • {e}")
            return 1
        elif slot.value is None:
            print("⚠️  尚未填写")
            return 1
        else:
            print("✅ 验证通过")
            return 0
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 2


def cmd_induce(args):
    """从已验证实例归纳规则"""
    import os
    
    values = []
    for f in args.files:
        try:
            sheet = parse_file(f)
            for slot in sheet.slots:
                if slot.name == args.slot and slot.value is not None:
                    values.append(slot.value)
        except Exception:
            continue
    
    if not values:
        print(f"❌ 没有找到 slot '{args.slot}' 的已填写值")
        return 2
    
    engine = InductionEngine()
    rule = engine.induce(values, args.rule_type)
    
    print(f"📊 收集到 {len(values)} 个值: {values[:10]}{'...' if len(values) > 10 else ''}")
    print(f"🧪 归纳规则: {rule or '无法归纳'}")
    return 0


def cmd_info(args):
    """显示文件信息"""
    try:
        sheet = parse_file(args.file)
        print(f"📄 文件: {args.file}")
        print(f"📌 标题: {sheet.meta.get('title', 'N/A')}")
        print(f"📝 版本: {sheet.meta.get('version', 'N/A')}")
        print(f"📅 创建: {sheet.meta.get('created', 'N/A')}")
        print()
        
        print("👤 Modules:")
        for m in sheet.modules:
            print(f"   • {m.name} ({m.role}) — {m.description}")
        print()
        
        print("📝 Slots:")
        for s in sheet.slots:
            status = f"= \"{s.value}\"" if s.value else "(空)"
            rule_str = f", rule={s.rule}" if s.rule else ""
            print(f"   • {s.name}: module={s.module}, verify={s.verify.value}{rule_str} {status}")
        
        if sheet.answers:
            print()
            print("🔑 答案区:")
            for a in sheet.answers:
                print(f"   • [{a.slot_name}]: {a.hash_type}:{a.hash_value[:20]}...")
        
        return 0
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 2


def main():
    parser = argparse.ArgumentParser(
        description="AnswerSheet — 可验证填表明文范式 CLI"
    )
    sub = parser.add_subparsers(dest="command", help="子命令")
    
    # validate
    p_val = sub.add_parser("validate", help="验证文件")
    p_val.add_argument("file", help="AnswerSheet .md 文件路径")
    p_val.add_argument("-m", "--module", help="以指定 module 身份验证")
    
    # fill
    p_fill = sub.add_parser("fill", help="填充 slot")
    p_fill.add_argument("file", help="文件路径")
    p_fill.add_argument("-s", "--slot", required=True, help="slot 名称")
    p_fill.add_argument("-v", "--value", required=True, help="填写值")
    
    # verify
    p_ver = sub.add_parser("verify", help="验证单个 slot")
    p_ver.add_argument("file", help="文件路径")
    p_ver.add_argument("slot", help="slot 名称")
    p_ver.add_argument("-m", "--module", help="以指定 module 身份验证")
    
    # induce
    p_ind = sub.add_parser("induce", help="从多个实例归纳规则")
    p_ind.add_argument("slot", help="slot 名称")
    p_ind.add_argument("files", nargs="+", help="多个 AnswerSheet 文件")
    p_ind.add_argument("-t", "--rule-type", default="auto",
                       choices=["auto", "pattern", "range", "enum", "length"],
                       help="规则类型 (默认 auto)")
    
    # info
    p_info = sub.add_parser("info", help="显示文件信息")
    p_info.add_argument("file", help="文件路径")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    commands = {
        "validate": cmd_validate,
        "fill": cmd_fill,
        "verify": cmd_verify,
        "induce": cmd_induce,
        "info": cmd_info,
    }
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
