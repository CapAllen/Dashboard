import os
import re
import json
import random
import pymysql
import pandas as pd
import numpy as np
from random import randrange

from flask import Flask,render_template, request, jsonify, url_for
from sqlalchemy import create_engine

from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Pie, Boxplot, Timeline, Sankey, Graph

from jinja2 import Markup, Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig

from help_funcs import *

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./templates"))

app = Flask(__name__,static_url_path='')
# app = Flask(__name__)
app.jinja_env.variable_start_string = '{{ '
app.jinja_env.variable_end_string = ' }}'

df = get_data(test=True)

#基本展示信息
scan_user = df.shape[0]
subscribers = df.query('is_filled==1').shape[0]
blacklist = df.query('(counter>3)|(sport_counter>3)').shape[0]

#用户数量统计
count_user_D_graph = line_counter(df)
count_user_HD_graph = line_counter(df,freq='12h')
count_user_H_graph = line_counter(df,freq='h')

#各类占比
juni_middle_school_value_count = df['school'].value_counts()[:10]
category_value_count = df['category'].value_counts()

juni_rate_graph = pie_radius(juni_middle_school_value_count,'初中学校占比',width='900px')
category_rate_graph = pie_radius(category_value_count,'考生类别占比')

#linkage
linkage_data = pre_linkage_data()
number_list = linkage_data[-1]

# index webpage displays cool visuals and receives user input text for model
@app.route('/')
@app.route('/index',methods=['GET'])
def index():     
    district = request.args.get('a', '') 
    school_name = request.args.get('b', '') 
    #筛选数据
    df_filtered = filter_data(df,district,school_name)
    
    if len(df_filtered)==0:
        return render_template('dashboard-2.html',
                            scan_user=scan_user,
                            subscribers=subscribers,
                            blacklist=blacklist,
                            district=district,
                            school_name=school_name,
                            number_list=number_list,
                            count_user_D_graph=Markup(count_user_D_graph.render_embed()),
                            count_user_HD_graph=Markup(count_user_HD_graph.render_embed()),
                            count_user_H_graph=Markup(count_user_H_graph.render_embed()),
                            juni_rate_graph=Markup(juni_rate_graph.render_embed()),
                            category_rate_graph=Markup(category_rate_graph.render_embed()),
                            #linkage
                            data = linkage_data[0],
                            school_detail_pies=linkage_data[1],
                            compare_school_first_pies=linkage_data[2],
                            compare_school_second_pies=linkage_data[3],
                            dingxiang_pies=linkage_data[4])
    else:
        #分区显示各学校成绩箱线图
        Score_Graph = district_score_box_plot(df_filtered,district,school_name)
        #定向志愿流向桑基图
        sankey_data = pre_sankey_data(df_filtered)
        Sankey_Graph = sankey_base(sankey_data,district,school_name)
        #统招志愿关系图谱
        nodes,links,categories = pre_graph_data(df_filtered)
        Relation_Graph = graph_with_opts(nodes,links,categories,district,school_name)
        #志愿距离
        DX_distance_series = pre_distance_data(df_filtered,tpe='DX')
        TZ_distance_series = pre_distance_data(df_filtered,tpe='TZ')
        DX_Distance_Graph = pie_radius(DX_distance_series,title='定向志愿距离',legend=False,width='500px')

        FF_Distance_Graph = pie_radius(TZ_distance_series[0],title='一批一志愿距离',legend=False,width='500px')
        FS_Distance_Graph = pie_radius(TZ_distance_series[1],title='一批二志愿距离',legend=False,width='500px')
        SF_Distance_Graph = pie_radius(TZ_distance_series[2],title='二批一志愿距离',legend=False,width='500px')
        SS_Distance_Graph = pie_radius(TZ_distance_series[3],title='二批二志愿距离',legend=False,width='500px')
        ST_Distance_Graph = pie_radius(TZ_distance_series[4],title='二批三志愿距离',legend=False,width='500px')
        #所有数据的表单
        all_data = df2list(df_filtered)
        return render_template('dashboard-2.html',
                                scan_user=scan_user,
                                subscribers=subscribers,
                                blacklist=blacklist,
                                district=district,
                                school_name=school_name,
                                number_list=number_list,
                                count_user_D_graph=Markup(count_user_D_graph.render_embed()),
                                count_user_HD_graph=Markup(count_user_HD_graph.render_embed()),
                                count_user_H_graph=Markup(count_user_H_graph.render_embed()),
                                juni_rate_graph=Markup(juni_rate_graph.render_embed()),
                                category_rate_graph=Markup(category_rate_graph.render_embed()),
                                Score_Graph=Markup(Score_Graph.render_embed()),
                                Sankey_Graph=Markup(Sankey_Graph.render_embed()),
                                Relation_Graph=Markup(Relation_Graph.render_embed()),
                                DX_Distance_Graph=Markup(DX_Distance_Graph.render_embed()),
                                FF_Distance_Graph=Markup(FF_Distance_Graph.render_embed()),
                                FS_Distance_Graph=Markup(FS_Distance_Graph.render_embed()),
                                SF_Distance_Graph=Markup(SF_Distance_Graph.render_embed()),
                                SS_Distance_Graph=Markup(SS_Distance_Graph.render_embed()),
                                ST_Distance_Graph=Markup(ST_Distance_Graph.render_embed()),
                                #linkage
                                data = linkage_data[0],
                                school_detail_pies=linkage_data[1],
                                compare_school_first_pies=linkage_data[2],
                                compare_school_second_pies=linkage_data[3],
                                dingxiang_pies=linkage_data[4],
                                all_data=all_data   
        )

def main():
    app.run(host='0.0.0.0',port=5000,debug=True)


if __name__ == '__main__':
    main()