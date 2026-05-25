"""
AnswerSheet — 可验证填表明文范式 · 核心引擎
纯 Python 实现，零外部依赖
"""

import re
import hashlib
import yaml
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class VerifyMode(Enum):
    SUPERVISED = "supervised"
    INDUCTION = "induction"


@dataclass
class Module:
    """权限角色"""
    name: str
    role: str
    description: str = ""


@dataclass
class Slot:
    """填空位"""
    name: str
    module: str
    verify: VerifyMode = VerifyMode.SUPERVISED
    rule: Optional[str] = None
    value: Optional[str] = None


@dataclass
class AnswerEntry:
    """答案条目"""
    slot_name: str
    hash_type: str  # sha256, md5, plain
    hash_value: str


@dataclass
class AnswerSheet:
    """AnswerSheet 文件模型"""
    meta: dict
    modules: list
    slots: list
    body: str
    answers: list = field(default_factory=list)
    raw_content: str = ""


class ParseError(Exception):
    """解析错误"""
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(f"[{code}] {message}")


# ── 解析器 ──────────────────────────────────────────────

class AnswerSheetParser:
    """解析 AnswerSheet .md 文件"""

    SLOT_RE = re.compile(
        r'\{\{\s*slot:(\w+)\s*\|([^}]+)\}\}'
    )
    PARAM_RE = re.compile(r'(\w+)=([^,|]+)')  # 每个参数值会在后续 strip
    ANSWER_RE = re.compile(r'^\[(\w+)\]:\s*(\w+):(.+)$')

    def parse(self, content: str) -> AnswerSheet:
        """解析完整的 AnswerSheet 内容"""
        self.raw = content

        # 1. 提取 front matter
        fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not fm_match:
            raise ParseError("E001", "缺少 YAML front matter（需要 --- 包裹）")

        try:
            meta = yaml.safe_load(fm_match.group(1))
        except yaml.YAMLError as e:
            raise ParseError("E001", f"YAML 解析失败: {e}")

        if not isinstance(meta, dict):
            raise ParseError("E001", "front matter 必须是 YAML 对象")

        # 2. 校验必填字段
        if meta.get("answersheet") != "1.0":
            raise ParseError("E002", "缺少 answersheet: \"1.0\" 字段")
        if "title" not in meta:
            raise ParseError("E002", "缺少 title 字段")
        if "modules" not in meta or not meta["modules"]:
            raise ParseError("E002", "缺少 modules 字段")

        # 3. 解析 modules
        modules = []
        module_names = set()
        for m in meta["modules"]:
            if not isinstance(m, dict) or "name" not in m:
                raise ParseError("E002", f"module 格式错误: {m}")
            if m["name"] in module_names:
                raise ParseError("E004", f"重复的 module 名称: {m['name']}")
            module_names.add(m["name"])
            modules.append(Module(
                name=m["name"],
                role=m.get("role", ""),
                description=m.get("description", "")
            ))

        # 4. 提取正文和答案区
        body_start = fm_match.end()
        body_content = content[body_start:]

        answer_section_idx = body_content.find("<!-- answers -->")
        if answer_section_idx >= 0:
            body = body_content[:answer_section_idx]
            answer_text = body_content[answer_section_idx + len("<!-- answers -->"):]
        else:
            body = body_content
            answer_text = ""

        # 5. 解析 slots
        slots = []
        slot_names = set()
        for match in self.SLOT_RE.finditer(body):
            name = match.group(1)
            if name in slot_names:
                raise ParseError("E009", f"重复的 slot 名称: {name}")
            slot_names.add(name)

            params_str = match.group(2)
            params = {k: v.strip() for k, v in self.PARAM_RE.findall(params_str)}

            module_name = params.get("module", "")
            if module_name not in module_names:
                raise ParseError("E004", f"slot '{name}' 引用了未定义的 module: {module_name}")

            verify_str = params.get("verify", "supervised")
            try:
                verify = VerifyMode(verify_str)
            except ValueError:
                raise ParseError("E003", f"slot '{name}' 的 verify 值无效: {verify_str}")

            value = params.get("value", None)

            slots.append(Slot(
                name=name,
                module=module_name,
                verify=verify,
                rule=params.get("rule"),
                value=value,
            ))

        # 6. 解析答案区
        answers = []
        for line in answer_text.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            am = self.ANSWER_RE.match(line)
            if am:
                answers.append(AnswerEntry(
                    slot_name=am.group(1),
                    hash_type=am.group(2),
                    hash_value=am.group(3).strip(),
                ))

        return AnswerSheet(
            meta=meta,
            modules=modules,
            slots=slots,
            body=body,
            answers=answers,
            raw_content=content,
        )


