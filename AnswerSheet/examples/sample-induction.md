---
answersheet: "1.0"
title: "产品需求调研表（无监督模式示例）"
modules:
  - name: pm
    role: creator
    description: "产品经理，创建调研表"
  - name: user
    role: filler
    description: "受访用户"
  - name: analyst
    role: reviewer
    description: "数据分析师"
created: "2026-05-12"
---

# 产品需求调研表

## 用户信息

年龄段：{{ slot:age_group | module=user, verify=induction, rule=enum:18-25,26-35,36-45,46-55 }}
使用频率：{{ slot:usage_freq | module=user, verify=induction, rule=enum:每天,每周几次,每月几次,很少用 }}

## 需求评估

满意度评分(1-10)：{{ slot:satisfaction | module=user, verify=induction, rule=range:1-10 }}
推荐意愿(1-10)：{{ slot:recommend | module=user, verify=induction, rule=range:1-10 }}

## 开放反馈

最想要的改进：{{ slot:improvement | module=user, verify=induction, rule=pattern:"^.{5,500}$" }}

## 分析结论

整体评估：{{ slot:conclusion | module=analyst, verify=induction }}
