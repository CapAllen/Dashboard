# -*- coding: utf-8 -*-
# import requests
import pymysql
import pandas as pd
import numpy as np

from sqlalchemy import create_engine
from example.commons import Faker
from pyecharts import options as opts
from pyecharts.components import Image
from pyecharts.options import ComponentTitleOpts
from pyecharts.charts import Bar, Line, Pie, Boxplot, Timeline, Sankey, Graph

from jinja2 import Markup

def get_data(test=False):
    '''
    Get Data From MySQL DataBase.
    Return:
    user_info(DataFrame):Users' Information;
    user_zhiyuan(DataFrame):Users' Direct&Volunteer;
    df(DataFrame):user_info concatenate user_zhiyuan.
    '''    
    if test:
        engine = create_engine('sqlite:///Doc/FakeDatasets.db')
        df_test = pd.read_sql_table(table_name='FakeDatasets',con=engine)
        return df_test
    config = {'host':'192.168.10.117',
              'user':'username',
              'password':'password'}
    connection = pymysql.connect(**config)
    #用户信息
    usermodel_cols = ['openid','date_joined','nickname','avatarUrl','sex','school','category','is_filled','score','university']
    usermodel = pd.read_sql('select * from miniprogram.login_usermodel',con=connection)[usermodel_cols]
    
    verify_cols = ['openid','mobile', 'counter', 'sport_counter','add_time']
    verify = pd.read_sql('select * from miniprogram.login_verifycode',con=connection)[verify_cols]
    #取重复值中最后一次填写的手机号
    drop_idxes = []
    for openid in verify[verify['openid'].duplicated()]['openid']:
        openid_df = verify[verify['openid']==openid]
        max_time = np.array(openid_df['add_time']).max()
        drop_index = list(openid_df[openid_df['add_time'] != max_time].index)
        drop_idxes = drop_idxes+drop_index
    verify = verify.drop(drop_idxes)    
    user_info = pd.concat([usermodel.set_index('openid'),verify.set_index('openid')],axis=1,sort=True).reset_index().rename(columns={'index':'openid'})
    user_info = user_info.replace('',np.NaN)
    #添加初中所在区
    school_dict = pd.read_excel('./Doc/middle_school_location.xlsx')
    school_dict = dict(zip(school_dict['school'],school_dict['region']))
    user_info['区'] = user_info['school'].apply(lambda x: school_dict.get(x))
    
    #定向志愿填写情况
    direct = pd.read_sql('select * from miniprogram.recommend_directschoolrank',con=connection)[['openid','highschool','juniormiddleschool']]
    direct = direct[~direct['openid'].str.contains('mock')]
    
    #统招志愿填写情况
    def dict2name(x):
        try:
            return(eval(x)['name'])
        except:
            return(np.NaN)
    volunteer = pd.read_sql('select * from miniprogram.recommend_personalvolunteer',con=connection).drop('id',axis=1)
    volunteer[['volunteer_1', 'volunteer_2', 'volunteer_3', 'volunteer_4','volunteer_5']]=\
    volunteer[['volunteer_1', 'volunteer_2', 'volunteer_3', 'volunteer_4','volunteer_5']].applymap(dict2name)
    
    user_zhiyuan = pd.concat([direct.set_index('openid'),volunteer.set_index('openid')],axis=1,sort=True).reset_index().rename(columns={'index':'openid'})
    user_zhiyuan = user_zhiyuan.replace('',np.NaN)
    
    #合并
    df = pd.concat([user_info.set_index('openid'),user_zhiyuan.set_index('openid')],axis=1,sort=True).reset_index().rename(columns={'index':'openid'})
    df['sex'] = df['sex'].map({'1':'男','2':'女'})
    #筛选日期
    df = df[df['date_joined'] > '2019-07-29']
    #分日分时
    df['date_joined_'] = df['date_joined'].dt.strftime('%m-%d-%H')

    return df

