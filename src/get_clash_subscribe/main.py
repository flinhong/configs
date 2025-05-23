import os
import re
import smtplib
import sys
import time
from datetime import datetime, timedelta
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
    log_dir = "./public/subscribe/log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    clash_req = requests.get("https://git.io/emzclash")

    # 检查下载是否成功
    if not clash_req.status_code in ok_code:
        write_log("更新失败！无法拉取 emzclash 订阅内容", "WARN")
        return None
    
    try:
        clash_content = clash_req.content.decode("utf-8")
        clash_content_replaced = re.sub(r"https://raw.githubusercontent.com", "https://cdn.honglin.ac.cn/statically/gh", clash_content, flags=re.IGNORECASE)

        node_free_proxies = get_node_free_proxies()
        if node_free_proxies is not None:
            clash_yaml = yaml.safe_load(clash_content_replaced)
            clash_content_replaced = append_proxies(clash_yaml, node_free_proxies)
        
        v2ray_share_proxies = get_v2ray_share_proxies()
        if v2ray_share_proxies is not None:
            clash_yaml = yaml.safe_load(clash_content_replaced)
            clash_content_replaced = append_proxies(clash_yaml, v2ray_share_proxies)
            
        # 将更新后的内容写入文件
        with open(dirs + '/clash.yml', 'w', encoding="utf-8") as f:
            f.write(clash_content_replaced)
            write_log(f"更新订阅成功", "INFO")
    except Exception as e:
        write_log(f"订阅解析错误", "WARN")
        return None
    
def append_proxies(clash_yaml, proxies):
    # 将新的节点列表追加到原订阅的节点列表
    original_proxies = clash_yaml.get('proxies', [])
    # 将原订阅的节点列表与 node_free_proxies 合并
    original_proxies.extend(proxies)
    # 更新原订阅的节点列表
    clash_yaml['proxies'] = original_proxies

    # 更新[♻️ 自动选择]列表
    original_groups = clash_yaml.get('proxy-groups', [])
    for group in original_groups:
        if group.get('name') == '♻️ 自动选择':
            # 获取原订阅的节点列表
            original_auto_proxies = group.get('proxies', [])
            # 将原订阅的节点列表与node_free_proxies合并
            node_free_proxy_names = [item['name'] for item in proxies]
            original_auto_proxies.extend(node_free_proxy_names)
            # 更新原订阅的节点列表
            group['proxies'] = original_auto_proxies
    # 将更新后的内容写回到YAML文件
    clash_yaml_replaced = yaml.dump(clash_yaml, default_flow_style=False, allow_unicode=True)
    return clash_yaml_replaced

def validate_yaml(data):
    try:
        yaml.safe_load(data)
        return True
    except yaml.YAMLError as exc:
        print(exc)
        return False

def check_and_validate_file(url):
    response = requests.get(url)
    print(f"获取 {url} 状态码: {response.status_code}")
    if not response.status_code in ok_code:
        return None
    
    try:
        data = response.content.decode('utf-8')
        if validate_yaml(data):
            return data
        else:
            return None
    except Exception as e:
        print(e)
        return None

def get_node_free_proxies():
    # 仅下载 nodefree 的 clash 订阅
    # https://nodefree.githubrowcontent.com/2025/05/20250521.yaml
    base_url = "https://nodefree.githubrowcontent.com/"
    current_date = datetime.now()
    current_date_str = current_date.strftime('%Y/%m/%Y%m%d')
    file_url = f"{base_url}{current_date_str}.yaml"

    # 如果当天的订阅获取失败，则获取前一天的订阅
    data_today = check_and_validate_file(file_url)
    if data_today is not None:
        proxies = get_extra_proxies(data_today, "NF")
        return proxies
    else:
        delta = timedelta(days=1)
        date_str = (current_date - delta).strftime('%Y/%m/%Y%m%d')
        new_url = f"{base_url}{date_str}.yaml"
        data_previous = check_and_validate_file(new_url)
        if data_previous is not None:
            proxies = get_extra_proxies(data_previous, "NF")
            return proxies
        else:
            print(f"获取 nodefree 订阅失败")
            return None

def get_v2ray_share_proxies():
    # 仅下载 v2rayshare 的 clash 订阅
    # https://v2rayshare.githubrowcontent.com/2025/05/20250523.yaml
    base_url = "https://v2rayshare.githubrowcontent.com/"
    current_date = datetime.now()
    current_date_str = current_date.strftime('%Y/%m/%Y%m%d')
    file_url = f"{base_url}{current_date_str}.yaml"

    # 如果当天的订阅获取失败，则获取前一天的订阅
    data_today = check_and_validate_file(file_url)
    if data_today is not None:
        proxies = get_extra_proxies(data_today, "VS")
        return proxies
    else:
        delta = timedelta(days=1)
        date_str = (current_date - delta).strftime('%Y/%m/%Y%m%d')
        new_url = f"{base_url}{date_str}.yaml"
        data_previous = check_and_validate_file(new_url)
        if data_previous is not None:
            proxies = get_extra_proxies(data_previous, "VS")
            return proxies
        else:
            print(f"获取 v2rayshare 订阅失败")
            return None

def get_extra_proxies(data, prefix):
    yaml_data = yaml.safe_load(data)
    proxies = yaml_data.get('proxies', [])
    for proxy in proxies:
        if 'name' in proxy and proxy['name']:
            proxy['name'] = f"{prefix}_{proxy['name']}"
        else:
            print("No name found in the proxy")
            return None
    return proxies

def main():
    get_subscribe_main()


# 主函数入口
if __name__ == '__main__':
    main()
