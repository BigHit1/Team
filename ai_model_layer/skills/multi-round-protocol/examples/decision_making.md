# 示例4: 需要决策

## 场景

在实现功能时发现多种可行方案，需要用户做出选择。

---

## 场景1: 技术方案选择

### 用户
```
优化角色移动系统的性能
```

### AI 响应

我分析了当前的移动系统，发现有两种优化方案：

**方案1: 使用 Character Movement Component**
- 优点：
  - UE5 官方组件，经过充分测试
  - 内置网络同步
  - 支持多种移动模式
- 缺点：
  - 功能较重，可能有不需要的开销
  - 自定义程度有限

**方案2: 自定义轻量级移动逻辑**
- 优点：
  - 完全控制，可以极致优化
  - 只实现需要的功能
  - 更轻量
- 缺点：
  - 需要自己实现网络同步
  - 开发时间更长
  - 需要更多测试

```yaml
---TASK_STATUS---
status: need_human
reason: 有两种优化方案，需要根据项目需求选择
intervention_type: decision
priority: high
question: |
  请选择移动系统优化方案：
  
  方案1: 使用 Character Movement Component（推荐）
    - 适合：需要网络同步、标准移动功能
    - 开发时间：短
  
  方案2: 自定义轻量级移动逻辑
    - 适合：单机游戏、极致性能要求
    - 开发时间：长
  
  您的项目是否需要网络同步？是否有极致性能要求？
options:
  - use_cmc: 使用 Character Movement Component
  - custom_light: 自定义轻量级逻辑
---END_STATUS---
```

---

## 场景2: 架构决策

### 用户
```
添加生命恢复系统
```

### AI 响应

我发现项目中已经有一个 `HealthComponent` 类，有两种实现方式：

**方案1: 扩展现有 HealthComponent**
```cpp
// 在现有 HealthComponent 中添加
UPROPERTY(EditAnywhere)
float HealthRegenRate = 5.0f;

void UHealthComponent::TickComponent(float DeltaTime, ...)
{
    // 添加恢复逻辑
    if (CurrentHealth < MaxHealth)
    {
        CurrentHealth += HealthRegenRate * DeltaTime;
    }
}
```

**方案2: 创建新的 HealthRegenComponent**
```cpp
// 创建独立的组件
UCLASS()
class UHealthRegenComponent : public UActorComponent
{
    UPROPERTY()
    UHealthComponent* HealthComponent;
    
    UPROPERTY(EditAnywhere)
    float RegenRate = 5.0f;
};
```

```yaml
---TASK_STATUS---
status: need_human
reason: 项目中已有 HealthComponent，需要确认实现方式
intervention_type: decision
priority: medium
question: |
  发现项目中已有 HealthComponent，请选择实现方式：
  
  方案1: 扩展现有 HealthComponent（推荐）
    优点：代码集中，易于维护
    缺点：需要修改现有代码
  
  方案2: 创建新的 HealthRegenComponent
    优点：不影响现有代码，职责分离
    缺点：需要管理两个组件的交互
  
  您更倾向于哪种方式？
options:
  - extend_existing: 扩展现有组件
  - create_new: 创建新组件
---END_STATUS---
```

---

## 场景3: 需要许可

### 用户
```
清理项目中未使用的资源
```

### AI 响应

我扫描了项目，发现以下未使用的资源：

- `Content/Textures/OldUI/` (15个文件，共 45MB)
- `Content/Materials/Deprecated/` (8个文件，共 12MB)
- `Content/Blueprints/Test/` (23个文件)

这些资源在代码中没有被引用。

```yaml
---TASK_STATUS---
status: need_human
reason: 需要确认是否删除未使用的资源
intervention_type: permission
priority: high
question: |
  发现以下未使用的资源，是否删除？
  
  1. Content/Textures/OldUI/ (15个文件，45MB)
  2. Content/Materials/Deprecated/ (8个文件，12MB)
  3. Content/Blueprints/Test/ (23个文件)
  
  总计可释放约 57MB 空间
  
  建议：先备份这些文件，确认无问题后再删除
risk_level: medium
recommended_action: 先移动到 Backup 文件夹，测试无问题后再删除
---END_STATUS---
```

---

## 场景4: 需要澄清

### 用户
```
添加角色技能系统
```

### AI 响应

我需要了解更多信息才能实现技能系统：

```yaml
---TASK_STATUS---
status: need_human
reason: 技能系统需求不够明确，需要澄清细节
intervention_type: clarification
priority: high
question: |
  请提供以下信息以便实现技能系统：
  
  1. 技能类型：
     - 主动技能（需要玩家触发）
     - 被动技能（自动生效）
     - 还是两者都有？
  
  2. 技能数量：
     - 每个角色有几个技能？
     - 是否支持技能切换/装备？
  
  3. 技能效果：
     - 伤害类（攻击敌人）
     - 增益类（提升属性）
     - 治疗类（恢复生命）
     - 还是其他？
  
  4. 冷却机制：
     - 是否需要冷却时间？
     - 是否需要消耗资源（如魔法值）？
  
  5. 是否使用 UE5 的 Gameplay Ability System (GAS)？
unclear_points:
  - 技能类型和数量
  - 技能效果范围
  - 冷却和资源消耗机制
  - 是否使用 GAS
---END_STATUS---
```

---

## 分析

### 何时使用 NEED_HUMAN？

| 情况 | 类型 | 优先级 |
|------|------|--------|
| 多种技术方案 | decision | high/medium |
| 修改关键代码 | permission | high |
| 删除文件/资源 | permission | high |
| 需求不明确 | clarification | high/medium |
| 发现潜在问题 | decision | medium |

### 关键点

1. **清晰的选项** - 列出所有可行方案
2. **优缺点分析** - 帮助用户做决策
3. **推荐方案** - 给出建议（如果有）
4. **风险评估** - 说明潜在风险
5. **明确问题** - 具体说明需要什么信息

---

## 用户响应后

### 用户选择方案1

```
使用 Character Movement Component
```

### AI 继续执行

好的，我将使用 Character Movement Component 进行优化。

[实现代码...]

```yaml
---TASK_STATUS---
status: completed
reason: 使用 Character Movement Component 完成移动系统优化
confidence: 0.9
files_modified: [...]
---END_STATUS---
```

---

## 最佳实践

### DO ✅

1. **提供足够信息** - 让用户能做出明智决策
2. **给出建议** - 基于经验推荐方案
3. **说明影响** - 每个选择的后果
4. **保持中立** - 不要强迫用户选择

### DON'T ❌

1. **不要猜测** - 不确定时一定要问
2. **不要隐藏风险** - 如实告知潜在问题
3. **不要过度询问** - 只问必要的问题
4. **不要做危险操作** - 删除/修改关键文件前必须询问