def filter_data(df,district,school_name):
    #筛选区域
    df_district = df[df['区']==district]
    #选择学校
    if school_name != '所有初中':
        df_district = df_district[df_district['school']==school_name]
    return df_district

def count_users(df):
    #浏览人数
    scan_user = df.shape[0]
    #注册用户
    subscribers = df.query('is_filled==1').shape[0]
    #黑名单用户
    blacklist = df.query('(counter>3)|(sport_counter>3)').shape[0]
    #定向志愿填写用户
    direct_users = df['highschool'].notna().sum()
    #统招志愿填写用户
    volunteer_users = df[['volunteer_1', 'volunteer_2', 'volunteer_3', 'volunteer_4','volunteer_5']].dropna(how='all').shape[0]
    #同时填写定向和统招志愿的用户数
    both_zy = ((df['highschool'].notna()) & (df[['volunteer_1', 'volunteer_2', 'volunteer_3', 'volunteer_4','volunteer_5']].notna().sum(axis=1) > 0)).sum()
    #填写志愿的用户
    sum_zy = direct_users + volunteer_users - both_zy
    
    return np.array([scan_user,subscribers,blacklist,direct_users,volunteer_users,both_zy,sum_zy])

def line_counter(df,freq='D',is_show=False):
    df['date_joined'] = pd.to_datetime(df['date_joined'])
    series = df.set_index('date_joined').resample(freq).apply(count_users).cumsum()
    
    x_label = list(series.index)  
    x_label = list(map(lambda x: x.strftime('%m-%d-%H'),x_label))
    scan_user = list(series.apply(lambda x:x[0]))
    subscribers = list(series.apply(lambda x:x[1]))
    blacklist = list(series.apply(lambda x:x[2]))
    direct_users = list(series.apply(lambda x:x[3]))
    volunteer_users = list(series.apply(lambda x:x[4]))
    both_zy = list(series.apply(lambda x:x[5]))
    sum_zy = list(series.apply(lambda x:x[6]))
    
    
    c = (
        Line(init_opts=opts.InitOpts(width='1750px'))
        .add_xaxis(x_label)
        .add_yaxis("浏览用户", scan_user,is_smooth=True,label_opts=opts.LabelOpts(is_show=is_show))
        .add_yaxis("注册用户", subscribers,is_smooth=True,label_opts=opts.LabelOpts(is_show=is_show))
        .add_yaxis("黑名单", blacklist,is_smooth=True,label_opts=opts.LabelOpts(is_show=is_show))
        .add_yaxis("定向用户", direct_users,is_smooth=True,label_opts=opts.LabelOpts(is_show=is_show))
        .add_yaxis("统招用户", volunteer_users,is_smooth=True,label_opts=opts.LabelOpts(is_show=is_show))
        .add_yaxis("定向&统招用户", both_zy,is_smooth=True,label_opts=opts.LabelOpts(is_show=is_show))
        .add_yaxis("填写志愿用户", sum_zy,is_smooth=True,label_opts=opts.LabelOpts(is_show=is_show))
        .set_global_opts(title_opts=opts.TitleOpts(title="各类别用户数量走势"),
                         legend_opts=opts.LegendOpts(pos_left="25%"),
                        yaxis_opts=opts.AxisOpts(name="数量",name_gap=50,name_location='middle'),
                         xaxis_opts=opts.AxisOpts(name="时间(月-日-时)",name_gap=30,name_location='middle'))
    )
    
    return c

def pie_radius(value_count,title,legend=True,width='650px',height='300px'):
    if value_count is not None:
        labels = list(value_count.index)
        counts = list(value_count) 
        subtitle = None 
        if width=='900px' :
            subtitle = '只显示注册数量前十的学校'

        c = (
            Pie(init_opts=opts.InitOpts(width=width,height=height))
            .add(
                "",
                [list(z) for z in zip(labels, counts)],
                radius=["45%", "75%"]
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title,subtitle=subtitle),
                legend_opts=opts.LegendOpts(is_show=legend,
                    type_="scroll",orient="vertical", pos_top="15%", pos_left="2%"
                ),
            )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        )
        
    else:
         c = (
            Pie(init_opts=opts.InitOpts(width=width,height=height))
            .add(
                "",
                []
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title,subtitle='无数据')
            )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        )
    return c

