import os
import re
import time
import logging
import ipaddress
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import yaml

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

# Configuration
SUCCESS_STATUS_CODES = [200, 201, 202, 203, 204, 205, 206]
OUTPUT_DIR = './public/subscribe'
LOG_DIR = './public/subscribe/log'
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://bing.com/",
}
TIMEOUT = 30  # Seconds
RULES_DIR = './public/rules'
RULES_BASE_URL = "https://cdn.honglin.ac.cn/statically/gh/flinhong/configs/public/rules"

def setup_logging():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    log_file = os.path.join(LOG_DIR, f'{time.strftime("%Y-%m", time.localtime())}-update.log')
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )

def is_local_server(server_address):
    """Check if the server address is a local IP or localhost."""
    if not server_address:
        return True # Treat empty as invalid/local to skip
    
    s = str(server_address).lower()
    if s == 'localhost':
        return True
    
    try:
        ip = ipaddress.ip_address(s)
        # Check for private (10., 192.168., 172.16.), loopback (127.), or link-local
        if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
            return True
        # Specific check for 0.0.0.0 (though is_private/reserved usually catches it)
        if str(ip) == '0.0.0.0': 
            return True
    except ValueError:
        # Not an IP address, likely a domain name. 
        # We assume domains are public unless it's 'localhost' (checked above).
        pass
        
    return False

DATE_BASED_URL_TEMPLATES = [
    ("https://static.v2rayshare.net/{date}.yaml", "%Y/%m/%Y%m%d"),
    ("https://node.nodefree.me/{date}.yaml", "%Y/%m/%Y%m%d"),
]


def probe_date():
    """Probe date-based URLs to determine the latest available date.
    Only returns today if ALL sources have today's file available;
    otherwise falls back to yesterday."""
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    for template, date_fmt in DATE_BASED_URL_TEMPLATES:
        date_part = today.strftime(date_fmt)
        url = template.format(date=date_part)
        try:
            response = requests.head(url, headers=HEADERS, timeout=10, verify=False)
            if response.status_code not in SUCCESS_STATUS_CODES:
                logging.info(f"Today's file not yet available at {url}, falling back to yesterday")
                return yesterday
        except Exception as e:
            logging.info(f"Error probing {url}: {e}, falling back to yesterday")
            return yesterday

    logging.info("All date-based sources have today's file available, using today")
    return today


def get_dynamic_urls(is_auto=False):
    """Generate URLs based on date."""
    current_date = probe_date()

    if is_auto:
        return [
            *(t.format(date=current_date.strftime(fmt)) for t, fmt in DATE_BASED_URL_TEMPLATES),
            "https://tt.vg/freeclash",
            "https://raw.githubusercontent.com/free18/v2ray/main/c.yaml",
            "https://raw.githubusercontent.com/Ruk1ng001/freeSub/main/clash.yaml",
            "https://raw.githubusercontent.com/mahdibland/SSAggregator/master/sub/sub_merge_yaml.yml",
            "https://raw.githubusercontent.com/ts-sf/fly/main/clash"
        ]
    else:
        return [
            "https://raw.githubusercontent.com/zhangkaiitugithub/passcro/main/speednodes.yaml",
            "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.yml"
        ]

def fetch_content(url):
    """Fetch content from URL with timeout and validation."""
    try:
        logging.info(f"Downloading: {url}")
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
        if response.status_code in SUCCESS_STATUS_CODES:
            return response.content.decode('utf-8')
        else:
            logging.warning(f"Failed to fetch {url}, status code: {response.status_code}")
            return None
    except Exception as e:
        logging.warning(f"Exception fetching {url}: {e}")
        return None

def parse_yaml_safe(content):
    """Safely parse YAML content."""
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError as e:
        logging.warning(f"YAML parsing error: {e}")
        return None

