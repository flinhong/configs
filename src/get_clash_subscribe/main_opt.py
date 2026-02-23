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

def get_dynamic_urls(is_auto=False):
    """Generate URLs based on date."""
    current_date = datetime.now().date() - timedelta(days=1)
    current_date_str = current_date.strftime('%Y/%m/%Y%m%d')

    if is_auto:
        return [
            f"https://v2rayshare.githubrowcontent.com/{current_date_str}.yaml",
            f"https://nodefree.githubrowcontent.com/{current_date_str}.yaml",
            "https://tt.vg/freeclash",
            "https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/c.yaml"
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

        # 3. Fix missing cipher
        if 'cipher' not in proxy or not proxy['cipher']:
            proxy['cipher'] = 'auto'

        # 4. Clean name: remove non-printable characters
        clean_name = "".join(ch for ch in str(proxy['name']) if ch.isprintable()).strip()
        if not clean_name:
            continue
        proxy['name'] = clean_name
            
        # 5. Filter unwanted names
        if any(kw in proxy['name'] for kw in filter_keywords):
            continue
            
        # 6. Rename to avoid collisions
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

def merge_proxies_to_config(config, lb_proxies, auto_proxies):
    """Merge proxies into the main configuration logic."""
    
    # 1. Update Proxy List
    original_proxies = config.get('proxies', [])
    if original_proxies is None:
        original_proxies = []
        
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
    main_content = re.sub(r"https://raw.githubusercontent.com", "https://cdn.honglin.ac.cn/statically/gh", main_content, flags=re.IGNORECASE)
    main_content = re.sub(r"/master", "@master", main_content, flags=re.IGNORECASE)

    try:
        config = yaml.safe_load(main_content)
        logging.info("Main subscription fetched and parsed.")
    except Exception as e:
        logging.error(f"Failed to parse main subscription: {e}")
        return

    # 2. Fetch Extra Proxies (Concurrently)
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
