# NameModifier
一个用来更改数据名的小程序
### 一. 功能：
###### 已实现
- 对数据进行重命名并进行筛选
- 将异常数据置为-1
- 对多测量值的数据计算平均值
- 去交集或并集并进行补全（用-1）
- 输出中只保留数据平均值
- 数据排序
- 根据转速对数据进行筛选

### 二. 实例化：

```python
NF = NameModifier("Liburdi","GE_LM2500")
```

|  参数  | 说明  |
|  ----  | ----  |
| system| 检测系统 (BH / Liburdi) | 
| engine| 燃机型号 (RR_RB211 / GE_LM2500) |

*注：engine参数也可以用(RR/GE)
### 三. 调用：
输入输出类型均为pandas的dataframe
```python
    df = pd.read_excel('Liburdi_GEtest.xlsx')
    new_df = NF(df,'ALL')
    new_df.to_excel('output.xlsx')
```
参数1为输入数据  
参数2见方法6`filter(data,retain)`
### 四. 方法：
#### 1. `rename(data)`
根据字典对数据进行**重命名**  
（修改原数据，无返回值）
#### 2. `slice(data)`
对数据进行**切片**只保留字典中存在的数据
#### 3. `missing_value_processing(data)`
**处理异常数据**，将所有类型为`str`的数据置为-1
（修改原数据，无返回值）
#### 4. `avg_calculating(data)`
根据列表对有多个测量值的数据**计算平均值**，将其作为一列新数据  
（修改原数据，无返回值）
#### 5. `complement(data，mode)`
不同系统测量值之间**取交集或并集**，使用-1补全没有进行监测的数据，使不同系统以及燃机型号的输出数据一致
| mode 参数值  | 说明  |
|  ----  | ----  |
| original  | (默认)原始数据 |
| union  | 取交集 |
| intersection  | 取并集 |
#### 6. `filter(data,retain)`
对数据进行切片，多测量值的数据**只保留平均值** 

| retain 参数值  | 说明  |
|  ----  | ----  |
| ALL  | (默认)所有数据全部保留 |
| NONE  | 全部多测量值数据只保留平均值 |
| T  | 温度之外的多测量值数据只保留平均值 |
#### 7. `sort(data)`
根据数据名对列进行**排序**
#### 8. `rpm_filter(data,section)`
根据**转速筛选**行
| 参数 section  |
|  ----  |
| 一个长度为2的列表，前一个值为下限，后一个值为上限，闭区间。|
| 例：[100,200] |



#### 9. `listing()`
返回会被保留的数据（即excel中存在已知意义的数据）重命名前的名字列表