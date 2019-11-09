# Dashboard
## 目录

- [项目概览](#overview)
- [文件组成](#components)
- [快速开始](#run)
- [致谢&参考](#credits)

***

<a id='overview'></a>

## 1. 项目概览

当处理一些较为灵活的数据时，团队内不同角色的同事会有自己对数据的关注点，所以，这就要求数据分析师不能只出一个“死”报告了事儿，而需要的是一个可以让同事们去探索，去解决自己关注问题的”活“报告——[Dashboard](https://en.wikipedia.org/wiki/Dashboard_(business)) 。本项目利用[Flask](https://dormousehole.readthedocs.io/en/latest/)和[Pyecharts](https://pyecharts.org/#/)搭建局域网内Dashboard，其中Flask用来提供Web应用框架，Pyecharts用来解决交互式可视化的需求。

架构如下：

<img src="https://s2.ax1x.com/2019/08/15/mE1fkd.png" alt="mE1fkd.png" border="0" width='350'/>



最终实现效果如下：

![mEB0bR.gif](https://s2.ax1x.com/2019/08/15/mEB0bR.gif)



![mEBg2D.gif](https://s2.ax1x.com/2019/08/15/mEBg2D.gif)

<a id='components'></a>

## 2. 文件组成

```
├── run.py ------------------------# 项目主程序
├── help_funcs.py -----------------# 主程序会用到的一些函数，包括数据处理、可视化等
├── templates/
│   ├── dashboard-2.html-----------# DashBoard的HTML模板
│   ├── 其余文件 --------------------# pyecharts模板
├── static -------------------------# DashBoard所需的web头像、css样式及js
├── Doc ----------------------------# 项目主程序所需的一些额外数据
```

<a id='run'></a>

## 3. 快速开始

1. 依次执行如下代码

   ```
   git clone git@github.com:CapAllen/Dashboard.git
   cd Dashboard
   python run.py
   ```

2. 打开浏览器输入 http://127.0.0.1:5000/

<a id='credits'></a>

## 4. 致谢&参考

- [Pyecharts](https://pyecharts.org/#/)给了我丰富的交互式可视化选择，详细的文档上手就会，强烈推荐！
- 李辉的[HelloFlask站点](http://helloflask.com/)，轻松入门Flask。
- [Data visualization using D3.js and Flask](https://branetheory.org/2014/12/18/data-visualization-using-d3-js-and-flask/)
- [flask框架中jinja2传递参数和html，js文件接收参数](https://blog.csdn.net/m0_38061194/article/details/78891125)
- [Echarts Demo - 多图联动](https://www.echartsjs.com/examples/editor.html?c=dataset-link)

<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt=" Creative Commons" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" style="float:left" /></a>
