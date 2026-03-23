# repo_facts: funNLP

## 语言分布
   1 py

## 目录结构（前两层）
/Users/tang/Documents/vibecoding/Doramagic/experiments/exp-why-extraction/funNLP
.github
.git
data
data/paper
data/职业词库
data/繁简体转换词库
data/公司名字词库
data/拆字词库
data/同义词库、反义词库、否定词库
data/中文分词词库整理
data/动物词库
data/汽车品牌、零件词库
data/停用词
data/古诗词库
data/财经词库
data/中文缩写库
data/成语词库
data/中英日文名字库
data/法律词库
data/医学词库
data/NLP_BOOK
data/.logo图片
data/诗词短句词库
data/IT词库
data/食物词库
data/中文谣言数据
data/历史名人词库
data/地名词库

## README（前100行）
<center>
    <img style="border-radius: 0.3125em;
    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);" 
    src="./data/.logo图片/.img.jpg"width="180">
    <br>
    <div style="color:orange; border-bottom: 1px solid #d9d9d9;
    display: inline-block;
    color: #999;
    padding: 2px;">NLP民工的乐园</div>
</center>
<br>

[![](https://img.shields.io/github/stars/fighting41love/funnlp?style=social)](https://github.com/fighting41love/funnlp)
[![](https://img.shields.io/badge/dynamic/json?color=blue&label=%E7%9F%A5%E4%B9%8E%E5%85%B3%E6%B3%A8&query=%24.data.totalSubs&url=https%3A%2F%2Fapi.spencerwoo.com%2Fsubstats%2F%3Fsource%3Dzhihu%26queryKey%3Dmountain-blue-64)](https://www.zhihu.com/people/mountain-blue-64)
[![](data/.logo图片/.捐赠图片/.Citations-487-red.svg)](https://scholar.google.com/citations?hl=en&user=aqZdfDUAAAAJ)

[![](data/.logo图片/.捐赠图片/.Home-%E4%BA%BA%E7%94%9F%E6%B5%AA%E8%B4%B9%E6%8C%87%E5%8D%97-brightgreen.svg)](http://fighting41love.github.io/archives/)
[![](data/.logo图片/.捐赠图片/.%E7%8C%8E%E9%80%81%E9%97%A8-CV-orange.svg)](http://fighting41love.github.io/)
<!-- [![](https://img.shields.io/badge/dynamic/json?color=blueviolet&label=github%20followers&query=%24.data.totalSubs&url=https%3A%2F%2Fapi.spencerwoo.com%2Fsubstats%2F%3Fsource%3Dgithub%26queryKey%3Dfighting41love)](https://github.com/fighting41love) -->
<!-- [![](https://img.shields.io/badge/Homepage-%E4%BA%BA%E7%94%9F%E6%B5%AA%E8%B4%B9%E6%8C%87%E5%8D%97-brightgreen)](http://fighting41love.github.io/archives/) -->

### The Most Powerful NLP-Weapon Arsenal
## NLP民工的乐园: 几乎最全的中文NLP资源库
在入门到熟悉NLP的过程中，用到了很多github上的包，遂整理了一下，分享在这里。

很多包非常有趣，值得收藏，满足大家的收集癖！
如果觉得有用，请分享并star:star:，谢谢！

长期不定时更新，欢迎watch和fork！:heart::heart::heart:

|  :fire::fire::fire::fire::fire::fire::fire::fire::fire::fire:   &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; |
|  ----  |
| * [类ChatGPT的模型评测对比](#类ChatGPT的模型评测对比)  <br> * [类ChatGPT的资料](#类ChatGPT的资料)  <br>* [类ChatGPT的开源框架](#类ChatGPT的开源框架)  <br>* [LLM的训练_推理_低资源_高效训练](#LLM的训练_推理_低资源_高效训练)   <br>* [提示工程](#提示工程)  <br>* [类ChatGPT的文档问答](#类ChatGPT的文档问答)  <br>* [类ChatGPT的行业应用](#类ChatGPT的行业应用)  <br>* [类ChatGPT的课程资料](#类ChatGPT的课程资料)  <br>* [LLM的安全问题](#LLM的安全问题)  <br>* [多模态LLM](#多模态LLM)  <br>* [LLM的数据集](#LLM的数据集)

 
|  :eggplant: :cherries: :pear: :tangerine:   &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;  |  :sunflower: :strawberry:  :melon: :tomato: :pineapple: &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;|
|  ----  | ----  |
| * [语料库](#语料库)  <br> * [词库及词法工具](#词库及词法工具)  <br> * [预训练语言模型](#预训练语言模型)  <br>  * [抽取](#抽取)  <br> * [知识图谱](#知识图谱)  <br>   * [文本生成](#文本生成) <br>   * [文本摘要](#文本摘要)  <br>  * [智能问答](#智能问答) <br>  * [文本纠错](#文本纠错)  | * [文档处理](#文档处理) <br>   * [表格处理](#表格处理) <br>   * [文本匹配](#文本匹配)  <br>   * [文本数据增强](#文本数据增强) <br>   * [文本检索](#文本检索) <br>  * [阅读理解](#阅读理解) <br>  * [情感分析](#情感分析) <br>  * [常用正则表达式](#常用正则表达式) <br>   * [语音处理](#语音处理) |
| * [常用正则表达式](#常用正则表达式) <br>  * [事件抽取](#事件抽取) <br> * [机器翻译](#机器翻译) <br> * [数字转换](#数字转换) <br>  * [指代消解](#指代消解) <br>  * [文本聚类](#文本聚类) <br>  * [文本分类](#文本分类) <br> * [知识推理](#知识推理) <br> * [可解释NLP](#可解释自然语言处理) <br> * [文本对抗攻击](#文本对抗攻击)  |  * [文本可视化](#文本可视化)  <br>  * [文本标注工具](#文本标注工具) <br>  * [综合工具](#综合工具) <br> * [有趣搞笑工具](#有趣搞笑工具) <br> * [课程报告面试等](#课程报告面试等) <br> * [比赛](#比赛) <br> * [金融NLP](#金融自然语言处理) <br> * [医疗NLP](#医疗自然语言处理) <br> * [法律NLP](#法律自然语言处理) <br> * [文本生成图像](#文本生成图像) <br> * [其他](#其他)  |

<!-- 
目录（Table of contents）
=================
<table border="0">
 <tr>
    <td><b style="font-size:30px">:star:</b></td>
    <td><b style="font-size:30px">:star::star:</b></td>
    <td><b style="font-size:30px">:star::star::star:</b></td>
    <td><b style="font-size:30px">:star::star::star::star:</b></td>
 </tr>
 <tr>
    <td>

<!--ts-->
   <!-- * [语料库](#语料库)
   * [词库及词法工具](#词库及词法工具)
   * [预训练语言模型](#预训练语言模型)
   * [抽取](#抽取)
   * [知识图谱](#知识图谱)
   * [文本生成](#文本生成)
   * [文本摘要](#文本摘要)
   * [智能问答](#智能问答)
   * [文本纠错](#文本纠错) -->


<!--te-->

  </td>

  <td>

<!--ts-->

   <!-- * [文档处理](#文档处理)
   * [表格处理](#表格处理)
   * [文本匹配](#文本匹配)
   * [文本数据增强](#文本数据增强)
   * [文本检索](#文本检索)
   * [阅读理解](#阅读理解)
   * [情感分析](#情感分析)
   * [常用正则表达式](#常用正则表达式)
   * [语音处理](#语音处理) -->
<!--te-->

  </td>

  <td>
   
<!--ts-->
   <!-- * [常用正则表达式](#常用正则表达式)
   * [事件抽取](#事件抽取)
   * [机器翻译](#机器翻译)
   * [数字转换](#数字转换)
   * [指代消解](#指代消解)
   * [文本聚类](#文本聚类)
   * [文本分类](#文本分类)
   * [知识推理](#知识推理)
   * [可解释NLP](#可解释自然语言处理)
   * [文本对抗攻击](#文本对抗攻击) -->


## 依赖
## 配置文件
.github/FUNDING.yml

## 核心代码文件（按大小排序 Top 10）
      14 data/中文分词词库整理/thirtyw.py

## 关键代码片段
### data/中文分词词库整理/thirtyw.py
```python
# -*- coding: UTF-8 -*- 
f = open('30wChinsesSeqDic.txt')
fout = open('30wdict.txt','a')
count = 0
for line in f:
	temp = line.strip()
	temp_list = temp.split(' ')
	temp_sublist = temp_list[1].split('\t')
	if len(temp_sublist[1]) > 2:
		count = count + 1
		print temp_sublist[1]
		fout.write(temp_sublist[1] + '\n')
f.close()
fout.close()
#print count```

## 入口文件