def middle_school_data4box(df):
    #筛选并reshape数据
    
    # df = df[df['区']==district]
    notna_idx = df['school'].dropna().index
    middle_score = df.loc[notna_idx,['school','score']].pivot(columns='school',values='score')
    #排序
    sorted_cols = list(middle_score.describe().loc['50%'].sort_values(ascending=False).index)
    middle_score = middle_score[sorted_cols]
    return middle_score

def district_score_box_plot(df,district,school_name):
    try:        
        # school_name=None
        middle_score = middle_school_data4box(df)
        labels = list(middle_score.columns)
        c = Boxplot(init_opts=opts.InitOpts(width='1750px'))
        c.add_xaxis([""])
        for col in labels:
            value = [list(middle_score[col].dropna())]
            c.add_yaxis(col,c.prepare_data(value))
        c.set_global_opts(title_opts=opts.TitleOpts(title=f"{district}-{school_name}成绩分布"),
                         legend_opts=opts.LegendOpts(is_show=False),
                         yaxis_opts=opts.AxisOpts(min_=400,max_=750))
        return c
    except:
        v2 = [Faker.values(450,650)]
        v1 = [Faker.values(500,700)]
        c = Boxplot(init_opts=opts.InitOpts(width='1750px'))
        c.add_xaxis([''])
        c.add_yaxis("中学A", c.prepare_data(v1)).add_yaxis("中学B", c.prepare_data(v2))
        c.set_global_opts(title_opts=opts.TitleOpts(title=f"{district}初中成绩分布（示例）", 
                                                    subtitle="当看到此页面，说明所选区目前无数据"))
        return c

def pre_sankey_data(df):
    
    # df = df[df['区']==district]
    
    #分箱
    tps = []
    for i in range(len(list(range(500,701,10)))-1):
        tps.append((list(range(500,701,10))[i],list(range(500,701,10))[i+1]))
    bins = pd.IntervalIndex.from_tuples(tps)
    df['score_cut'] = pd.cut(df['score'],bins)
    #筛选数据&清理&排序
    sankey_data = df[['juniormiddleschool','score_cut','highschool']]
    notna_idx = sankey_data['highschool'].dropna().index
    sankey_data = sankey_data.loc[notna_idx]
    sankey_data['highschool'] = sankey_data['highschool'].apply(lambda x: x+'(高)')
    sankey_data = sankey_data.dropna()
    return sankey_data

def sankey_base(sankey_data,district,school_name):
    nodes=[]
    links = []
    # school_name = None
    for col in sankey_data.columns:
        for i in sankey_data[col].unique():
            nodes.append({'name':str(i),'value':int(sankey_data[sankey_data[col] == i].count().iloc[0])})
    school2score_data = pd.DataFrame(sankey_data.groupby(['juniormiddleschool','score_cut'])['highschool'].count()).reset_index()
    school2score_data = school2score_data.sort_values(by='score_cut',ascending=False)
    score_data2highschool = pd.DataFrame(sankey_data.groupby(['score_cut','highschool'])['juniormiddleschool'].count()).reset_index()
    score_data2highschool = score_data2highschool.sort_values(by='score_cut',ascending=False)
    for idx in school2score_data.index:
        links.append({"source": school2score_data.loc[idx,'juniormiddleschool'], 
                      "target": str(school2score_data.loc[idx,'score_cut']), 
                      "value": int(school2score_data.loc[idx,'highschool'])})
    for idx in score_data2highschool.index:
        links.append({"source": str(score_data2highschool.loc[idx,'score_cut']), 
                      "target": score_data2highschool.loc[idx,'highschool'], 
                      "value": int(score_data2highschool.loc[idx,'juniormiddleschool'])})
    c = (
        Sankey(init_opts=opts.InitOpts(height='900px',width='1750px'))
        .add(
            "",
            nodes,
            links,
            linestyle_opt=opts.LineStyleOpts(opacity=0.2, curve=0.5, color="source"),
            label_opts=opts.LabelOpts(position="right"),
        )
        .set_global_opts(title_opts=opts.TitleOpts(title=f"{district}-{school_name}定向志愿同分数段去向"))
    )

    return c