def process_proxies(content):
    """Extract, filter, and rename proxies from YAML content."""
    data = parse_yaml_safe(content)
    if not data or 'proxies' not in data:
        return []

    proxies = data.get('proxies', [])
    filter_keywords = ['未知', 'tg', 'TG', 'KB/s']
    
    valid_proxies = []
    for proxy in proxies:
        # 1. Check necessary fields
        if 'name' not in proxy or not proxy['name']:
            continue
        if 'server' not in proxy or not proxy['server']:
            continue
            
        # 2. Filter Local IPs
        if is_local_server(proxy['server']):
            continue

        # 3. Filter http type proxies
        if proxy.get('type', '').lower() == 'http':
            continue

        # 4. Filter reality-opts without short-id
        if 'reality-opts' in proxy:
            reality_opts = proxy.get('reality-opts', {})
            if 'short-id' not in reality_opts or not reality_opts['short-id']:
                logging.warning(f"Filtered proxy {proxy.get('name', 'unknown')}: reality-opts missing short-id")
                continue

        # 4. Fix missing cipher
        if 'cipher' not in proxy or not proxy['cipher']:
            proxy['cipher'] = 'auto'

        # 5. Clean name: remove non-printable characters
        clean_name = "".join(ch for ch in str(proxy['name']) if ch.isprintable()).strip()
        if not clean_name:
            continue
        proxy['name'] = clean_name
            
        # 6. Filter unwanted names
        if any(kw in proxy['name'] for kw in filter_keywords):
            continue
            
        # 7. Rename to avoid collisions
        proxy['name'] = f"X_{proxy['name']}"
        valid_proxies.append(proxy)
        
    return valid_proxies

def fetch_and_process_subscriptions(urls):
    """Concurrent fetch and process of multiple subscription URLs."""
    all_proxies = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(fetch_content, url): url for url in urls}
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                content = future.result()
                if content:
                    proxies = process_proxies(content)
                    all_proxies.extend(proxies)
            except Exception as e:
                logging.error(f"Error processing {url}: {e}")

    return remove_duplicate_proxies(all_proxies)

def remove_duplicate_proxies(proxies):
    """Deduplicate proxies based on server address only."""
    seen_servers = set()
    unique_proxies = []
    for proxy in proxies:
        server = proxy.get("server")
        if not server:
            continue
            
        # Use lower case for consistent string comparison
        server_key = str(server).lower()
        
        if server_key not in seen_servers:
            unique_proxies.append(proxy)
            seen_servers.add(server_key)
            
    return unique_proxies

def filter_reality_opts_proxies(proxies):
    """Filter out proxies that have reality-opts but missing short-id."""
    filtered = []
    for proxy in proxies:
        if 'reality-opts' in proxy:
            reality_opts = proxy.get('reality-opts', {})
            if 'short-id' not in reality_opts or not reality_opts['short-id']:
                logging.warning(f"Filtered proxy {proxy.get('name', 'unknown')}: reality-opts missing short-id")
                continue
        filtered.append(proxy)
    return filtered

def merge_proxies_to_config(config, lb_proxies, auto_proxies):
    """Merge proxies into the main configuration logic."""
    
    # 1. Filter and Update Proxy List
    original_proxies = config.get('proxies', [])
    if original_proxies is None:
        original_proxies = []
    
    # Filter original proxies for reality-opts without short-id
    original_proxies = filter_reality_opts_proxies(original_proxies)
    logging.info(f"Filtered original proxies: {len(original_proxies)} remaining")
    
    # Add both sets of proxies to the main list
    original_proxies.extend(lb_proxies)
    original_proxies.extend(auto_proxies)
    config['proxies'] = original_proxies

    # 2. Update Proxy Groups
    groups = config.get('proxy-groups', [])
    
    # Logic for Load Balance Group (from lb_proxies)
    if lb_proxies:
        lb_group = {
            'name': "🪐 负载均衡",
            'type': "load-balance",
            'url': "https://client3.google.com/generate_204",
            'interval': 120,
            'strategy': "consistent-hashing",
            'proxies': [p['name'] for p in lb_proxies]
        }
        groups.append(lb_group)

    # Logic for Auto Select Group (modified by both)
    auto_select_group = next((g for g in groups if g.get('name') == '♻️ 自动选择'), None)
    
    if auto_select_group:
        current_proxies = auto_select_group.get('proxies', [])
        
        # Add "🪐 负载均衡" to Auto Select if it exists
        if lb_proxies:
            if "🪐 负载均衡" not in current_proxies:
                current_proxies.insert(0, "🪐 负载均衡")
            
            auto_select_group['url'] = "https://client3.google.com/generate_204"
            auto_select_group['interval'] = 60
            auto_select_group['tolerance'] = 1

        # Add auto_proxies directly to Auto Select
        if auto_proxies:
            current_proxies.extend([p['name'] for p in auto_proxies])
            
            auto_select_group['url'] = "https://www.facebook.com/common/referer_frame.php"
            auto_select_group['interval'] = 60
            auto_select_group['tolerance'] = 5

        auto_select_group['proxies'] = current_proxies

    config['proxy-groups'] = groups
    return config

