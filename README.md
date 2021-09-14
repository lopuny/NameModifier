# NameModifier
一个用来更改数据名的小程序
### 一. 功能：
- 对数据进行重命名并进行筛选,保留进行过重命名的数据
- 将异常数据置为-1
- 对多测量值的数据计算平均值
- 取交集或并集并用-1进行补全（不适用于自定义转换）
- 输出中只保留数据平均值
- 数据根据名称排序
- 根据转速对数据进行筛选

### 二. 实例化：

```python
NF = NameModifier("Liburdi","GE_LM2500")
```

|  参数  | 说明  |
|  ----  | ----  |
| system| 检测系统 (BH / Liburdi / other) | 
| engine| 燃机型号 (RR_RB211 / GE_LM2500 / other) |
| path| 配置文件路径 |

* system和engine只要不是前两个就默认other,空着也行  
* 只要两个有一个是other就需要自定义配置文件  
* 自定义配置文件需要path  
* engine参数也可以使用(RR / GE)代替(RR_RB211 / GE_LM2500)

|  实例变量  | 说明  |
|  ----  | ----  |
|__system (str) | 检测系统 | 
|__engine (str) | 燃机型号 |
|__dic_name (str) | 系统+燃机对应的配置文件名 |
|__names (list) | 所有名称转换后的数据名 |
|__dic (dic) | 名称转换字典(键：转换前数据名 值：转换后数据名) |
|__name_union (set) | 不同系统所采集的数据取交集 |
|__name_intersection (set) | 不同系统所采集的数据取并集 |


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
根据名称转换字典`self._dic`对数据进行重命名
（修改原数据，无返回值）
#### 2. `slice(data)`
对数据进行切片只保留字典中存在的数据(保留`self._names`中存在的数据)
#### 3. `missing_value_processing(data)`
处理异常数据，将所有类型为`str`的数据置为-1  
若数字被存为str类型则此方法会将其转换为数字类型  
（修改原数据，无返回值）
#### 4. `avg_calculating(data)`
根据列表对有多个测量值的数据计算平均值，将其作为一列新数据。  
自定义名称转换时需注意，此方法的逻辑是计算名称最后为小写字母并且前缀相同的数据的平均值。  
例：7Ta、7Tb、7Tc、……  求得平均值记为7T  
（修改原数据，无返回值）
#### 5. `complement(data，mode)`
不同系统测量值之间取交集或并集，使用-1补全没有进行监测的数据，使不同系统以及燃机型号的输出数据一致  
（自定义转换无法使用）
| mode 参数值  | 说明  |
|  ----  | ----  |
| original  | (默认)原始数据 |
| union  | 取交集 |
| intersection  | 取并集 |
#### 6. `filter(data,retain)`
对数据进行切片，多测量值的数据只保留平均值  
判断依据是不以小写字母结尾则保留  
| retain 参数值  | 说明  |
|  ----  | ----  |
| ALL  | (默认)所有数据全部保留 |
| NONE  | 全部多测量值数据只保留平均值 |
| T  | 温度之外的多测量值数据只保留平均值 |
#### 7. `sort(data)`
根据数据名对列进行排序
#### 8. `rpm_filter(data,section)`
根据转速筛选行
| 参数 section  
  ---- 
一个长度为2的列表，前一个值为下限，后一个值为上限，闭区间
例：[100,200]
RR_RB211 默认[8200, 9500]
GE_LM2500 默认[8200, 10000]   
#### 9. `listing()`
返回会被保留的数据（即excel中存在已知意义的数据）重命名前的名称列表  
（这方法一般情况下用不上）