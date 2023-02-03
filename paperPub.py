import xlrd
import matplotlib.pyplot as plt
from xlutils.copy import copy


# 获取论文日期数据,存入二维数组
def dataInf(length):
    DataInf = []
    for i in range(1, length):
        if table1.cell(i, 4).value == '':
            continue
        a = int(table1.cell(i, 4).value)
        if a > 0:
            DataInf.append(a)
    print(len(DataInf))
    year = []
    yearNum = []
    for i in range(len(DataInf)):
        if DataInf[i] in year:
            continue
        else:
            year.append(DataInf[i])
    year.sort()
    for i in range(len(year)):
        yearNum.append(DataInf.count(year[i]))
    return year, yearNum


# 年份与论文发表数量柱状图
def imgPaperDate(year, num):
    plt.figure(figsize=(10, 5))
    plt.bar(year, num, width=0.5)
    # 柱状图上显示数据
    for y, n in zip(year, num):
        plt.text(y, n, '%.0f ' % n, ha='center', va='bottom')
    plt.title('Number of papers published per year')
    plt.xlabel('Years')
    plt.ylabel('Number')
    plt.show()


# 统计发表和未发表论文的结构数量
def TobePublished(length):
    numP = 0
    numNP = 0
    for i in range(1, length):
        if table1.cell(i, 1).value == '':
            continue
        if table1.cell(i, 1).value == 'To be published':
            numNP += 1
        else:
            numP += 1
    print(length-numNP, numP, numNP)


if __name__ == '__main__':
    # 获取excel信息
    data1 = xlrd.open_workbook('PDB_Excel.xls', formatting_info=True)
    excel1 = copy(wb=data1)  # 完成xlrd对象向xlwt对象转换
    table1 = data1.sheet_by_index(0)

    # pdb结构数量
    pdbNum = table1.nrows

    # 每年发表的论文数量
    paperYear, paperNum = dataInf(pdbNum)
    # 绘柱状图
    imgPaperDate(paperYear, paperNum)
    # 统计未发表的结构数量
    TobePublished(pdbNum)