def pre_graph_data(df):
    #筛选数据&去除全为空值的行
    volunteer_cols = ['volunteer_1','volunteer_2','volunteer_3','volunteer_4','volunteer_5']
    graph_data = df[['school']+volunteer_cols]
    notna_idx = graph_data[volunteer_cols].dropna(how='all').index
    graph_data = graph_data.loc[notna_idx]
    
    #高中名称添加(高)
    def add_high_school(x):
        try:
            return (x+'(高)')
        except:
            return x
    graph_data[volunteer_cols] = graph_data[volunteer_cols].applymap(add_high_school)
    
    nodes=[]
    #初中学校
    for school_name in graph_data['school'].unique():
        count = (graph_data['school'] == school_name).sum()
        nodes.append(opts.GraphNode(name=school_name, symbol_size=int(count),value=int(count), category='初中'))

    #第一批次学校
    first_batch = (graph_data['volunteer_1'].append(graph_data['volunteer_2'])).dropna()
    for school_name in first_batch.unique():
        count = (first_batch == school_name).sum()
        nodes.append(opts.GraphNode(name=school_name, symbol_size=int(count),value=int(count), category='第一批次'))

    #第二批次学校
    second_batch = (graph_data['volunteer_3'].append(graph_data['volunteer_4']).append(graph_data['volunteer_5'])).dropna()
    for school_name in second_batch.unique():
        count = (second_batch == school_name).sum()
        nodes.append(opts.GraphNode(name=school_name, symbol_size=int(count), value=int(count),category='第二批次')) 
    
    def data2links(pivot_data,color):
        '''
        将分志愿计数的dataframe处理成links
        '''
        links=[]
        for idx in pivot_data.index:
            for col in pivot_data.columns:
                if not np.isnan(pivot_data.loc[idx,col]):
                    links.append(opts.GraphLink(source=idx,
                                                target=col,
                                                value=int(pivot_data.loc[idx,col]),
                                                linestyle_opts=opts.LineStyleOpts(width=int(pivot_data.loc[idx,col]),
                                                                                  color=color,
                                                                                  curve=0.2)))
        return links   
    #各志愿对应的线条颜色
    colors = ['#FF8947','#41E89D','#FF8947','#41E89D','#557EFF']
    links=[]
    for volunteer,color in list(zip(volunteer_cols,colors)):
        pivot_data = graph_data.pivot_table(index='school',columns=volunteer,aggfunc='size')
        link = data2links(pivot_data,color)
        links += link
    #Categories
    categories = [
            opts.GraphCategory(name='初中'),
            opts.GraphCategory(name='第一批次'),
            opts.GraphCategory(name='第二批次')
        ]
    return nodes,links,categories

def graph_with_opts(nodes, links,categories,district,school_name):
    c = (
        Graph(init_opts=opts.InitOpts(width='1750px'))
        .add("", nodes, links,categories)
        .set_global_opts(title_opts=opts.TitleOpts(title=f"{district}-{school_name}\n统招志愿关系图谱"))
    )
    return c

