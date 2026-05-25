"""
AnswerSheet 核心逻辑单元测试
"""

import hashlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from answersheet import (
    AnswerSheetParser, AnswerSheetValidator,
    AnswerSheetFiller, InductionEngine,
    ParseError, VerifyMode, parse_file
)


# ── 测试用的 AnswerSheet 内容 ──────────────────────

VALID_SHEET = """---
answersheet: "1.0"
title: "测试表"
modules:
  - name: teacher
    role: creator
  - name: student
    role: filler
---

# 测试表

姓名：{{ slot:name | module=student }}
成绩：{{ slot:score | module=teacher, verify=supervised }}
班级：{{ slot:class | module=student, verify=induction, rule=pattern:"^[甲乙丙]班$" }}

<!-- answers -->
[score]: plain:95
"""

SUPERVISED_FILLED = """---
answersheet: "1.0"
title: "测试表"
modules:
  - name: teacher
    role: creator
  - name: student
    role: filler
---

# 测试表

姓名：{{ slot:name | module=student, verify=induction | value=张三 }}
成绩：{{ slot:score | module=teacher, verify=supervised | value=95 }}
班级：{{ slot:class | module=student, verify=induction, rule=pattern:"^[甲乙丙]班$" | value=甲班 }}

<!-- answers -->
[score]: plain:95
"""

SUPERVISED_FAIL = """---
answersheet: "1.0"
title: "测试表"
modules:
  - name: teacher
    role: creator
  - name: student
    role: filler
---

# 测试表

成绩：{{ slot:score | module=teacher, verify=supervised | value=60 }}

<!-- answers -->
[score]: plain:95
"""


class TestParser(unittest.TestCase):
    """解析器测试"""

    def setUp(self):
        self.parser = AnswerSheetParser()

    def test_parse_valid(self):
        """正常解析"""
        sheet = self.parser.parse(VALID_SHEET)
        self.assertEqual(sheet.meta["title"], "测试表")
        self.assertEqual(len(sheet.modules), 2)
        self.assertEqual(len(sheet.slots), 3)
        self.assertEqual(len(sheet.answers), 1)

    def test_parse_slots(self):
        """slot 解析正确"""
        sheet = self.parser.parse(VALID_SHEET)
        slots = {s.name: s for s in sheet.slots}
        
        self.assertEqual(slots["name"].module, "student")
        self.assertEqual(slots["name"].verify, VerifyMode.SUPERVISED)  # 默认值
        
        self.assertEqual(slots["score"].module, "teacher")
        self.assertEqual(slots["score"].verify, VerifyMode.SUPERVISED)
        
        self.assertEqual(slots["class"].module, "student")
        self.assertEqual(slots["class"].verify, VerifyMode.INDUCTION)
        self.assertEqual(slots["class"].rule, 'pattern:"^[甲乙丙]班$"')

    def test_parse_filled_value(self):
        """已填写的 slot 解析"""
        sheet = self.parser.parse(SUPERVISED_FILLED)
        slots = {s.name: s for s in sheet.slots}
        self.assertEqual(slots["name"].value, "张三")
        self.assertEqual(slots["score"].value, "95")
        self.assertEqual(slots["class"].value, "甲班")

    def test_no_front_matter(self):
        """缺少 front matter 报错"""
        with self.assertRaises(ParseError) as ctx:
            self.parser.parse("没有front matter的内容")
        self.assertIn("E001", str(ctx.exception))

    def test_missing_answersheet_field(self):
        """缺少 answersheet 字段"""
        content = """---
title: "测试"
modules:
  - name: a
    role: b
---
正文"""
        with self.assertRaises(ParseError) as ctx:
            self.parser.parse(content)
        self.assertIn("E002", str(ctx.exception))

    def test_undefined_module(self):
        """slot 引用未定义的 module"""
        content = """---
answersheet: "1.0"
title: "测试"
modules:
  - name: teacher
    role: creator
---
{{ slot:x | module=hacker }}
"""
        with self.assertRaises(ParseError) as ctx:
            self.parser.parse(content)
        self.assertIn("E004", str(ctx.exception))

    def test_duplicate_slot(self):
        """重复 slot 名称"""
        content = """---
answersheet: "1.0"
title: "测试"
modules:
  - name: a
    role: b
---
{{ slot:x | module=a }}
{{ slot:x | module=a }}
"""
        with self.assertRaises(ParseError) as ctx:
            self.parser.parse(content)
        self.assertIn("E009", str(ctx.exception))


