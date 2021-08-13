from name_dic import BH_RR_RB211,BH_GE_LM2500,Liburdi_RR_RB211,Liburdi_GE_LM2500
from name_dic import BH_RR_RB211_error,BH_GE_LM2500_error,Liburdi_RR_RB211_error,Liburdi_GE_LM2500_error
from name_dic import BH_RR_RB211_avg,BH_GE_LM2500_avg,Liburdi_RR_RB211_avg,Liburdi_GE_LM2500_avg
import pandas as pd
import re

class NameModifier():
    def __init__(self, system, engine):
        # ststem: BH,Liburdi
        if system != "BH" and system != "Liburdi":
            raise Exception("Inexistent system name! Error name: "+system)
        # engine: RR_RB211,GE_LM2500
        if engine == "RR":
            engine = "RR_RB211"
        if engine == "GE":
            engine = "GE_LM2500"
        if engine != "RR_RB211" and engine != "GE_LM2500":
            raise Exception("Inexistent engine name! Error name: "+engine)
        self.__system = system # 检测系统
        self.__engine = engine # 燃机型号
        self.__dic_name = system + "_" + engine # 系统及燃机对应的字典的名字
        dic = eval(self.__dic_name) 
        errdic = eval(self.__dic_name + "_error")
        self.__names = list(dic) # 字典中所有转换后的数据名
        # 反转字典
        self.__dic = dict(zip(dic.values(),dic.keys())) # 系统及燃机对应的字典
        self.__errdic = dict(zip(errdic.values(),errdic.keys())) # 系统及燃机对应的补漏字典
        self.__avgdic = eval(self.__dic_name + "_avg") # 系统及燃机对应的均值字典
        # 所有系统及燃机对应的所有数据名
        if engine == "RR_RB211":
            self.__name_union = set(BH_RR_RB211)|set(Liburdi_RR_RB211)|\
                        set(BH_RR_RB211_avg)|set(Liburdi_RR_RB211_avg)
            self.__name_intersection = ( set(BH_RR_RB211)|set(BH_RR_RB211_avg) )&\
                        ( set(Liburdi_RR_RB211)|set(Liburdi_RR_RB211_avg) )
        elif engine == "GE_LM2500":
            self.__name_union = set(BH_GE_LM2500)|set(Liburdi_GE_LM2500)|\
                        set(BH_GE_LM2500_avg)|set(Liburdi_GE_LM2500_avg)
            self.__name_intersection = ( set(BH_GE_LM2500)|set(BH_GE_LM2500_avg) )&\
                        ( set(Liburdi_GE_LM2500)|set(Liburdi_GE_LM2500_avg) )

    # Liburdi数据前缀处理
    def __Liburdi_prefix_processing(self,data):
        # Liburdi的数据名存在标识地名与机器的前缀，需先删除
        names = data.columns.values
        names_new = []
        for name in names:
            name = re.sub(r"^[0-9A-Za-z]+\.","",name)
            name = re.sub(r"^unit[0-9]+\.","",name)
            names_new.append(name)
        data.columns = names_new

    # 数据重命名
    def rename(self,data):
        # Liburdi的数据需要先删除前缀
        if self.__system == "Liburdi":
            self.__Liburdi_prefix_processing(data)

        # 根据字典修改列名
        data.rename(columns=self.__dic,inplace=True)
        # 根据可能出现的命名错误的字典再次修改列名
        data.rename(columns=self.__errdic,inplace=True)
    
    # 只保留进行了重命名的数据(即已知意义的数据)
    def slice_up(self,data):
        # 选取列
        columns_retained = [] # 需要保留的列的列名
        for name in data.columns.values: 
            if name in self.__names:
                columns_retained.append(name)
        data_new = data.loc[:,columns_retained]
        return data_new

    # 异常值处理（置为-1）
    def missing_value_processing(self,data):
        # 异常数值修改为 -1 （判断标准：类型为str）
        for i in range(len(data.index.values)):
            for j in range (len(data.columns.values)):
                if type(data.iat[i,j]) == str:
                    data.iat[i,j] = -1

    # 部分数据计算平均值
    def avg_calculating(self,data):
        # 遍历所有可能需要计算平均值的数据名
        for name in self.__avgdic:
            if name in data.columns.values:
                # 该数据平均值存在 或 只有唯一测量值，无需计算平均
                continue    
            # 该数据的所有测量值的数据名
            names = [name+i for i in list(map(chr, range(97,123)))
                    if name+i in data.columns.values]
            if len(names) == 0:
                # 该数据的任何测量值店都不存在，无需计算平均
                continue
            data[name] = [0]*len(data.index.values)
            for i in names:
                data[name] += data[i]
            data[name]/=len(names)    

    # 补全没有测量值的数据（用-1）
    def complement(self,data):
        empty_column = [-1 for i in range(len(data.index.values))]
        names = set(self.__name_union)-set(data.columns.values)
        print(names)
        for name in names:
            data[name] = empty_column

    # 筛选去除多测量值数据，只保留平均值
    def filter(self,data,retain):
        para = ["ALL","NONE","T"]
        if retain not in para:
            raise Exception("Inexistent parameter! Error parameter: "+retain)
        if retain == "ALL":
            return data
        columns_retained = [] # 需要保留的列的列名
        for name in data.columns.values: 
            if retain == 'T' and name[0] != 'T' and 'a' <= name[-1] <= 'z':
                continue  
            elif retain == 'NONE' and 'a' <= name[-1] <= 'z':
                continue 
            columns_retained.append(name)
        data_new = data.loc[:,columns_retained]
        return data_new

    # 根据数据名排序
    def sort(self,data):
        return data.sort_index(axis=1)

    def __call__(self, data, retain="ALL"):
        para = ["ALL","NONE","T"]
        if retain not in para:
            raise Exception("Inexistent parameter! Error parameter: "+retain)
        # 列重命名
        self.rename(data)
        # 列切片
        new_data = self.slice_up(data)
        # 异常值处理
        self.missing_value_processing(new_data)
        # 多测量值数据的均值计算
        self.avg_calculating(new_data)
        # 不同系统测量值之间取并集，并用-1补全没有的数据
        self.complement(new_data)
        # 筛选数据
        new_data = self.filter(new_data,retain)
        # # 根据数据名排序
        new_data = self.sort(new_data)


        # print(self.__name_union)
        # print(self.__name_intersection)
        # columns_retained = [] # 需要保留的列的列名
        # for name in self.__name_intersection: 
        #     if 'a' <= name[-1] <= 'z':
        #         continue
        #     columns_retained.append(name)
        # print(columns_retained)

        return new_data


if __name__ == "__main__":
    # NF = NameModifier("BH","RR_RB211")
    # NF = NameModifier("BH","GE_LM2500")
    NF = NameModifier("Liburdi","RR_RB211")
    # NF = NameModifier("Liburdi","GE_LM2500")
    
    # df = pd.read_excel('BH_RRtest.xlsx')
    # df = pd.read_excel('BH_GEtest.xlsx')
    df = pd.read_excel('Liburdi_RRtest.xlsx')
    # df = pd.read_excel('Liburdi_GEtest.xlsx')
    
    new_df = NF(df,'ALL')
    print(new_df)
    new_df.to_excel('output.xlsx')



# 两两取交集（同种e）
# 取个并集   GE: 17  RR: 12