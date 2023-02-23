"""
Description: 调用高德地图地理编码API
Author: cheereus
Date: 2020-08-03 14:23:35
LastEditTime: 2023-02-22 15:15:14
LastEditors: cheereus
"""
import requests
import time
import pandas as pd
from tqdm import trange
from urllib.parse import quote

# 高德地理编码 API
baseUrl = 'https://restapi.amap.com/v3/geocode/geo?'
# header 可有可无
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/59.0.3071.115 Safari/537.36"}

# key 列表
key_list = [
    'e363ffe111111111111111111134acf1',
    '0785f491111111111111111111fd1a99',
    '65a4aed11111111111111111113ce16d',
    'f3a8be71111111111111111111406b5c'
]

# 原始数据的 excel
fileName = 'data.xlsx'
# 输出数据的 csv
output_fileName = 'output.csv'


# 从 xlsx 文件中获取地址信息
def get_excel_data(file_path):
    # 获取经纬度 list
    sheet = pd.read_excel(file_path, sheet_name=0, header=0)
    return sheet.values


address_list = get_excel_data(fileName)
rows = len(address_list)


# 请求高德地图 API 返回经纬度
# key 为高德开放平台应用生成的密钥
# addr 结构化地址
def get_gaode_data(addr, key="cd6866c941e61e69d63c4f1e7fdc3ed2"):
    addr_encoded = quote(addr, safe='')
    response = requests.get(url=f'{baseUrl}address={addr_encoded}&key={key}', headers=headers)
    data = response.json()
    return data


count_api_err = 0
count_net_err = 0
# 写入 csv，写入 xlsx 太麻烦了，表头自己加一下，经纬度在最开头两列
with open(output_fileName, 'w', encoding='gbk') as output:
    for i in trange(rows):
        address_info = list(map(str, address_list[i]))  # 预处理一下数据，方便后面以文本形式写入csv
        address = address_info[19]  # 从 excel 数据中取 address，此处取的第19列
        key = key_list[i // 3000]  # 每 3000 条数据换一个 key，如果 key_list 不够这一步会报错，没测过
        try:
            res = get_gaode_data(address, key=key)
            if res.get('geocodes'):
                longitude, latitude = res['geocodes'][0]['location'].split(',')  # 获得经纬度
                output.writelines(','.join([longitude, latitude] + address_info) + '\n')
            else:
                info, infocode = res['info'], res['infocode']  # 保存报错信息
                output.writelines(','.join([info, infocode + f':{key}'] + address_info) + '\n')
                count_api_err += 1
        except:
            info, infocode = '其他报错', 'nocode'  # 保存报错信息
            output.writelines(','.join([info, infocode + f':{key}'] + address_info) + '\n')
            count_net_err += 1
        time.sleep(0.5) # 可有可无，太频繁可能会导致 API 请求报错增多
        if i % 100 == 0:
            print('\n')
            print('当前使用key', key)
            print('API报错数', count_api_err)
            print('NET报错数', count_net_err)
