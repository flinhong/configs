import os
import re
import time
from datetime import datetime

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
        clash_content = check_and_validate_file("https://git.io/emzclash")
        clash_content_replaced = re.sub(r"https://raw.githubusercontent.com", "https://cdn.honglin.ac.cn/statically/gh", clash_content, flags=re.IGNORECASE)
        # clash_content_replaced = re.sub(r"http://www.gstatic.com/generate_204", "https://www.gstatic.com/generate_204", clash_content_replaced, flags=re.IGNORECASE)
        # clash_content_replaced = re.sub(r"tolerance: 50", "tolerance: 10", clash_content_replaced, flags=re.IGNORECASE)

        # 将更新后的内容写入文件
        with open(dirs + '/clash.yml', 'w', encoding="utf-8") as f:
            f.write(clash_content_replaced)
            write_log(f"同步订阅成功", "INFO")

        extra_proxies = download_extra_proxies()
        if extra_proxies is not None:
            clash_yaml = yaml.safe_load(clash_content_replaced)
            clash_content_updated = append_proxies(clash_yaml, extra_proxies)
            # 将合并后的内容写入文件
            with open(dirs + '/clash.yml', 'w', encoding="utf-8") as f:
                f.write(clash_content_updated)
                write_log(f"合并订阅成功", "INFO")
        else:
            return
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

    # # 更新[♻️ 自动选择]列表
    # original_groups = clash_yaml.get('proxy-groups', [])
    # for group in original_groups:
    #     if group.get('name') == '♻️ 自动选择':
    #         # 获取原订阅的节点列表
    #         original_auto_proxies = group.get('proxies', [])
    #         # 将原订阅的节点列表与额外节点合并
    #         extra_proxy_names = [item['name'] for item in proxies]
    #         original_auto_proxies.extend(extra_proxy_names)
    #         # 更新原订阅的节点列表
    #         group['proxies'] = original_auto_proxies
    #         group['url'] = "https://www.facebook.com/common/referer_frame.php"
    #         group['interval'] = 60
    #         group['tolerance'] = 5
    # # 将更新后的内容写回到YAML文件
    # clash_yaml_replaced = yaml.dump(clash_yaml, default_flow_style=False, allow_unicode=True)
    # return clash_yaml_replaced

    # 追加[🪐 负载均衡]列表
    original_groups = clash_yaml.get('proxy-groups', [])
    original_groups.append({
        'name': "🪐 负载均衡",
        'type': "load-balance",
        'url': "https://client3.google.com/generate_204",
        'interval': 120,
        'strategy': "consistent-hashing",
        'proxies': [item['name'] for item in proxies]
    })
    
    # 修改原[♻️ 自动选择]列表
    for group in original_groups:
        if group.get('name') == '♻️ 自动选择':
            # 获取原订阅的节点列表
            original_auto_proxies = group.get('proxies', [])
            # 将负载均衡添加到自动选择
            original_auto_proxies.insert(0, "🪐 负载均衡")
            # 更新原订阅的节点列表
            group['proxies'] = original_auto_proxies
            group['url'] = "https://client3.google.com/generate_204"
            group['interval'] = 60
            group['tolerance'] = 1

    clash_yaml_replaced = yaml.dump(clash_yaml, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return clash_yaml_replaced

def validate_yaml(data):
    try:
        yaml.safe_load(data)
        return True
    except yaml.YAMLError as exc:
        print(f"Error validating YAML: {e}")
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

def download_extra_proxies():
    current_date = datetime.now()
    current_date_str = (current_date).strftime('%Y/%m/%Y%m%d')

    urls = [
        "https://raw.githubusercontent.com/zhangkaiitugithub/passcro/main/speednodes.yaml",
        # "https://raw.githubusercontent.com/NiREvil/vless/main/sub/clash-meta-wg.yml",
        # "https://raw.githubusercontent.com/ts-sf/fly/main/clash",
        # "https://raw.githubusercontent.com/MrMohebi/xray-proxy-grabber-telegram/master/collected-proxies/clash-meta/actives_under_1000ms.yaml",
        # "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge_yaml.yml",
        "https://suo.yt/d5UCwQr", # https://github.com/Pawdroid/Free-servers
        f"https://v2rayshare.githubrowcontent.com/{current_date_str}.yaml",
        f"https://nodefree.githubrowcontent.com/{current_date_str}.yaml",
        "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.yml",
        "https://bin.mudfish.net/r/249-7825-3630"
    ]
    all_proxies = []

    for file_url in urls:
        try:
            data = check_and_validate_file(file_url)
            if data is not None:
                proxies = get_extra_proxies(data)
                all_proxies.extend(proxies)
            
        except Exception as e:
            print(f"Error downloading or processing {file_url}: {e}")

    unique_proxies = remove_duplicate_proxies(all_proxies)
    return unique_proxies

def remove_duplicate_proxies(proxies):
    seen_servers = set()
    unique_proxies = []
    for proxy in proxies:
        server = proxy.get('server')
        if server and server not in seen_servers:
            unique_proxies.append(proxy)
            seen_servers.add(server)
    return unique_proxies

def get_extra_proxies(data):
    yaml_data = yaml.safe_load(data)
    proxies = yaml_data.get('proxies', [])
    filter_string = ['未知', 'tg', 'TG', 'KB/s']
    filtered_proxies = [proxy for proxy in proxies if not any(str in proxy['name'] for str in filter_string)]
    # filtered_proxies = [proxy for proxy in filtered_proxies if not proxy['type']=='ss' ]

    # 防止名称和 ermz 重复
    for proxy in filtered_proxies:
        if 'name' in proxy and proxy['name']:
            proxy['name'] = f"X_{proxy['name']}"
        else:
            print("No name found in the proxy")
            return None

    return filtered_proxies

def main():
    get_subscribe_main()


# 主函数入口
if __name__ == '__main__':
    main()
