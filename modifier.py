import pandas as pd
import re
import os

dirname = os.path.split(__file__)[0]

class NameModifier():
    def __init__(self, system="other", engine="other", path=""):
        # ststem: BH,Liburdi,other(需要自定义csv名称转换文件)
        # engine: RR_RB211,GE_LM2500,other
        if engine == "RR":
            engine = "RR_RB211"
        if engine == "GE":
            engine = "GE_LM2500"
        # 自定义名称转换规则
        if (system != "BH" and system != "Liburdi") or (engine != "RR_RB211" and engine != "GE_LM2500"):
            if path == "":
                raise Exception("Path of configuration file is not provided!")
            df = pd.read_csv(path, encoding = 'gbk')
            df.rename(columns=lambda x: x.strip(),inplace=True)
            df.loc[0] = [x.strip() for x in list(df.loc[0])]
            dic = df.to_dict(orient='records')[0]
            self.__names = list(dic) # 字典中所有转换后的数据名
            # 反转字典
            self.__dic = dict(zip(dic.values(),dic.keys())) # 系统及燃机对应的字典
            self.__system = "other" # 检测系统
            self.__engine = "other" # 燃机型号
            return

        BH_RR_RB211,BH_GE_LM2500,Liburdi_RR_RB211,Liburdi_GE_LM2500 =self.__read_csv()
        self.__system = system # 检测系统
        self.__engine = engine # 燃机型号
        self.__dic_name = system + "_" + engine # 系统及燃机对应的字典的名字
        dic = eval(self.__dic_name) 
        self.__names = list(dic) # 字典中所有转换后的数据名
        # 反转字典
        self.__dic = dict(zip(dic.values(),dic.keys())) # 系统及燃机对应的字典
        # 不同系统数据间交集、并集数据名集合
        if engine == "RR_RB211":
            self.__name_union = set(BH_RR_RB211)|set(Liburdi_RR_RB211)
            self.__name_intersection = set(BH_RR_RB211) & set(Liburdi_RR_RB211)
        elif engine == "GE_LM2500":
            self.__name_union = set(BH_GE_LM2500)|set(Liburdi_GE_LM2500)
            self.__name_intersection = set(BH_GE_LM2500)&set(Liburdi_GE_LM2500)
        # 在交集、并集中添加平均值数据名
        union_add = []
        intersection_add = []
        for name in self.__name_union:
            if name[-1] == 'a':
                union_add.append(name[0:-1])
        for name in self.__name_intersection:
            if name[-1] == 'a':
                intersection_add.append(name[0:-1])
        self.__name_union = self.__name_union | set(union_add)
        self.__name_intersection = self.__name_intersection | set(intersection_add)

    # 读取配置文件(BH、Liburdi转换表)
    def __read_csv(self):
        df = pd.read_csv(dirname + "/Config/BH_RR_RB211.csv")
        BH_RR_RB211 = df.to_dict(orient='records')[0]
        df = pd.read_csv(dirname + "/Config/BH_GE_LM2500.csv")
        BH_GE_LM2500 = df.to_dict(orient='records')[0]
        df = pd.read_csv(dirname + "/Config/Liburdi_RR_RB211.csv")
        Liburdi_RR_RB211 = df.to_dict(orient='records')[0]
        df = pd.read_csv(dirname + "/Config/Liburdi_GE_LM2500.csv")
        Liburdi_GE_LM2500 = df.to_dict(orient='records')[0]
        return BH_RR_RB211,BH_GE_LM2500,Liburdi_RR_RB211,Liburdi_GE_LM2500

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
        data.rename(columns=lambda x: x.strip() if type(x) == str else x,inplace=True)
        data.rename(columns=self.__dic,inplace=True)
    
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
        # for i in range(len(data.index.values)):
        #     for j in range (len(data.columns.values)):
        #         if type(data.iat[i,j]) == str:
        # #           print(i,j,data.iat[i,j],type(data.iat[i,j]))
        #             data.iat[i,j] = -1

        data.replace(regex=r".*[a-zA-Z]+.*", value=-1, inplace=True)
        return data.apply(pd.to_numeric,errors = 'ignore')

    # 部分数据计算平均值（重命名之后）
    def avg_calculating(self,data):
        # 遍历所有数据名 找到需要计算平均值的数据（判断依据以'a'结尾）
        for name in data.columns.values:
            if name[-1] != 'a':
                #不是a结尾则跳过
                continue
            name = name[0:-1] #去掉末尾的a
            if name in data.columns.values:
                # 若平均值已存在，则无需计算平均
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

    # 不同系统数据间取交集或并集, 补全没有测量值的数据（用-1）
    def complement(self,data,mode = "original",tags=[]):
        empty_column = [-1 for i in range(len(data.index.values))] # 空列（-1）
        if tags != []:
            missing_names = set(tags)-set(data.columns.values)
            for name in missing_names:
                data[name] = empty_column

        if mode == "original":
            return data
        elif mode == "union":
            missing_names = set(self.__name_union)-set(data.columns.values)
            for name in missing_names:
                data[name] = empty_column
            return data
        elif mode == "intersection":
            names = []
            missing_names = []
            for name in self.__name_intersection:
                if name in data.columns.values:
                    names.append(name)
                else:
                    missing_names.append(name)
            data = data.loc[:,names]
            for name in missing_names:
                data[name] = empty_column
            return data
        else:
            raise Exception("Inexistent parameter! Error parameter: "+mode)

    # 筛选去除多测量值数据，只保留平均值（求平均值后使用，因为可能没有平均值）
    def filter(self,data,retain="ALL"):
        para = ["ALL","NONE","T"]
        if retain not in para:
            raise Exception("Inexistent parameter! Error parameter: "+retain)
        if retain == "ALL":
            return data
        columns_retained = [] # 需要保留的列的列名
        for name in data.columns.values: 
            if retain == 'T' and name[1] != 'T' and 'a' <= name[-1] <= 'z':
                continue  
            elif retain == 'NONE' and 'a' <= name[-1] <= 'z':
                continue 
            columns_retained.append(name)
        data_new = data.loc[:,columns_retained]
        return data_new

    # 根据数据名排序
    def sort(self,data):
        return data.sort_index(axis=1)

    # 根据转速筛选
    def rpm_filter(self,data,section = []):
        if section == []:
            if self.__engine == "RR_RB211":
                section = [8200, 9500]
            elif self.__engine == "GE_LM2500":
                section = [8200, 10000]
            else :
                raise Exception("Lack rpm range!")
        indexes = []
        for index,rmp in enumerate(data["3NH"]):
            if section[0] <= rmp <= section[1]:
                indexes.append(index)
        return data.iloc[indexes],indexes

    # 返回所需数据名（重命名前的）列表
    def listing(self):
        return list(self.__dic)

    def __call__(self, data, retain="ALL", section = []):
        retain_para = ["ALL","NONE","T"]
        if retain not in retain_para:
            raise Exception("Inexistent parameter! Error parameter: "+retain)
        indexes = data.index.to_list()
        # 列重命名
        self.rename(data)
        # 列切片
        new_data = self.slice_up(data)
        # 异常值处理
        new_data = self.missing_value_processing(new_data)
        # 多测量值数据的均值计算
        self.avg_calculating(new_data)
        # 筛选数据()
        new_data = self.filter(new_data,retain)
        # 根据数据名排序
        new_data = self.sort(new_data)
        # 根据转速筛选行
        new_data,indexes = self.rpm_filter(new_data,section)

        return new_data,indexes

