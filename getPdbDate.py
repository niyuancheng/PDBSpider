import string
import time

import winsound
from selenium.webdriver.android.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

import xlrd
# 导入excel表格的处理函数
import xlwt
from xlutils.copy import copy
from progressbar import ProgressBar
import re

cols = ('线站名称', '蛋白质编号', 'Pdb_DOI', 'PubMed_DOI', '文献链接', '文献标题', '日期', '组织', '作者')
def isSame(a, b):
    if(len(a) == len(b)):
        for i in range(len(a)):
            if(a[i] != b[i]):
                return False
        return True
    return False

def getAllPdbsByXianzhan(name: string, driver: WebDriver):
    url = "https://www.rcsb.org/"
    result = []
    driver.get(url)
    input = driver.find_element_by_xpath('//*[@id="search-bar-input-text"]')
    btn = driver.find_element_by_xpath('//*[@id="search-icon"]')
    input.send_keys(name)
    btn.click()
    lastdata = []
    while True:
        time.sleep(3)
        data = []
        nextPageBtn = driver.find_elements_by_xpath('//*[@class="glyphicon glyphicon-triangle-right"]')[2]
        aArray = driver.find_elements_by_xpath('//*[@class="results-item-header"]/tbody/tr/td[1]/h3/a')
        for i in range(len(aArray)):
            el = aArray[i]
            data.append(el.text)
        if(isSame(data,lastdata)):
            break
        for i in range(len(data)):
            result.append(data[i])
        lastdata = data
        nextPageBtn.click()
    return result

# 根据指定的蛋白质名称获取对应的信息
def getPdbDate(pdb: string, baseURL: string, driver: WebDriver):
    pubmed_doi_str = ""
    pubmed_url = ""

    url_pdb = baseURL + pdb
    driver.get(url_pdb)
    doi = driver.find_element_by_xpath('//*[@id="header_doi"]/a')
    header_organism = driver.find_element_by_xpath('//*[@id="header_organism"]/a')
    header_deposited_released_dates = driver.find_element_by_xpath('//*[@id="header_deposited-released-dates"]')
    header_deposition_author = driver.find_element_by_xpath('//*[@id="header_deposition-authors"]')
    try:
        pubmed_doi = driver.find_element_by_xpath('//*[@id="pubmedDOI"]/a')
    except:
        pubmed_doi = None
    pubmed_title = driver.find_element_by_xpath('//*[@id="primarycitation"]/h4')
    download_button = driver.find_element_by_xpath('//*[@id="dropdownMenuDownloadFiles"]')
    pdb_download = driver.find_element_by_xpath('//*[@id="DownloadFilesButton"]/ul/li[6]/a')
    if (pubmed_doi is not None):
        pubmed_url = pubmed_doi.get_attribute("href")
        pudmed_doi_str = pubmed_doi.text
    downloadPdb(download_button, pdb_download)
    return ["BL18U1", pdb, doi.text, pubmed_doi_str, pubmed_url, pubmed_title.text,
            header_deposited_released_dates.text, header_organism.text, header_deposition_author.text]


# 下载pdb格式的文件
def downloadPdb(btn: WebElement, pdb: WebElement):
    btn.click()
    pdb.click()


def createExcel(col, datalist, path: string):
    # 1. 创建excel的表格文件
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet('pdb文件数据', cell_overwrite_ok=True)
    for i in range(0, 9):
        sheet.write(0, i, col[i])
    for i in range(len(datalist)):
        data = datalist[i]
        for j in range(len(data)):
            sheet.write(i + 1, j, data[j])
    book.save(path)


options = webdriver.ChromeOptions()
prefs = {'profile.default_content_settings.popups': 0,
         'download.default_directory': 'D:\桌面\总文件夹\大学终章\毕业论文材料准备\PDBanalysis\docs\BL18U1\PDB'}
options.add_experimental_option('prefs', prefs)

chromeDriver = webdriver.Chrome('./chromedriver.exe', options=options)
chromeDriver.implicitly_wait(5)

Url = 'https://www.rcsb.org/structure/'
datalist = []

results = getAllPdbsByXianzhan("BL18U1", chromeDriver)
print(results)
for i in range(len(results)):
    datalist.append(getPdbDate(results[i],Url,chromeDriver))

createExcel(cols,datalist,"./docs/BL18U1/PDB.xls")
