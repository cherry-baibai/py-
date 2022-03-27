
import requests
import time
import pandas as pd
import os
import json
import warnings
#from wordcloud import WordCloud
import matplotlib.pyplot as plt
#爬取国家数据

agent={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
basepath='E:\大四上的迷迷茫茫\python大作业'
if not os.path.exists(basepath):
    os.mkdir(basepath)
warnings.filterwarnings('ignore')
baseurl='https://data.stats.gov.cn/easyquery.htm' #基本请求网页url，后续加参数的模板，且是唯一的模板
dbcode,wdcode,rowcode,colcode='hgnd','zb','zb','sj'
def retry(url,params,headers):
    while True:
        try:
            req=requests.get(url,params=params,headers=headers,verify=False)
            req.encoding = req.apparent_encoding #解码后一切正常,防止出现乱码现象
            trans_dict=json.loads(req.text)
            break
        except:
            time.sleep(2)
            print('服务器繁忙')
    return trans_dict
#定义爬取函数
def packcsv(valuecode,path):
    base_can={'m':'QueryData','dbcode':dbcode,'rowcode':rowcode,'colcode':colcode,
              'wds':'[]','dfwds':'[{"wdcode":"zb","valuecode":"%s"},{"wdcode":"sj","valuecode":"2000-2019"}]'%valuecode,
              'k1':str(int(time.time()*1000))}
    trans_dict=retry(baseurl,base_can,agent)
    row_loc=trans_dict['returndata']['wdnodes'][0]['nodes']
    print(row_loc)
    print('*****************')
    totaldata=trans_dict['returndata']['datanodes'] #totaldata由code;data(data,dotcount,hasdata,strdata);wds(两个valuecode和wdcode构成)
    frame_dict={each['code']:pd.DataFrame(columns=['年份',each['cname']]) for each in row_loc}#提取字段编号相应的中文，每一字段编号对应一个由年份和中文名生成的空dataframe，后续不同的列可以merge在一起
    #frame_dict = {'A0G0K01': Empty DataFrame
#Columns: [年份, 新注册民用汽车拥有量]
#Index: [], 'A0G0K02': Empty DataFrame
#Columns: [年份, 新注册民用载客汽车拥有量]
#Index: []....} 
    for i in totaldata:
        match_year=int(i['wds'][1]['valuecode']) #获取整数年份
        match_code=i['wds'][0]['valuecode'] #获得字段编码
        match_row=list(frame_dict[match_code].columns)[-1] #通过frame_dict获得中文名字
        if i['data']['hasdata']:
            match_data=i['data']['data'] #获取数据，（年拥有量）
        else:
            match_data=float('nan') #有数据则取，无数据则为nan
        eachcsv=frame_dict[match_code]
        eachcsv=eachcsv.append({'年份':match_year,match_row:match_data},ignore_index=True)
        frame_dict[match_code]=eachcsv
    for i in frame_dict:#frame_dict生成完毕，循环merge成一个大的dataframe
        try:
            csv=pd.merge(csv,frame_dict[i],how='outer',on=['年份'])
        except NameError:
            csv=frame_dict[i]
    csv['年份']=csv['年份'].astype("int64")
    csv.to_csv(path,index=False)#保存文件


code_path={'zb':basepath}
while code_path:
    each_root={}
    for each in code_path:
        add_can={'id':each,'dbcode':dbcode,'wdcode':wdcode,'m':'getTree'}
        root_req=retry(baseurl,add_can,agent) #第二次调用retry函数
        for i in root_req: #爬取所有最外层的父标题和子标题
            if (i['name'] =='运输和邮电' or i['name'] =='新注册民用汽车数量'):
                rootname=i['name'].replace('/','每')
                idsign=i['id']
                makedir=code_path[each]+'\\'+rootname
                if i['isParent']:
                    if not os.path.exists(makedir):
                        os.mkdir(makedir)
                        print('已创建路径%s'%makedir)
                    else:
                        print('已有路径%s'%makedir)
                    each_root[idsign]=makedir
                else:
                    print('正在写表,对应路径为%s'%(makedir+'.csv'))
                    packcsv(idsign,makedir+'.csv')
                    print('写表完成')
    code_path=each_root


# （第一个图）每年新增的车辆数的图
import numpy as np
with open('E:\大四上的迷迷茫茫\python大作业\运输和邮电\新注册民用汽车数量.csv','r',encoding='utf-8') as data:
    ls = [line.strip().split(',') for line in data]
    ls = ls[:19][:]
#print(ls)
#解决中文编码问题
plt.rcParams['font.sans-serif'] = ['KaiTi'] # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题

print([(x[0],sum(map(float,x[1:]))) for x in ls[1:]])
every_year_add = [sum(map(float,x[1:])) for x in ls[1:]] #建立在每一年的新增的车辆的总和；纵坐标
year = list(range(2002,2020,1))#创建横坐标
every_year_add.reverse()
plt.plot(year,every_year_add)
plt.xticks(year,year)
plt.xlabel('年份')
plt.ylabel('每年新注册的车辆数（万辆）')
plt.show()


#（第二个图）开始第二个图啦~2002-2019年新增注册车总和
import numpy as np
import matplotlib.pyplot as plt
with open('E:\大四上的迷迷茫茫\python大作业\运输和邮电\新注册民用汽车数量.csv','r',encoding='utf-8') as data:
    ls = [line.strip().split(',') for line in data]
    ls = ls[:19][:]
every_type_add = []
#构建纵坐标，每种类型各年增加的数量
for i in range(1,13):
    summ = 0
    for x in ls[1:]:
        summ += float(x[i])
    every_type_add.append(summ)
plt.rcParams['font.sans-serif'] = ['KaiTi'] # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
add_type = [ls[0][1:]] #横坐标，各个车的种类
for index, i in enumerate(add_type[0]):
    add_type[0][index] = add_type[0][index].replace('拥有量','').replace('新注册','')
    print(add_type[0][index])
#开始作图啦~
#plt.bar(np.arange(1,13,1),np.asarray(every_type_add),alpha=0.5)
plt.bar(add_type[0],every_type_add,alpha=0.5)
plt.xticks(fontsize=6)
#plt.xticks(list(range(1,13)),add_type)
plt.ylim(0,28000)
plt.xlabel('新注册的车的类型')
plt.ylabel('2002-2019年新增注册车总和')
plt.show()



#（第三个图）占比的饼子

with open('E:\大四上的迷迷茫茫\python大作业\运输和邮电\新注册民用汽车数量.csv','r',encoding='utf-8') as data:
    ls = [line.strip().split(',') for line in data]
    ls = ls[:19][:]
#print([(x[0],sum(map(float,x[1:]))) for x in ls[1:]])

every_year_add_2019 = [sum(map(float,ls[1][1:]))] #2019年车的总和
every_year_add_2002 = [sum(map(float,ls[18][1:]))] #2009年车的总和

label = [ls[0][1:]] #横坐标，各个车的种类
for index, i in enumerate(label[0]): #使add_type 成为饼状图的标签['汽车', '载客汽车', '大型载客汽车', '中型载客汽车',...) 12个
    label[0][index] = label[0][index].replace('拥有量','').replace('新注册','').replace('民用','')

data_in_2019 = [float(x) for x in ls[1][1:]] #构建2019和2009的所有数据,删除过年份了哦
data_in_2002 = [int(float(x)) for x in ls[18][1:]]
print(data_in_2002)
explode = [0, 0, -0.2, 0,0,0,0,0.2,0,0,0,-0.4] #顺时针转到，移出来
plt.rcParams['font.family']='SimHei' #让中文正常显示
#开始画图了~
fig,axes=plt.subplots(1,2)
axes[0].pie(data_in_2019,labels=label[0],explode=explode,autopct='%1.2f%%',textprops={'fontsize':8,'color':'black'}) #绘制2019年的图
axes[0].set_title('2019年各类民用汽车新注册拥有量')

axes[1].pie(data_in_2002,labels=label[0],explode=explode,autopct='%1.2f%%',textprops={'fontsize':8,'color':'black'})
axes[1].set_title('2002年各类民用汽车新注册拥有量')
plt.show()

#想画一个雷达图，以新注册民用汽车拥有量逐年的变化为例子
import numpy as np
with open('E:\大四上的迷迷茫茫\python大作业\运输和邮电\新注册民用汽车数量.csv','r',encoding='utf-8') as data:
    ls = [line.strip().split(',') for line in data]
    ls = ls[:19][:]
car_have_every_year = []
for x in ls[1:]:
    car_have_every_year.append(float(x[1]))
feature = list(range(2002,2020,1))
car_have_every_year.reverse() #和年份匹配的 ’新注册民用汽车拥有量‘的各个年份的增长数量
angles=np.linspace(0, 2*np.pi,len(feature), endpoint=False) # 设置每个数据点的显示位置，在雷达图上用角度表示
# 拼接数据首尾，使图形中线条封闭
values=np.concatenate((car_have_every_year,[car_have_every_year[0]]))
angles=np.concatenate((angles,[angles[0]]))
feature=np.concatenate((feature,[feature[0]]))
# 用于正常显示中文
plt.rcParams['font.sans-serif'] = 'SimHei'
#用于正常显示符号
plt.rcParams['axes.unicode_minus'] = False
# 绘图
fig = plt.figure()
# 设置为极坐标格式
ax = fig.add_subplot(111, polar=True)
# 绘制折线图
ax.plot(angles, values, 'o-', linewidth=2)
# 填充颜色
ax.fill(angles, values, alpha=0.25)
# 设置图标上的角度划分刻度，为每个数据点处添加标签
ax.set_thetagrids(angles * 180 / np.pi,feature)
#添加标题
plt.title('新注册民用汽车拥有量逐年的变化')
# 添加网格线
ax.grid(True)
plt.show()









