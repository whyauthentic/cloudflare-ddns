import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

zone_id = os.getenv('ZONE_ID')
api_key = os.getenv('API_KEY')
subdomain = os.getenv('SUBDOMAIN')

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={subdomain}'

while True:
    try:
        # get current IP address
        current_ip = requests.get('https://api.ipify.org').text

        # get current Cloudflare DNS record
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # update Cloudflare DNS record if necessary
        cf_record_id = response.json()['result'][0]['id']
        cf_ip = response.json()['result'][0]['content']
        if current_ip != cf_ip:
            data = {
                'type': 'A',
                'name': subdomain,
                'content': current_ip,
                'proxied': True
            }
            response = requests.put(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{cf_record_id}', headers=headers, json=data)
            response.raise_for_status()
            print(f'Cloudflare DNS record updated: {subdomain} now points to {current_ip}')
        else:
            print(f'No update needed: {subdomain} already points to {current_ip}')

    except requests.exceptions.RequestException as e:
        print(f'Cloudflare API request failed: {e}')

    try:
        time.sleep(60)  # sleep for X minutes
    except KeyboardInterrupt:
        print('Exiting script')
        break
