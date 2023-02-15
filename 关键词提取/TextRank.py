# textrank算法
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from operator import itemgetter
from collections import defaultdict

import string
import xlrd
import xlwt
from xlutils.copy import copy

import jsonlines
from nltk import word_tokenize, pos_tag, WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from gensim.models.word2vec import Word2Vec
from gensim.models import word2vec,KeyedVectors

# 拿到训练好的词向量模型
model = KeyedVectors.load_word2vec_format("../pubmedDataset/gensim_model.vector")


# 计算两个词语之间的余弦相似度
def computeSimilarity(word1, word2):
    return model.similarity(word1, word2)


# 在提取关键词前需要进行文本预处理
def textPreHandle(text: string):
    cutwords1 = word_tokenize(text.lower())  # 分词

    interpunctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']  # 定义符号列表
    cutwords2 = [word for word in cutwords1 if word not in interpunctuations]  # 去除标点符号

    stops = set(stopwords.words("english"))
    cutwords3 = [word for word in cutwords2 if word not in stops]

    cutwords4 = []
    # 根据词性提取单词：形容词，名称，动词，动名词
    for item in pos_tag(cutwords3):
        if item[1] in ['NN', 'NNS', 'NNP', 'NNPS', 'FW', 'VB', 'VBG', 'VBD', 'VBN', 'JJ']:
            cutwords4.append(item[0])

    for item in cutwords4:
        item = PorterStemmer().stem(item)

    for item in cutwords4:
        item = WordNetLemmatizer().lemmatize(item, pos='v')  # 指定还原词性为名词

    res = cutwords4

    return res


class UndirectWeightedGraph:
    d = 0.85

    def __init__(self):
        self.graph = defaultdict(list)

    # 给词图添加一条边
    def addEdge(self, start, end, weight):
        # use a tuple (start, end, weight) instead of a Edge object
        self.graph[start].append((start, end, weight))
        self.graph[end].append((end, start, weight))

    # 图的textrank算法
    def rank(self):
        ws = defaultdict(float)
        outSum = defaultdict(float)

        # wsdef代表着词的权重值，每个词的初始权重值都是1
        wsdef = 1.0 / (len(self.graph) or 1.0)
        for n, out in self.graph.items():
            ws[n] = wsdef
            outSum[n] = sum((e[2] for e in out), 0.0)

        # this line for build stable iteration
        sorted_keys = sorted(self.graph.keys())
        for x in range(10000):  # 10 iters
            for n in sorted_keys:
                s = 0
                for e in self.graph[n]:
                    s += e[2] / outSum[e[1]] * ws[e[1]]
                ws[n] = (1 - self.d) + self.d * s

        (min_rank, max_rank) = (sys.float_info[0], sys.float_info[3])

        for w, num in ws.items():
            if num < min_rank:
                min_rank = num
            if num > max_rank:
                max_rank = num

        for n, w in ws.items():
            # to unify the weights, don't *100.
            ws[n] = (w - min_rank / 10.0) / (max_rank - min_rank / 10.0)

        return ws


class TextRank:

    def __init__(self):
        self.span = 5

    def textrank(self, sentence, topK=5, withWeight=False, withFlag=True):
        """
        Extract keywords from sentence using TextRank algorithm.
        Parameter:
            - topK: return how many top keywords. `None` for all possible words.
            - withWeight: if True, return a list of (word, weight);
                          if False, return a list of words.
            - allowPOS: the allowed POS list eg. ['ns', 'n', 'vn', 'v'].
                        if the POS of w is not in this list, it will be filtered.
            - withFlag: if True, return a list of pair(word, weight) like posseg.cut
                        if False, return a list of words
        """
        # 初始化一个图类
        g = UndirectWeightedGraph()
        cm = defaultdict(int)
        words = textPreHandle(sentence)
        for i, wp in enumerate(words):
            for j in range(i + 1, i + self.span):
                if j >= len(words):
                    break
                if withFlag:
                    d = 0.8
                    try:
                        d = computeSimilarity(wp, words[j])
                    except:
                        d = 0.8
                    finally:
                        cm[(wp, words[j])] += d
                else:
                    d = 0.8
                    try:
                        d = computeSimilarity(wp, words[j])
                    except:
                        d = 0.8
                    finally:
                        cm[(wp.word, words[j].word)] += d

        for terms, w in cm.items():
            g.addEdge(terms[0], terms[1], w)
        nodes_rank = g.rank()
        if withWeight:
            tags = sorted(nodes_rank.items(), key=itemgetter(1), reverse=True)
        else:
            tags = sorted(nodes_rank, key=nodes_rank.__getitem__, reverse=True)

        if topK:
            return tags[:topK]
        else:
            return tags


textrank = TextRank()

keywords = []

with jsonlines.open("../docs/BL18U1/paper.jsonlines") as f:
    for line in f:
        key = []
        sentence = line.get("title") + " " + line.get("abstract")
        if (line.get("keywords") is None):
            key = []
        else:
            key = line.get("keywords").replace("Keywords:", "").split(";")
        res = (key + textrank.textrank(sentence))[:10]
        keywords.append({
            "key": res,
            "index": line.get("index")
        })

print(keywords)

data = xlrd.open_workbook('../docs/BL18U1/PDB.xls', formatting_info=True)
excel = copy(wb=data)  # 完成xlrd对象向xlwt对象转换

excel_table = excel.get_sheet(0)  # 获得要操作的页
table = data.sheets()[0]

for keyword in keywords:
    str = ""
    for s in keyword.get("key"):
        str += s + " "
    excel_table.write(keyword.get("index"), 9, str)

excel.save('PDB.xls')
