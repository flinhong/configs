import os
import time
import logging
import ipaddress
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import yaml

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

# Load configuration
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources.yaml")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

def setup_logging():
    log_dir = CONFIG["log_dir"]
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f'{time.strftime("%Y-%m", time.localtime())}-update.log')
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
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return True
        # Specific check for 0.0.0.0 (though is_private/reserved usually catches it)
        if str(ip) == '0.0.0.0': 
            return True
    except ValueError:
        # Not an IP address, likely a domain name. 
        # We assume domains are public unless it's 'localhost' (checked above).
        pass
        
    return False

def probe_date():
    """Probe date-based URLs to determine the latest available date.
    Only returns today if ALL sources have today's file available;
    otherwise falls back to yesterday."""
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    date_templates = CONFIG["date_based_url_templates"]

    for entry in date_templates:
        template = entry["url"]
        date_fmt = entry["date_format"]
        date_part = today.strftime(date_fmt)
        url = template.format(date=date_part)
        try:
            response = requests.head(url, headers=CONFIG["headers"], timeout=10, verify=False)
            if response.status_code not in CONFIG["success_status_codes"]:
                logging.info(f"Today's file not yet available at {url}, falling back to yesterday")
                return yesterday
        except Exception as e:
            logging.info(f"Error probing {url}: {e}, falling back to yesterday")
            return yesterday

    logging.info("All date-based sources have today's file available, using today")
    return today


def fetch_content(url):
    """Fetch content from URL with timeout and validation."""
    try:
        logging.info(f"Downloading: {url}")
        response = requests.get(url, headers=CONFIG["headers"], timeout=CONFIG["timeout"], verify=False)
        if response.status_code in CONFIG["success_status_codes"]:
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
    filter_keywords = CONFIG["filter_keywords"]
    
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

        # 4. Filter reality-opts with invalid short-id
        if 'reality-opts' in proxy:
            reality_opts = proxy.get('reality-opts', {})
            raw_short_id = str(reality_opts.get('short-id', '')).strip()
            if not raw_short_id or not all(c in '0123456789abcdefABCDEF' for c in raw_short_id):
                logging.warning(f"Filtered proxy {proxy.get('name', 'unknown')}: reality-opts short-id '{raw_short_id}' missing or invalid")
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
    """Deduplicate proxies based on server address and name."""
    seen_servers = set()
    seen_names = set()
    unique_proxies = []
    for proxy in proxies:
        server = proxy.get("server")
        name = proxy.get("name")
        if not server or not name:
            continue

        server_key = str(server).lower()
        name_key = str(name).strip()

        if server_key in seen_servers or name_key in seen_names:
            continue

        unique_proxies.append(proxy)
        seen_servers.add(server_key)
        seen_names.add(name_key)

    return unique_proxies

def merge_proxies_to_config(config, lb_proxies, auto_proxies):
    """Merge proxies into the main configuration logic."""
    
    # 1. Filter and Update Proxy List
    original_proxies = config.get('proxies', [])
    if original_proxies is None:
        original_proxies = []
    
    # Filter original proxies for reality-opts without short-id
    filtered_original = []
    for proxy in original_proxies:
        if 'reality-opts' in proxy:
            reality_opts = proxy.get('reality-opts', {})
            raw_short_id = str(reality_opts.get('short-id', '')).strip()
            if not raw_short_id or not all(c in '0123456789abcdefABCDEF' for c in raw_short_id):
                logging.warning(f"Filtered proxy {proxy.get('name', 'unknown')}: reality-opts short-id '{raw_short_id}' missing or invalid")
                continue
        filtered_original.append(proxy)
    original_proxies = filtered_original
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
            
            auto_select_group['url'] = "https://client3.google.com/generate_204"
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

    rules_dir = CONFIG["rules_dir"]
    if not os.path.exists(rules_dir):
        os.makedirs(rules_dir)

    for name, provider in providers.items():
        url = provider.get('url', '')
        if not url:
            continue

        local_filename = f"{name}.yaml"
        local_path = os.path.join(rules_dir, local_filename)

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

        provider['url'] = f"{CONFIG['rules_base_url']}/{local_filename}"
        provider['path'] = f"./rules/{local_filename}"
        logging.info(f"Updated rule-provider {name} URL to {provider['url']}")

def main():
    setup_logging()

    output_dir = CONFIG["output_dir"]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Fetch Main Config
    main_url = CONFIG["main_url"]
    main_content = fetch_content(main_url)

    if not main_content:
        logging.error("Failed to fetch main subscription.")
        return


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

    lb_urls = list(CONFIG["lb_urls"])
    auto_urls = list(CONFIG["auto_urls"])

    current_date = probe_date()
    for entry in CONFIG["date_based_url_templates"]:
        date_part = current_date.strftime(entry["date_format"])
        auto_urls.insert(0, entry["url"].format(date=date_part))

    lb_proxies = fetch_and_process_subscriptions(lb_urls)
    logging.info(f"Fetched {len(lb_proxies)} unique proxies for Load Balancer.")

    auto_proxies = fetch_and_process_subscriptions(auto_urls)
    logging.info(f"Fetched {len(auto_proxies)} unique proxies for Auto Select.")

    # 3. Merge and Finalize
    final_config = merge_proxies_to_config(config, lb_proxies, auto_proxies)

    output_path = os.path.join(output_dir, 'clash.yml')
    try:
        with open(output_path, 'w', encoding="utf-8") as f:
            yaml.dump(final_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        logging.info(f"Successfully wrote config to {output_path}")
    except (OSError, yaml.YAMLError) as e:
        logging.error(f"Failed to write config file: {e}")

if __name__ == '__main__':
    main()