def test():
    # NF = NameModifier("BH","RR_RB211")
    # df = pd.read_excel('../BH_RRtest.xlsx')

    # NF = NameModifier("BH","GE_LM2500")
    # df = pd.read_excel('../BH_GEtest.xlsx')

    # NF = NameModifier("Liburdi","RR_RB211")
    # df = pd.read_excel('../Liburdi_RRtest.xlsx')

    # NF = NameModifier("Liburdi","GE_LM2500")
    # df = pd.read_excel('../Liburdi_GEtest.xlsx')
    
    # new_df,index = NF(df,'ALL')
    # print("NF.listing():",NF.listing())
    # print(new_df)
    # new_df.to_excel('../output.xlsx')

# 自定义测试
    NF = NameModifier(path="../my_dic.csv")
    df = pd.read_excel('../中卫2015.xlsx')

    new_df,index = NF(df,'ALL',[8200, 9500])
    print("NF.listing():",NF.listing())
    print(new_df)
    new_df.to_excel('../output.xlsx')


if __name__ == "__main__":
    test()
    # writer = pd.ExcelWriter('data_name_conversion.xlsx')
    # df = pd.DataFrame(BH_RR_RB211,index=[0])
    # df.sort_index(axis=1).to_excel(writer,sheet_name="BH_RR_RB211")
    # df = pd.DataFrame(BH_GE_LM2500,index=[0])
    # df.sort_index(axis=1).to_excel(writer,sheet_name="BH_GE_LM2500")
    # df = pd.DataFrame(Liburdi_RR_RB211,index=[0])
    # df.sort_index(axis=1).to_excel(writer,sheet_name="Liburdi_RR_RB211")
    # df = pd.DataFrame(Liburdi_GE_LM2500,index=[0])
    # df.sort_index(axis=1).to_excel(writer,sheet_name="Liburdi_GE_LM2500")
    # writer.save()
    # writer.close()


    # dic = df.to_dict(orient='records')[0]
    # print(dic)