class TestValidator(unittest.TestCase):
    """验证器测试"""

    def setUp(self):
        self.parser = AnswerSheetParser()
        self.validator = AnswerSheetValidator()

    def test_supervised_pass(self):
        """有监督验证通过"""
        sheet = self.parser.parse(SUPERVISED_FILLED)
        result = self.validator.validate(sheet, "teacher")
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)

    def test_supervised_fail(self):
        """有监督验证失败"""
        sheet = self.parser.parse(SUPERVISED_FAIL)
        result = self.validator.validate(sheet, "teacher")
        self.assertFalse(result["valid"])
        self.assertTrue(any("E005" in e for e in result["errors"]))

    def test_induction_pass(self):
        """无监督归纳验证通过"""
        sheet = self.parser.parse(SUPERVISED_FILLED)
        result = self.validator.validate(sheet, "student")
        # class slot value=甲班, rule=pattern:^[甲乙丙]班$
        # name slot 没有验证模式
        slot_errors = [e for e in result["errors"] if "class" in e]
        self.assertEqual(len(slot_errors), 0)

    def test_induction_fail(self):
        """无监督归纳验证失败"""
        content = """---
answersheet: "1.0"
title: "测试"
modules:
  - name: student
    role: filler
---
班级：{{ slot:class | module=student, verify=induction, rule=pattern:"^[甲乙丙]班$" | value=丁班 }}
"""
        sheet = self.parser.parse(content)
        result = self.validator.validate(sheet, "student")
        self.assertFalse(result["valid"])
        self.assertTrue(any("E006" in e for e in result["errors"]))

    def test_unfilled_warning(self):
        """未填写的 slot 产生警告"""
        sheet = self.parser.parse(VALID_SHEET)
        result = self.validator.validate(sheet)
        self.assertTrue(any("E008" in w for w in result["warnings"]))

    def test_wrong_module(self):
        """不同 module 只能验证自己负责的 slot"""
        sheet = self.parser.parse(SUPERVISED_FILLED)
        result = self.validator.validate(sheet, "student")
        # student 不负责 score (teacher的)，但有 name 和 class
        # student 没有 answer 可以验证，所以不应该有越权错误
        # 只验证自己的 slots
        self.assertTrue(result["valid"])


class TestInduction(unittest.TestCase):
    """归纳引擎测试"""

    def setUp(self):
        self.engine = InductionEngine()

    def test_auto_range(self):
        """自动归纳数值范围"""
        rule = self.engine.induce(["10", "20", "30", "40"])
        self.assertEqual(rule, "range:10.0-40.0")

    def test_auto_enum(self):
        """自动归纳枚举值"""
        rule = self.engine.induce(
            ["甲班", "乙班", "甲班", "丙班", "乙班", "甲班"]
        )
        self.assertTrue(rule.startswith("enum:"))

    def test_auto_length(self):
        """自动归纳字符串长度"""
        rule = self.engine.induce(["abc", "hello", "world"])
        self.assertEqual(rule, "length:3-5")

    def test_explicit_pattern(self):
        """显式 pattern 归纳"""
        rule = self.engine.induce(["123", "456", "789"], "pattern")
        self.assertIn("pattern:", rule)

    def test_empty_values(self):
        """空值列表"""
        rule = self.engine.induce([])
        self.assertIsNone(rule)


class TestFiller(unittest.TestCase):
    """填表操作测试"""

    def setUp(self):
        self.filler = AnswerSheetFiller()

    def test_fill_slot(self):
        """填充 slot"""
        content = """---
answersheet: "1.0"
title: "测试"
modules:
  - name: student
    role: filler
---
姓名：{{ slot:name | module=student }}
"""
        result = self.filler.fill(content, "name", "张三")
        self.assertIn("value=张三", result)

    def test_fill_nonexistent_slot(self):
        """填充不存在的 slot"""
        content = """---
answersheet: "1.0"
title: "测试"
modules:
  - name: a
    role: b
---
正文"""
        with self.assertRaises(ParseError):
            self.filler.fill(content, "nope", "值")

    def test_fill_overwrite(self):
        """覆盖已填写的 slot"""
        content = """---
answersheet: "1.0"
title: "测试"
modules:
  - name: a
    role: b
---
姓名：{{ slot:name | module=a | value=旧值 }}
"""
        result = self.filler.fill(content, "name", "新值")
        self.assertIn("value=新值", result)
        self.assertNotIn("旧值", result)


class TestHashVerification(unittest.TestCase):
    """哈希验证测试"""

    def setUp(self):
        self.parser = AnswerSheetParser()
        self.validator = AnswerSheetValidator()

    def test_sha256_match(self):
        """SHA-256 验证通过"""
        value = "95"
        h = hashlib.sha256(value.encode()).hexdigest()
        content = f"""---
answersheet: "1.0"
title: "测试"
modules:
  - name: teacher
    role: creator
---
成绩：{{{{ slot:score | module=teacher, verify=supervised | value={value} }}}}

<!-- answers -->
[score]: sha256:{h}
"""
        sheet = self.parser.parse(content)
        result = self.validator.validate(sheet, "teacher")
        self.assertTrue(result["valid"])

    def test_md5_match(self):
        """MD5 验证通过"""
        value = "100"
        h = hashlib.md5(value.encode()).hexdigest()
        content = f"""---
answersheet: "1.0"
title: "测试"
modules:
  - name: teacher
    role: creator
---
成绩：{{{{ slot:score | module=teacher, verify=supervised | value={value} }}}}

<!-- answers -->
[score]: md5:{h}
"""
        sheet = self.parser.parse(content)
        result = self.validator.validate(sheet, "teacher")
        self.assertTrue(result["valid"])


if __name__ == "__main__":
    unittest.main()
