# 根据上一步生成的excel文件去获取对应论文的详细信息:摘要和标题
import re
import string

import jsonlines
import xlrd

from selenium.webdriver.android.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


def getPaper(driver: WebDriver):
    res = []
    pubmed_doi = "https://pubmed.ncbi.nlm.nih.gov/?myncbishare=pubmedplus"
    excel = xlrd.open_workbook("./docs/BL18U1/PDB.xls")  # 打开excel文件
    sheet = excel.sheet_by_index(0)  # 根据下标获取工作薄，这里获取第一个
    col = sheet.col_values(1)  # 获取第一列的内容
    for i in range(len(col)):
        row = sheet.row_values(i)  # 获取到excel中第i行的数据
        if len(row[4]) == 0 or i == 0: continue

        doi_url = row[4].replace("http://dx.doi.org/", "")
        driver.get(pubmed_doi)
        inputBox = driver.find_element_by_xpath('//*[@id="id_term"]')
        btn = driver.find_elements_by_class_name("search-btn")[0]
        inputBox.send_keys(doi_url)
        btn.click()
        try:
            title = driver.find_elements_by_class_name("heading-title")[0].text
            abstract = driver.find_element_by_xpath('//*[@id="eng-abstract"]/p').text
            try:
                keywords = driver.find_element_by_xpath('//*[@id="abstract"]/p').text
            except:

                keywords = None
            print("--------------------------")
            print(title, abstract, keywords, i)
            print("--------------------------")
            res.append({
                "title": title,
                "abstract": abstract,
                "keywords": keywords,
                "index": i
            })
        except:
            print(doi_url + "未找到对应文章")

    return res


# 初始化一些例如下载路径之类的变量
options = webdriver.ChromeOptions()
prefs = {'profile.default_content_settings.popups': 0,
         'download.default_directory': 'D:\桌面\总文件夹\大学终章\毕业论文材料准备\PDBanalysis\docs\BL18U1\Paper'}
options.add_experimental_option('prefs', prefs)
options.add_argument('blink-settings=imagesEnabled=false')

chromeDriver = webdriver.Chrome('./chromedriver.exe', options=options)
chromeDriver.implicitly_wait(5)

res = getPaper(chromeDriver)
with jsonlines.open("./docs/BL18U1/paper.jsonlines", 'w') as w:
    for item in res:
        w.write(item)
