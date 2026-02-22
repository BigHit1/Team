# 示例2: 复杂任务（多轮执行）

## 场景

用户请求实现一个完整的库存系统，包括数据结构、管理逻辑和 UI 界面。

---

## 对话流程

### 用户
```
请实现一个完整的库存系统，包括：
1. 物品数据结构
2. 库存管理逻辑
3. UI 界面
```

---

### AI 第1轮：创建数据结构

我来开始实现库存系统。首先创建物品数据结构。

```cpp
// InventoryItem.h
USTRUCT(BlueprintType)
struct FInventoryItem
{
    GENERATED_BODY()
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString ItemName;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 Quantity;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    UTexture2D* Icon;
};
```

已创建基础的物品数据结构。

```yaml
---TASK_STATUS---
status: continue
reason: 完成了物品数据结构定义，需要继续实现库存管理逻辑
progress: 0.3
completed_parts:
  - 创建 FInventoryItem 结构体
  - 定义物品基础属性（名称、数量、图标）
next_part: 创建 InventoryComponent 实现库存管理逻辑
estimated_rounds: 2
---END_STATUS---
```

---

### 用户
```
继续
```

---

### AI 第2轮：实现管理逻辑

现在实现库存管理组件。

```cpp
// InventoryComponent.h
UCLASS()
class UInventoryComponent : public UActorComponent
{
    GENERATED_BODY()
    
public:
    UFUNCTION(BlueprintCallable)
    bool AddItem(const FInventoryItem& Item);
    
    UFUNCTION(BlueprintCallable)
    bool RemoveItem(const FString& ItemName, int32 Quantity);
    
    UFUNCTION(BlueprintCallable)
    TArray<FInventoryItem> GetAllItems() const;
    
private:
    UPROPERTY()
    TArray<FInventoryItem> Items;
    
    UPROPERTY(EditAnywhere)
    int32 MaxSlots = 20;
};
```

```cpp
// InventoryComponent.cpp
bool UInventoryComponent::AddItem(const FInventoryItem& Item)
{
    // 查找是否已存在
    for (auto& ExistingItem : Items)
    {
        if (ExistingItem.ItemName == Item.ItemName)
        {
            ExistingItem.Quantity += Item.Quantity;
            return true;
        }
    }
    
    // 检查空间
    if (Items.Num() >= MaxSlots)
    {
        return false;
    }
    
    // 添加新物品
    Items.Add(Item);
    return true;
}

bool UInventoryComponent::RemoveItem(const FString& ItemName, int32 Quantity)
{
    for (int32 i = 0; i < Items.Num(); i++)
    {
        if (Items[i].ItemName == ItemName)
        {
            Items[i].Quantity -= Quantity;
            if (Items[i].Quantity <= 0)
            {
                Items.RemoveAt(i);
            }
            return true;
        }
    }
    return false;
}

TArray<FInventoryItem> UInventoryComponent::GetAllItems() const
{
    return Items;
}
```

已实现库存管理逻辑。

```yaml
---TASK_STATUS---
status: continue
reason: 完成了库存管理逻辑，需要继续实现 UI 界面
progress: 0.6
completed_parts:
  - 创建 InventoryComponent 类
  - 实现添加物品功能
  - 实现移除物品功能
  - 实现获取物品列表功能
  - 添加最大槽位限制
next_part: 创建 UMG UI 界面显示库存
estimated_rounds: 1
---END_STATUS---
```

---

### 用户
```
继续
```

---

### AI 第3轮：创建 UI

现在创建 UI 界面。

```cpp
// InventoryWidget.h
UCLASS()
class UInventoryWidget : public UUserWidget
{
    GENERATED_BODY()
    
public:
    UFUNCTION(BlueprintCallable)
    void RefreshInventory(UInventoryComponent* InventoryComp);
    
protected:
    UPROPERTY(meta = (BindWidget))
    UScrollBox* ItemList;
    
    UPROPERTY(EditAnywhere)
    TSubclassOf<UUserWidget> ItemSlotWidgetClass;
};
```

```cpp
// InventoryWidget.cpp
void UInventoryWidget::RefreshInventory(UInventoryComponent* InventoryComp)
{
    if (!InventoryComp || !ItemList)
    {
        return;
    }
    
    // 清空现有列表
    ItemList->ClearChildren();
    
    // 获取所有物品
    TArray<FInventoryItem> Items = InventoryComp->GetAllItems();
    
    // 为每个物品创建 UI
    for (const auto& Item : Items)
    {
        if (ItemSlotWidgetClass)
        {
            UUserWidget* SlotWidget = CreateWidget<UUserWidget>(this, ItemSlotWidgetClass);
            if (SlotWidget)
            {
                // 设置物品数据（需要在 ItemSlotWidget 中实现）
                ItemList->AddChild(SlotWidget);
            }
        }
    }
}
```

库存系统实现完成！

```yaml
---TASK_STATUS---
status: completed
reason: 完整实现了库存系统，包括数据结构、管理逻辑和 UI 界面
confidence: 0.9
files_modified:
  - Source/MyProject/Inventory/InventoryItem.h
  - Source/MyProject/Inventory/InventoryComponent.h
  - Source/MyProject/Inventory/InventoryComponent.cpp
  - Source/MyProject/UI/InventoryWidget.h
  - Source/MyProject/UI/InventoryWidget.cpp
changes_summary: |
  - 创建 FInventoryItem 数据结构
  - 实现 InventoryComponent 管理逻辑
    - AddItem: 添加物品（支持堆叠）
    - RemoveItem: 移除物品
    - GetAllItems: 获取所有物品
    - 最大槽位限制
  - 创建 InventoryWidget UI 界面
    - 动态刷新物品列表
    - 使用 ScrollBox 显示
next_steps:
  - 创建 ItemSlotWidget 显示单个物品
  - 添加拖拽功能
  - 添加物品详情显示
---END_STATUS---
```

---

## 分析

### 为什么使用多轮？

1. **任务复杂** - 包含多个子系统
2. **逻辑分层** - 数据 → 逻辑 → UI
3. **便于验证** - 每轮可以单独验证
4. **避免过长** - 单次响应不会太长

### 进度追踪

| 轮次 | 进度 | 完成内容 |
|------|------|----------|
| 第1轮 | 30% | 数据结构 |
| 第2轮 | 60% | 管理逻辑 |
| 第3轮 | 100% | UI 界面 |

### 关键点

1. **清晰的进度** - 每轮都说明完成了什么
2. **明确的下一步** - 告诉用户接下来做什么
3. **合理的估计** - 预计还需要几轮
4. **最终总结** - 完成时提供完整的变更说明

---

## 变体：如果中途遇到问题

### 第2轮遇到决策问题

```yaml
---TASK_STATUS---
status: need_human
reason: 发现项目中已有 ActorComponent，需要确认是否复用
intervention_type: decision
priority: medium
question: |
  发现项目中已有 BaseComponent 类，是否：
  1. 继承 BaseComponent（保持一致性）
  2. 直接继承 UActorComponent（更简单）
options:
  - inherit_base: 继承 BaseComponent
  - inherit_actor: 继承 UActorComponent
---END_STATUS---
```

