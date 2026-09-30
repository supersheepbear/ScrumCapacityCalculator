# 使用演示 (Demo Walkthrough)

## 步骤 1: 启动应用

```bash
cd D:\repos\ScrumBoardTool
python app.py
```

应该看到:
```
============================================================
Scrum Capacity Calculator
============================================================

Starting server at http://localhost:5000

Press Ctrl+C to stop
============================================================
```

## 步骤 2: 打开配置编辑器

1. 在浏览器中打开: `http://localhost:5000`
2. 点击顶部的 **"⚙️ Open Config Editor"** 按钮
3. 你会看到一个友好的表单界面

## 步骤 3: 填写配置 (两种方式)

### 方式 A: 使用示例数据 (最快)

1. 点击 **"📋 Load Example"** 按钮
2. 表单会自动填充示例数据:
   - Sprint: 2024-Q1-Sprint-1 (Jan 8 - Jan 19)
   - 2 个团队成员 (张三, 李四)
   - 2 个办公地点 (Beijing, Shanghai)
   - 1 个 PTO 记录

### 方式 B: 手动输入

**Sprint Configuration:**
- Sprint Name: `2024-Q1-Sprint-1`
- Start Date: `2024-01-08`
- End Date: `2024-01-19`

**Team Members:**

成员 1:
- Name: `张三`
- Jira Username: `john.doe`
- Daily Hours: `8`
- Location: `Beijing`
- 点击 **"➕ Add Member"**

成员 2:
- Name: `李四`
- Jira Username: `jane.smith`
- Daily Hours: `6`
- Location: `Shanghai`
- 点击 **"➕ Add Member"**

**Office Locations:**

地点 1:
- Location Name: `Beijing`
- Country Code: `CN`
- 点击 **"➕ Add Location"**

地点 2:
- Location Name: `Shanghai`
- Country Code: `CN`
- 点击 **"➕ Add Location"**

**PTO (Time Off):**

PTO 1:
- Member Name: `张三`
- Date: `2024-01-10`
- Hours: `8`
- 点击 **"➕ Add PTO"**

## 步骤 4: 生成配置

点击 **"✨ Generate Configuration"** 按钮

系统会:
1. 验证所有输入
2. 生成 JSON 配置
3. 自动跳转到主页面
4. 配置已自动填入左侧文本框

## 步骤 5: 添加 Jira 数据

现在你需要 Jira CSV 数据。有两种方式:

### 方式 A: 使用演示数据

复制以下内容到 "Jira CSV Export" 文本框:

```csv
Issue Key,Summary,Assignee,Sprint,Estimate
PROJ-101,Login Feature,john.doe,2024-Q1-Sprint-1,30
PROJ-102,User Dashboard,john.doe,2024-Q1-Sprint-1,25
PROJ-103,API Integration,jane.smith,2024-Q1-Sprint-1,40
PROJ-104,Database Migration,john.doe,2024-Q1-Sprint-1,15
```

### 方式 B: 从 Jira 导出

1. 打开你的 Jira Sprint Board
2. 点击 "..." → Export → CSV
3. 确保包含这些列: Issue Key, Summary, Assignee, Sprint, Estimate
4. 复制整个 CSV 内容
5. 粘贴到文本框

## 步骤 6: 计算容量

点击 **"✨ Calculate Capacity"** 按钮

## 步骤 7: 查看结果

你会看到:

### Team Capacity Summary (团队容量汇总)
```
Total Capacity: 126.0h
Total Planned: 110.0h  
Average Load: 87.3%
Overloaded Members: 1
```

### Individual Results (个人结果)

**张三**
- Location: Beijing
- Capacity: 72.0h (9 working days × 8h)
- Planned: 70.0h
- Remaining: 2.0h
- Load: 97.2% 🟡 Warning

**李四**
- Location: Shanghai  
- Capacity: 54.0h (9 working days × 6h)
- Planned: 40.0h
- Remaining: 14.0h
- Load: 74.1% 🟢 Normal

### Warnings (警告)

如果有以下情况会显示警告:
- ⚠️ Unassigned Tasks (未分配的任务)
- ⚠️ Unestimated Tasks (未估算的任务)
- ⚠️ Unmatched Assignees (配置中没有的人员)

## 理解结果

### 状态指示器

- 🟢 **Normal** (正常): 负载率 < 80%
  - 团队成员有足够容量
  - 可以承担额外工作

- 🟡 **Warning** (警告): 负载率 80-100%
  - 团队成员接近满负荷
  - 需要关注，避免加班

- 🔴 **Overload** (超载): 负载率 > 100%
  - 团队成员超载！
  - **需要立即调整任务分配**
  - 或者减少任务范围

### 容量计算公式

```
工作日 = Sprint 天数 - 周末 - 公共假期 - PTO
容量(小时) = 工作日 × 每日工时
负载率 = 计划工时 / 容量工时 × 100%
```

### 示例计算: 张三

```
Sprint: 2024-01-08 到 2024-01-19 = 12 日历天
周末: 2024-01-13, 2024-01-14 = 2 天
PTO: 2024-01-10 = 1 天
工作日: 12 - 2 - 1 = 9 天
每日工时: 8 小时
容量: 9 × 8 = 72 小时
计划工作: 70 小时
负载率: 70 / 72 = 97.2% 🟡 接近满负荷
```

## 保存配置供将来使用

在配置编辑器页面:
1. 填写完所有信息
2. 点击 **"💾 Download as File"**
3. 保存 `team_config.json` 文件
4. 下次使用时，在主页面直接上传此文件

## 常见问题

### Q: 如何修改已生成的配置?
A: 返回配置编辑器 (点击 "⚙️ Open Config Editor")，重新填写表单

### Q: 可以添加多个 PTO 记录吗?
A: 可以！继续点击 "➕ Add PTO" 添加更多记录

### Q: 删除添加错的成员怎么办?
A: 每个添加的项目右侧都有 "Delete" 按钮

### Q: 如何处理半天休假?
A: PTO Hours 字段输入 `4` (而不是 `8`)

### Q: 系统如何知道公共假期?
A: 自动根据 Country Code 和日期范围获取该国的公共假期

### Q: 负载率超过 100% 意味着什么?
A: **成员超载了！** 需要:
- 减少任务
- 重新分配给其他成员
- 延长 Sprint 时间
- 或者接受加班

## 实际使用场景

### 场景 1: Sprint Planning
在 Sprint Planning 会议前:
1. 在配置编辑器中设置团队和 Sprint 日期
2. 从 Jira 导出候选任务
3. 计算容量
4. 根据结果调整任务分配

### 场景 2: 中途检查
Sprint 进行中:
1. 更新 PTO (有人临时请假)
2. 从 Jira 导出当前状态
3. 重新计算
4. 识别风险

### 场景 3: 多地点团队
不同国家的团队:
1. 添加所有办公地点 (Beijing, Bangalore, New York)
2. 系统自动处理各地假期
3. 每个成员按其所在地计算工作日

## 下一步

现在你已经知道如何使用系统了！

- 用真实数据试试
- 将此工具集成到你的 Sprint Planning 流程中
- 每个 Sprint 开始前检查容量
- 识别并解决超载问题

**祝你的 Sprint 顺利！** 🎯