#根据两点经纬度计算直线距离
def cacu_distance(*tp):
    lng_a,lat_a,lng_b,lat_b = np.radians(tp)
    r = 6378137.0
    #A，B 向量
    v_a = r * np.array([np.cos(lat_a) * np.cos(lng_a),np.cos(lat_a) * np.sin(lng_a), np.sin(lat_a)])
    v_b = r * np.array([np.cos(lat_b) * np.cos(lng_b),np.cos(lat_b) * np.sin(lng_b), np.sin(lat_b)])
    #计算向量夹角(弧度制)
    temp = (v_a*v_b).sum() / (np.linalg.norm(v_a)*np.linalg.norm(v_b))
    if temp > 1:
        temp = 1
    elif temp < -1:
        temp = -1
    else:
        temp = temp
    theta = np.arccos(temp)
#     print(theta)
    #计算两点弧长
    distance = theta * r
    
    return int(distance/1000)

def get_distance(school_a,school_b):
    df = pd.read_excel('./Doc/school_location.xlsx')    
    location_a = eval(df[df['school']==school_a]['location'].iloc[0])
    location_b = eval(df[df['school']==school_b]['location'].iloc[0])
    distance = cacu_distance(location_a[0],location_a[1],location_b[0],location_b[1])
    return distance

def pre_distance_data(df,tpe='DX'):
    '''对所在初中及填报高中与初中之间的距离进行统计计数，返回value_counts'''
    bins = pd.IntervalIndex.from_tuples([(-1,3),(3,5),(5,8),(8,100000)],dtype='interval[int64]')
    
    if tpe == 'DX':
        #定向
        df = df[['juniormiddleschool','highschool']]
        notna_idx = df['highschool'].dropna().index
        df = df.loc[notna_idx]
        
        df['distance'] = (df['juniormiddleschool']+'-'+df['highschool']).apply(lambda x: get_distance(x.split('-')[0],x.split('-')[1]))
        df['distance_cut'] = pd.cut(df['distance'],bins)
        df['distance_cut'] = df['distance_cut'].astype(str).map({str(bins[0]):'3公里以内',
                                                                     str(bins[1]):'3到5公里',
                                                                     str(bins[2]):'5到8公里',
                                                                     str(bins[3]):'8公里以外'})
        distance_data = pd.DataFrame(df.groupby(['juniormiddleschool','distance_cut'])['distance'].count()).reset_index().rename(columns={'distance':'count'})
        dingxiang_series = distance_data.groupby('distance_cut')['count'].sum()
        
        for cut in ['3公里以内', '3到5公里', '5到8公里', '8公里以外']:
            try:
                dingxiang_series[cut]
            except KeyError:
                dingxiang_series[cut] = 0
        dingxiang_series = dingxiang_series.sort_index()        
        return dingxiang_series
    
    else:
        #统招
        volunteer_cols = ['volunteer_1','volunteer_2','volunteer_3','volunteer_4','volunteer_5']
        tz_df = df[['school']+volunteer_cols]
        notna_idx = tz_df[volunteer_cols].dropna(how='all').index
        tz_df = tz_df.loc[notna_idx]
        
        tz_dfs = []
        rename_cols = ['一批一志愿','一批二志愿','二批一志愿','二批二志愿','二批三志愿']
        for col in volunteer_cols:
            idx = volunteer_cols.index(col)
            
            notna_idx_col = tz_df[col].dropna(how='all').index
            tz_df_col = tz_df.loc[notna_idx_col]
            

            tz_df_col['distance'] = (tz_df_col['school']+'-'+tz_df_col[col]).apply(lambda x: get_distance(x.split('-')[0],x.split('-')[1])) 
            tz_df_col['distance_cut'] = pd.cut(tz_df_col['distance'],bins)
            tz_df_col['distance_cut'] = tz_df_col['distance_cut'].astype(str).map({str(bins[0]):'3公里以内',
                                                                     str(bins[1]):'3到5公里',
                                                                     str(bins[2]):'5到8公里',
                                                                     str(bins[3]):'8公里以外'})
            distance_data = pd.DataFrame(tz_df_col.groupby(['school','distance_cut'])['distance'].count()).rename(columns={'distance':rename_cols[idx]})
            tz_dfs.append(distance_data)
        
        distance_data = pd.concat(tz_dfs,axis=1).reset_index().replace(np.NaN,0)
        distance_data[rename_cols] = distance_data[rename_cols].astype(int)
        
        tongzhao_serieses = []
        for col in rename_cols:
            ff_series = distance_data.groupby('distance_cut')[col].sum()
            for cut in ['3公里以内', '3到5公里', '5到8公里', '8公里以外']:
                try:
                    ff_series[cut]
                except KeyError:
                    ff_series[cut] = 0
            ff_series = ff_series.sort_index()
            tongzhao_serieses.append(ff_series)
        return tongzhao_serieses

