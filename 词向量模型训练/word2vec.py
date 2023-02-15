from gensim.models.word2vec import Word2Vec
from gensim.models import word2vec,KeyedVectors
import time
sentence = word2vec.Text8Corpus("./pubmedDataset/TextDataSet.txt")

def word2vec(sss):
    start = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print("开始进行训练，当前时间为: ", start)
    # 生成词向量为200维，考虑上下5个单词共10个单词，采用sg=1的方法也就是skip-gram
    model = Word2Vec(vector_size=200, workers=3, sg=1)

    model.build_vocab(sss)
    model.train(sss, total_examples = model.corpus_count, epochs=100)
    model.wv.save_word2vec_format('./pubmedDataset/gensim_model.vector')  # 保存模型
    model.save('./pubmedDataset/gensim_model') # 以两种不同的方式保存模型
    end = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print("训练完成，当前时间为: ", end)

# 测试训练好的word2vec模型
def testMode(path):
    new_model = KeyedVectors.load_word2vec_format(path)  # 调用模型
    return new_model
# testMode("./pubmedDataset/gensim_model.vector")