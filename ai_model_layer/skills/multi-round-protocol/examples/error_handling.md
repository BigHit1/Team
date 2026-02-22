# 示例3: 错误处理

## 场景

在实现功能时遇到编译错误，需要识别、报告并修复。

---

## 对话流程

### 用户
```
请在 MyCharacter 中添加生命恢复功能
```

---

### AI 第1轮：初次实现（有错误）

好的，我来添加生命恢复功能。

```cpp
// MyCharacter.cpp
void AMyCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    // 生命恢复
    if (CurrentHealth < MaxHealth)
    {
        CurrentHealth += HealthRegenRate * DeltaTime;
    }
}
```

已添加生命恢复逻辑。

```yaml
---TASK_STATUS---
status: waiting
waiting_for: compile_result
reason: 等待编译结果以验证代码正确性
timeout: 300
next_action: 根据编译结果决定是否需要修复
---END_STATUS---
```

---

### 系统
```
编译失败：
MyCharacter.cpp(45): error C2065: 'HealthRegenRate' : undeclared identifier
```

---

### AI 第2轮：识别错误

收到编译错误，我来分析。

```yaml
---TASK_STATUS---
status: error
error_type: compile
error_message: |
  MyCharacter.cpp(45): error C2065: 'HealthRegenRate' : undeclared identifier
error_location:
  file: Source/MyProject/Characters/MyCharacter.cpp
  line: 45
root_cause: 在 .cpp 文件中使用了 HealthRegenRate 变量，但忘记在 .h 文件中声明
suggested_fix: 在 MyCharacter.h 中添加 UPROPERTY() float HealthRegenRate = 5.0f;
can_auto_fix: true
---END_STATUS---
```

---

### 用户
```
修复它
```

---

### AI 第3轮：修复错误

好的，我来修复这个问题。

```cpp
// MyCharacter.h
UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()
    
public:
    // 现有代码...
    
    // 生命恢复速率（每秒）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Health")
    float HealthRegenRate = 5.0f;
};
```

已在头文件中添加 HealthRegenRate 声明。

```yaml
---TASK_STATUS---
status: waiting
waiting_for: compile_result
reason: 等待重新编译以验证修复是否成功
timeout: 300
next_action: 如果编译成功则标记为完成，如果失败则继续修复
---END_STATUS---
```

---

### 系统
```
编译成功！
```

---

### AI 第4轮：确认完成

太好了，编译成功！

```yaml
---TASK_STATUS---
status: completed
reason: 成功添加生命恢复功能并修复了编译错误
confidence: 0.95
files_modified:
  - Source/MyProject/Characters/MyCharacter.h
  - Source/MyProject/Characters/MyCharacter.cpp
changes_summary: |
  - 在 MyCharacter.h 中添加 HealthRegenRate 属性
  - 在 MyCharacter.cpp 的 Tick 中实现生命恢复逻辑
  - 修复了未声明标识符的编译错误
---END_STATUS---
```

---

## 分析

### 错误处理流程

```
实现代码 → waiting
    ↓
收到错误 → error（分析原因）
    ↓
修复代码 → waiting
    ↓
编译成功 → completed
```

### 关键点

1. **主动等待** - 使用 waiting 状态等待编译结果
2. **详细分析** - error 状态包含完整的错误信息
3. **明确修复** - 提供具体的修复方案
4. **验证修复** - 再次等待编译验证

---

## 其他错误类型示例

### 逻辑错误

```yaml
---TASK_STATUS---
status: error
error_type: logic
error_message: 生命值可能超过最大值
root_cause: 恢复逻辑没有检查上限
suggested_fix: 使用 FMath::Min(CurrentHealth + Regen, MaxHealth)
can_auto_fix: true
---END_STATUS---
```

### 运行时错误

```yaml
---TASK_STATUS---
status: error
error_type: runtime
error_message: Assertion failed: HealthComponent != nullptr
error_location:
  file: MyCharacter.cpp
  line: 67
root_cause: HealthComponent 未初始化就被使用
suggested_fix: 在使用前添加空指针检查
can_auto_fix: true
---END_STATUS---
```

### 语法错误

```yaml
---TASK_STATUS---
status: error
error_type: syntax
error_message: expected ';' before '}' token
error_location:
  file: MyCharacter.cpp
  line: 89
root_cause: 缺少分号
suggested_fix: 在第88行末尾添加分号
can_auto_fix: true
---END_STATUS---
```

---

## 无法自动修复的情况

```yaml
---TASK_STATUS---
status: error
error_type: compile
error_message: |
  无法找到 CustomHealthSystem.h 头文件
root_cause: 项目中不存在 CustomHealthSystem 模块
suggested_fix: |
  需要以下操作之一：
  1. 创建 CustomHealthSystem 模块
  2. 使用其他现有的健康系统
  3. 实现自定义的健康逻辑
can_auto_fix: false
requires_decision: true
---END_STATUS---
```

此时应该转为 `need_human` 状态：

```yaml
---TASK_STATUS---
status: need_human
reason: 缺少必要的模块，需要决定如何处理
intervention_type: decision
priority: high
question: |
  项目中不存在 CustomHealthSystem 模块，请选择：
  1. 创建新的 CustomHealthSystem 模块
  2. 使用 UE5 内置的 Gameplay Ability System
  3. 实现简单的自定义健康逻辑
options:
  - create_module: 创建新模块
  - use_gas: 使用 GAS
  - custom_simple: 简单自定义
---END_STATUS---
```