#dataframe转成字典组成的列表，方便转成html表单
def df2list(df):
    #只显示填写表单的用户
    df = df.query('is_filled==1').rename(columns={'区':'district'})
    #更改时间显示
    df['date_joined'] = df['date_joined'].dt.strftime('%m-%d-%H')
    cols = ['date_joined','district','school','category','score','highschool','volunteer_1', 'volunteer_2', 'volunteer_3', 'volunteer_4','volunteer_5']
    form = []
    for i in df.index:
        temp_dict={}
        for col in cols:
            temp_dict[col] = df.loc[i,col]
        form.append(temp_dict)  
    return form

def value2cumsum(df,columns):
    '''
    把数据进行累加计数
    '''
    df_value_counts = pd.DataFrame(df.groupby('time')['obj'].value_counts()).rename(columns={'obj':'count'}).reset_index()
    #模拟数据
    multi_index = pd.MultiIndex.from_product([columns,df.obj.unique()],names=['time','obj'])
    df_create = pd.DataFrame(data=0, index=multi_index, columns=['count']).reset_index()
    #添加非重复的数据
    for idx in df_create.index:
        t = df_create.loc[idx,'time']
        o = df_create.loc[idx,'obj']
        if df_value_counts[(df_value_counts['time']==t) & (df_value_counts['obj']==o) ].shape[0] == 0:
            df_value_counts = df_value_counts.append(df_create.loc[idx])
    #重新排序        
    df_value_counts = df_value_counts.sort_values(by=['time','obj']).reset_index(drop=True)
    #做cumulative sum
    cum_sum_df_list = []
    for unique_obj in df_value_counts.obj.unique():
        df_uniuqe_obj = df_value_counts[df_value_counts['obj']==unique_obj].reset_index(drop=True)
        df_uniuqe_obj['count'] = df_uniuqe_obj['count'].cumsum()
        cum_sum_df_list.append(df_uniuqe_obj)
    #合并
    df_final = pd.DataFrame()
    for df_temp in cum_sum_df_list:
        df_final = df_final.append(df_temp)
    #排序
    df_final = df_final.sort_values(by=['time','obj']).reset_index(drop=True)
    return df_final

def pre_linkage_pies(df_input,title,columns,width='350px'):
    '''
    读入df，绘制该df所有时段的pie，返回pie的列表
    '''
    pies = []
    df = value2cumsum(df_input,columns=columns)
    
    for col in columns:
        
        values = df[df['time'] == col].set_index('obj')['count'].sort_values(ascending=False)[:5]
        
        chart = pie_radius(values,title,width=width,height='250px')
        chart = Markup(chart.render_embed())
        pies.append(chart)
    return pies

