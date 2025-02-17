from mitmproxy import ctx, options
import json
from datetime import datetime
import os

class LayeredgeLogger:
    def __init__(self):
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, f'layeredge_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        self.requests = []
        
        # 设置环境变量代理
        os.environ['HTTP_PROXY'] = 'http://192.168.0.12:7890'
        os.environ['HTTPS_PROXY'] = 'http://192.168.0.12:7890'

        # 需要直接访问的域名
        self.direct_domains = [
            'google.com',
            'gstatic.com',
            'recaptcha.net',
            'googleapis.com'
        ]

    def request(self, flow):
        host = flow.request.pretty_host
        
        # 对于 Google 服务相关域名，使用直接连接
        if any(domain in host for domain in self.direct_domains):
            flow.request.proxy_mode = 'upstream'
            return

        # 只记录 layeredge.io 相关的请求
        if 'layeredge.io' in host:
            try:
                req_data = {
                    'timestamp': datetime.now().isoformat(),
                    'method': flow.request.method,
                    'url': flow.request.pretty_url,
                    'headers': dict(flow.request.headers),
                    'content': flow.request.content.decode('utf-8', 'ignore') if flow.request.content else None
                }
                self.requests.append({'request': req_data})
                self._save_to_file()
            except Exception as e:
                print(f"Error: {str(e)}")

    def response(self, flow):
        if 'layeredge.io' in flow.request.pretty_host:
            try:
                for req in self.requests:
                    if req.get('request', {}).get('url') == flow.request.pretty_url:
                        resp_data = {
                            'status_code': flow.response.status_code,
                            'headers': dict(flow.response.headers),
                            'content': flow.response.content.decode('utf-8', 'ignore') if flow.response.content else None
                        }
                        req['response'] = resp_data
                        self._save_to_file()
            except Exception as e:
                print(f"Error: {str(e)}")

    def _save_to_file(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.requests, f, ensure_ascii=False, indent=2)

addons = [
    LayeredgeLogger()
]
