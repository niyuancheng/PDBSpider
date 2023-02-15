# 使用nltk进行文本预处理
import string

import jsonlines
from nltk import word_tokenize, pos_tag, WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


# 对语料库进行文本预处理，也就是进行分词，删去无用词等操作
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


# 从语料库JSONL格式的文件中提取相关信息（论文的摘要部分）到代码中，方便后续的文本预处理
def handleJSONl():
    text = ""
    with open("./pubmedDataset/miniPubMed.jsonl", "r+", encoding="utf8") as f:
        count = 1
        for item in jsonlines.Reader(f):
            print(count)
            if count > 360000:
                return text
            text += item["text"] + " "
            count += 1
    return text


text = handleJSONl()
cutwords = textPreHandle(text)

print(cutwords)
with open("./pubmedDataset/TextDataSet.txt", mode="w", encoding="utf8") as f:
    for i in cutwords:
        f.write(i + " ")