# ── 验证器 ──────────────────────────────────────────────

class AnswerSheetValidator:
    """验证 AnswerSheet 文件"""

    def validate(self, sheet: AnswerSheet, actor_module: str = "") -> dict:
        """
        验证整个 AnswerSheet
        返回: {"valid": bool, "errors": [...], "warnings": [...]}
        """
        errors = []
        warnings = []

        # 检查 actor 权限
        module_names = {m.name for m in sheet.modules}
        if actor_module and actor_module not in module_names:
            errors.append(f"执行者 module '{actor_module}' 未在文件中定义")

        # 验证每个 slot
        for slot in sheet.slots:
            if slot.value is None:
                warnings.append(f"slot '{slot.name}' 尚未填写 (E008)")
                continue

            # 权限检查：跳过不属于自己的 slot（不报错）
            if actor_module and slot.module != actor_module:
                continue

            # 根据验证模式执行验证
            if slot.verify == VerifyMode.SUPERVISED:
                err = self._verify_supervised(slot, sheet.answers)
                if err:
                    errors.append(err)
            elif slot.verify == VerifyMode.INDUCTION:
                err = self._verify_induction(slot)
                if err:
                    errors.append(err)

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def _verify_supervised(self, slot: Slot, answers: list) -> Optional[str]:
        """有监督验证：对比 answer"""
        answer = next((a for a in answers if a.slot_name == slot.name), None)
        if answer is None:
            return f"slot '{slot.name}' (supervised) 找不到对应答案 (E007)"

        computed = self._hash(slot.value, answer.hash_type)
        if computed != answer.hash_value:
            return f"slot '{slot.name}' 验证失败：哈希不匹配 (E005)"
        return None

    def _verify_induction(self, slot: Slot) -> Optional[str]:
        """无监督验证：基于规则的归纳"""
        if not slot.rule:
            return None  # 无规则 = 不验证

        value = slot.value or ""
        rule = slot.rule

        # pattern:"<regex>"
        if rule.startswith("pattern:"):
            pattern = rule[len("pattern:"):].strip('"')
            if not re.match(pattern, value):
                return f"slot '{slot.name}' 归纳验证失败：不匹配 pattern {pattern} (E006)"
            return None

        # range:<min>-<max>
        if rule.startswith("range:"):
            try:
                parts = rule[len("range:"):].split("-")
                lo, hi = float(parts[0]), float(parts[1])
                val = float(value)
                if not (lo <= val <= hi):
                    return f"slot '{slot.name}' 归纳验证失败：{val} 不在范围 [{lo}, {hi}] (E006)"
            except (ValueError, IndexError):
                return f"slot '{slot.name}' range 规则格式错误: {rule}"
            return None

        # enum:<v1>,<v2>,...
        if rule.startswith("enum:"):
            allowed = rule[len("enum:"):].split(",")
            if value not in allowed:
                return f"slot '{slot.name}' 归纳验证失败：'{value}' 不在枚举 {allowed} 中 (E006)"
            return None

        # length:<min>-<max>
        if rule.startswith("length:"):
            try:
                parts = rule[len("length:"):].split("-")
                lo, hi = int(parts[0]), int(parts[1])
                if not (lo <= len(value) <= hi):
                    return f"slot '{slot.name}' 归纳验证失败：长度 {len(value)} 不在 [{lo}, {hi}] (E006)"
            except (ValueError, IndexError):
                return f"slot '{slot.name}' length 规则格式错误: {rule}"
            return None

        return None

    @staticmethod
    def _hash(value: str, algorithm: str) -> str:
        """计算哈希值"""
        if algorithm == "plain":
            return value
        if algorithm == "sha256":
            return hashlib.sha256(value.encode()).hexdigest()
        if algorithm == "md5":
            return hashlib.md5(value.encode()).hexdigest()
        return value


