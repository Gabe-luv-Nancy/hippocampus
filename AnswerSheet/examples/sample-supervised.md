---
answersheet: "1.0"
title: "学生考试成绩单（有监督模式示例）"
modules:
  - name: teacher
    role: creator
    description: "出卷教师，创建答案"
  - name: student
    role: filler
    description: "答题学生"
created: "2026-05-12"
---

# 学生考试成绩单

## 基本信息

学生姓名：{{ slot:student_name | module=student }}
学号：{{ slot:student_id | module=student }}

## 考试成绩

语文：{{ slot:chinese_score | module=teacher, verify=supervised }}
数学：{{ slot:math_score | module=teacher, verify=supervised }}
英语：{{ slot:english_score | module=teacher, verify=supervised }}

## 教师评语

{{ slot:comment | module=teacher, verify=induction, rule=pattern:"^.{10,200}$" }}

<!-- answers -->
[chinese_score]: plain:92
[math_score]: plain:88
[english_score]: plain:95