def convert_list_to_yaml(content):
    lines = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append('')
        elif stripped.startswith('#'):
            lines.append(stripped)
        else:
            lines.append(f"- {stripped}")
    return 'payload:\n' + '\n'.join(f'  {l}' if l else '' for l in lines)

def download_rule_providers(config):
    providers = config.get('rule-providers', {})
    if not providers:
        return

    if not os.path.exists(RULES_DIR):
        os.makedirs(RULES_DIR)

    for name, provider in providers.items():
        url = provider.get('url', '')
        if not url:
            continue

        local_filename = f"{name}.yaml"
        local_path = os.path.join(RULES_DIR, local_filename)

        content = fetch_content(url)
        if content:
            yaml_content = convert_list_to_yaml(content)
            try:
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
                logging.info(f"Downloaded rule-provider {name} -> {local_path}")
            except Exception as e:
                logging.error(f"Failed to write rule-provider {name}: {e}")
                continue
        else:
            logging.warning(f"Failed to download rule-provider {name} from {url}, keeping original URL")
            continue

        provider['url'] = f"{RULES_BASE_URL}/{local_filename}"
        provider['path'] = f"./rules/{local_filename}"
        logging.info(f"Updated rule-provider {name} URL to {provider['url']}")

def main():
    setup_logging()
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. Fetch Main Config
    main_url = "https://github.com/ermaozi/get_subscribe/raw/main/subscribe/clash.yml"
    main_content = fetch_content(main_url)
    
    if not main_content:
        logging.error("Failed to fetch main subscription.")
        return

    # Apply Main Config Replacements
    # https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/refs/heads/master/Clash/ChinaDomain.list
    # https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/refs/heads/master/Clash/Providers/ChinaCompanyIp.yaml
    # main_content = re.sub(r"https://raw.githubusercontent.com", "https://core.cdn.honglin.ac.cn/statically/gh", main_content, flags=re.IGNORECASE)
    # main_content = re.sub(r"/refs/heads/master/Clash", "/Clash/Providers", main_content, flags=re.IGNORECASE)
    # main_content = re.sub(r"\.list", ".yaml", main_content, flags=re.IGNORECASE)

    try:
        config = yaml.safe_load(main_content)
        logging.info("Main subscription fetched and parsed.")
    except Exception as e:
        logging.error(f"Failed to parse main subscription: {e}")
        return

    # 2. Download Rule Providers
    logging.info("Downloading rule-providers...")
    download_rule_providers(config)

    # 3. Fetch Extra Proxies (Concurrently)
    logging.info("Fetching extra proxies...")
    
    lb_urls = get_dynamic_urls(is_auto=False)
    auto_urls = get_dynamic_urls(is_auto=True)

    lb_proxies = fetch_and_process_subscriptions(lb_urls)
    logging.info(f"Fetched {len(lb_proxies)} unique proxies for Load Balancer.")

    auto_proxies = fetch_and_process_subscriptions(auto_urls)
    logging.info(f"Fetched {len(auto_proxies)} unique proxies for Auto Select.")

    # 3. Merge and Finalize
    final_config = merge_proxies_to_config(config, lb_proxies, auto_proxies)

    output_path = os.path.join(OUTPUT_DIR, 'clash.yml')
    try:
        with open(output_path, 'w', encoding="utf-8") as f:
            yaml.dump(final_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        logging.info(f"Successfully wrote config to {output_path}")
    except Exception as e:
        logging.error(f"Failed to write config file: {e}")

if __name__ == '__main__':
    main()
