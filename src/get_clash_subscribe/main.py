import os
import re
import smtplib
import sys
import time
from email.mime.text import MIMEText
from email.utils import formataddr

import requests
import yaml

requests.packages.urllib3.disable_warnings()


ok_code = [200, 201, 202, 203, 204, 205, 206]


def write_log(content, level="INFO"):

    date_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    update_log = f"[{date_str}] [{level}] {content}\n"
    print(update_log)
    with open(f'./public/subscribe/log/{time.strftime("%Y-%m", time.localtime(time.time()))}-update.log', 'a', encoding="utf-8") as f:
        f.write(update_log)

def get_subscribe_main():
    dirs = './public/subscribe'
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    log_dir = "./log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    clash_req = requests.get("https://cdn.honglin.ac.cn/statically/gh/ermaozi/get_subscribe/main/subscribe/clash.yml")
    # 检查下载是否成功
    if not clash_req.status_code in ok_code:
        write_log("更新失败！无法拉取原订阅内容", "WARN")
        return
    
    try:
        clash_content = clash_req.content.decode("utf-8")
        clash_content_replaced = re.sub(r"https://raw.githubusercontent.com", "https://cdn.honglin.ac.cn/statically/gh", clash_content, flags=re.IGNORECASE)

        node_free_proxies = get_node_free()
        if node_free_proxies:
            clash_yaml = yaml.safe_load(clash_content_replaced)
            # 获取原订阅的节点列表
            original_proxies = clash_yaml.get('proxies', [])
            # 将原订阅的节点列表与node_free_proxies合并
            original_proxies.extend(node_free_proxies)
            # 更新原订阅的节点列表
            clash_yaml['proxies'] = original_proxies

            # 更新[♻️ 自动选择]列表
            original_groups = clash_yaml.get('proxy-groups', [])
            for group in original_groups:
                if group.get('name') == '♻️ 自动选择':
                    # 获取原订阅的节点列表
                    original_auto_proxies = group.get('proxies', [])
                    # 将原订阅的节点列表与node_free_proxies合并
                    node_free_proxy_names = [item['name'] for item in node_free_proxies]
                    original_auto_proxies.extend(node_free_proxy_names)
                    # 更新原订阅的节点列表
                    group['proxies'] = original_auto_proxies

            # 将更新后的内容写回到YAML文件
            clash_content_replaced = yaml.dump(clash_yaml, default_flow_style=False, allow_unicode=True)
            
        # 将更新后的内容写入文件
        with open(dirs + '/clash.yml', 'w', encoding="utf-8") as f:
            f.write(clash_content_replaced)
            write_log(f"获取原订阅成功", "INFO")
    except Exception as e:
        write_log(f"订阅解析错误", "WARN")
        return


def get_node_free():
    url = "https://cdn.honglin.ac.cn/statically/gh/Barabama/FreeNodes/main/nodes/nodefree.yaml"

    # Send a GET request to the specified URL
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the YAML content
        try:
            data = yaml.safe_load(response.content.decode('utf-8'))
            proxies = data.get('proxies', [])
            
            for item in proxies:
                # Check if the 'name' key exists and is not empty
                if 'name' in item and item['name']:
                    new_name = 'NF_' + item['name']
                    item['name'] = new_name
                else:
                    print("No name found in the item")

            return proxies
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            return

    else:
        print(f'Failed to retrieve the file: {response.status_code}')
        return

def main():
    get_subscribe_main()
    # get_node_free()


# 主函数入口
if __name__ == '__main__':
    main()
