import requests
import re
from bs4 import BeautifulSoup
import subprocess
import argparse

# 存储包存在状态的字典
package_existence = {}

parser = argparse.ArgumentParser()
parser.add_argument('-u','--url',help='Internal rubyGems URL')

args = parser.parse_args()

url = args.url  # 替换成你要请求的网址

# 发送HTTP请求并获取页面内容
response = requests.get(url)
html = response.text

# 使用BeautifulSoup解析HTML页面
soup = BeautifulSoup(html, 'html.parser')

# 查找指定的<li>标签
li_tags = soup.find_all('li', {'class': 'gem-version'})

# 提取每个<li>标签内的<h2>标签文本
results = []
for li_tag in li_tags:
    h2_tag = li_tag.find('h2')
    result = h2_tag.text.strip()
    results.append(result)

#print(results)

clean_results= []
for result in results:
    # 使用正则表达式匹配并删除括号及其中的内容
    clean_result = re.sub(r'\s?\(.*?\)', '', result)

    #print(clean_result)
    clean_results.append(clean_result)

# 遍历每个RubyGem包名
for gem_name in clean_results:
    # 执行Gem命令获取包信息
    command = f'gem search {gem_name}'
    #print(command)
    output = subprocess.check_output(command, shell=True, encoding='utf-8')

    # 检查输出中是否包含包名
    if gem_name in output:
        package_existence[gem_name] = True
    else:
        package_existence[gem_name] = False

# 输出包存在状态
for gem_name, exists in package_existence.items():
    #print(gem_name)
    if exists:
        print(f'{gem_name} exists')
    else:
        print(f'{gem_name} does not exist')