# ── Induction 引擎 ──────────────────────────────────────

class InductionEngine:
    """
    归纳引擎：从已验证实例中归纳出验证规则
    用于无监督模式下自动推断规则
    """

    def induce(self, values: list, rule_type: str = "auto") -> Optional[str]:
        """
        从已验证的值列表中归纳出规则
        rule_type: auto | pattern | range | enum | length
        """
        if not values:
            return None

        if rule_type == "auto":
            return self._auto_induce(values)
        if rule_type == "pattern":
            return self._induce_pattern(values)
        if rule_type == "range":
            return self._induce_range(values)
        if rule_type == "enum":
            return self._induce_enum(values)
        if rule_type == "length":
            return self._induce_length(values)
        return None

    def _auto_induce(self, values: list) -> Optional[str]:
        """自动推断最合适的规则类型"""
        # 尝试数值范围
        try:
            nums = [float(v) for v in values]
            if len(nums) >= 2:
                return self._induce_range(values)
        except ValueError:
            pass

        # 枚举值（种类少）
        unique = set(values)
        if len(unique) <= 10 and len(unique) < len(values):
            return self._induce_enum(values)

        # 字符串长度
        return self._induce_length(values)

    def _induce_range(self, values: list) -> str:
        """归纳数值范围"""
        nums = [float(v) for v in values]
        return f"range:{min(nums)}-{max(nums)}"

    def _induce_enum(self, values: list) -> str:
        """归纳枚举值"""
        unique = sorted(set(values))
        return f"enum:{','.join(unique)}"

    def _induce_length(self, values: list) -> str:
        """归纳字符串长度范围"""
        lengths = [len(v) for v in values]
        return f"length:{min(lengths)}-{max(lengths)}"

    def _induce_pattern(self, values: list) -> str:
        """归纳正则模式（简化版：取最长公共前缀+后缀）"""
        # 简化实现：检查是否全是数字、字母等
        if all(v.isdigit() for v in values):
            return 'pattern:"^\\d+$"'
        if all(v.isalpha() for v in values):
            return 'pattern:"^[a-zA-Z]+$"'
        # 默认：按长度约束
        return self._induce_length(values)


# ── 填表操作 ──────────────────────────────────────────────

class AnswerSheetFiller:
    """执行 fill-in 操作"""

    def fill(self, content: str, slot_name: str, value: str) -> str:
        """在内容中填充指定 slot"""
        pattern = re.compile(
            r'(\{\{\s*slot:' + re.escape(slot_name) + r'\s*\|)([^}]+)(\}\})'
        )
        match = pattern.search(content)
        if not match:
            raise ParseError("E003", f"找不到 slot: {slot_name}")

        params = match.group(2)
        # 如果已有 value，替换；否则追加
        if "value=" in params:
            new_params = re.sub(r'value=[^,|}]+', f'value={value}', params)
        else:
            new_params = params.rstrip() + f" | value={value}"

        return content[:match.start()] + match.group(1) + new_params + match.group(3) + content[match.end():]


# ── 便捷函数 ──────────────────────────────────────────────

def parse_file(filepath: str) -> AnswerSheet:
    """从文件路径解析 AnswerSheet"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return AnswerSheetParser().parse(f.read())


def validate_file(filepath: str, actor_module: str = "") -> dict:
    """解析并验证文件"""
    sheet = parse_file(filepath)
    return AnswerSheetValidator().validate(sheet, actor_module)