def pre_linkage_data():
    #数据清理
    df_nginx = pd.read_csv("./Doc/nginx_access.csv",header=None)
    df_nginx[0] = pd.to_datetime(df_nginx[0]).astype(str) + '-' + df_nginx[1].astype(str)
    df_nginx[0] = pd.to_datetime(df_nginx[0],format='%Y-%m-%d-%H')
    df_nginx[0] = df_nginx[0].dt.strftime('%m-%d-%H')
    # df_nginx = df_nginx[(df_nginx[0] > '07-30-00') & (df_nginx[0] < '08-05-00')]
    
    #准备折线图数据    
    data_for_line = pd.DataFrame(df_nginx.groupby(0)[2].value_counts().sort_index()).rename(columns={2:'count'}).unstack(0)
    data_for_line.columns = [x[1] for x in data_for_line.columns]
    data_for_line = data_for_line.fillna(0).astype(int)    
    data_for_line = data_for_line.loc[['学校详情','比较学校','进入定向志愿']].rename(index={'学校详情':'查看学校详情','比较学校':'对比统招学校','进入定向志愿':'查看定向学校'})
    
    list_for_line = [['time']+list(data_for_line.columns)]
    for i in data_for_line.index:
        loc_data = [i] + list(data_for_line.loc[i])
        list_for_line.append(loc_data)
        
    #静态数据
    number_list = []
    for unique_2 in df_nginx[2].unique():
        number_list.append(df_nginx[df_nginx[2]==unique_2].shape[0])

    #饼图数据
    def cut_long_name(x):
        if len(x)<=5:
            return (x)
        else:
            return (x[:5]+'\n'+cut_long_name(x[5:]))
    #学校详情
    df_school_detail = df_nginx[df_nginx[2]=='学校详情'][[0,3]].rename(columns={0:'time',3:'obj'})
    df_school_detail = df_school_detail.loc[df_school_detail['obj'].replace('undefined',np.NaN).dropna().index]
    df_school_detail['obj'] = df_school_detail['obj'].apply(cut_long_name)
    school_detail_pies = pre_linkage_pies(df_school_detail,'学校查看详情',data_for_line.columns,width='400px')

    #统招志愿
    #先区分一批和二批学校
    school_batch = pd.read_excel('./Doc/school_batch.xlsx')
    df_temp = df_nginx.join((df_nginx[df_nginx[2]=='比较学校'][3].str.split(',',expand=True)).rename(columns=lambda x: 'school_'+str(x)))
    df_compare_school = pd.DataFrame()
    for col in df_temp.columns[4:]:
        temp = df_temp[[0,2,3,col]].rename(columns={col:'school_0'})
        df_compare_school = df_compare_school.append(temp)
    df_compare_school = df_compare_school.sort_values(by=0).reset_index(drop=True)
    df_compare_school = df_compare_school.loc[df_compare_school['school_0'].replace('None',np.NaN).dropna().index][[0,'school_0']]
    df_compare_school['batch'] = df_compare_school['school_0'].apply(lambda x: school_batch[school_batch['schoolname']==x]['school_batch'].iloc[0])

    df_compare_school_first = df_compare_school.query('batch=="一批"').rename(columns={0:'time','school_0':'obj'})[['time','obj']]    
    df_compare_school_second = df_compare_school.query('batch=="二批"').rename(columns={0:'time','school_0':'obj'})[['time','obj']]
    df_compare_school_first['obj'] = df_compare_school_first['obj'].apply(cut_long_name)
    df_compare_school_second['obj'] = df_compare_school_second['obj'].apply(cut_long_name)

    compare_school_first_pies = pre_linkage_pies(df_compare_school_first,'一批学校比较详情',data_for_line.columns,width='400px')
    compare_school_second_pies = pre_linkage_pies(df_compare_school_second,'二批学校比较详情',data_for_line.columns,width='400px')
    
    #定向志愿
    df_dingxiang = df_nginx[df_nginx[2]=='进入定向志愿'][[0,3]].rename(columns={0:'time',3:'obj'})
    df_dingxiang['obj'] = df_dingxiang['obj'].apply(cut_long_name)
    dingxiang_pies = pre_linkage_pies(df_dingxiang,'定向志愿查看详情',data_for_line.columns,width='400px')
    
    return list_for_line,school_detail_pies,compare_school_first_pies,compare_school_second_pies,dingxiang_pies
