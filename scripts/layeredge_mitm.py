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
        
        # 需要直接访问的域名
        self.direct_domains = [
            'google.com',
            'gstatic.com',
            'recaptcha.net',
            'googleapis.com'
        ]

    def load(self, loader):
        loader.add_option(
            name = "ssl_insecure",
            typespec = bool,
            default = True,
            help = "忽略SSL证书验证",
        )

    def running(self):
        ctx.options.ssl_insecure = True
        ctx.options.upstream_cert = False

    def request(self, flow):
        host = flow.request.pretty_host
        
        # 对于 Google 服务相关域名，直接放行
        if any(domain in host for domain in self.direct_domains):
            # 添加必要的 CORS 头
            if 'Origin' in flow.request.headers:
                flow.request.headers["Access-Control-Allow-Origin"] = "*"
                flow.request.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
                flow.request.headers["Access-Control-Allow-Headers"] = "*"
            return

        # 处理预加载资源
        if flow.request.pretty_url.endswith(('.woff2', '.js', '.css')):
            # 添加缓存控制头
            flow.request.headers["Cache-Control"] = "no-cache"
            return

        # 只记录 layeredge.io 相关的请求
        if 'layeredge.io' in host:
            try:
                # 跳过资源文件的记录
                if flow.request.pretty_url.endswith(('.woff2', '.js', '.css', '.png', '.jpg', '.gif')):
                    return

                req_data = {
                    'timestamp': datetime.now().isoformat(),
                    'method': flow.request.method,
                    'url': flow.request.pretty_url,
                    'headers': dict(flow.request.headers),
                    'content': flow.request.content.decode('utf-8', 'ignore') if flow.request.content else None
                }
                print(f"捕获请求: {flow.request.method} {flow.request.pretty_url}")
                self.requests.append({'request': req_data})
                self._save_to_file()
            except Exception as e:
                print(f"Error: {str(e)}")

    def response(self, flow):
        host = flow.request.pretty_host

        # 处理 Google reCAPTCHA 响应
        if any(domain in host for domain in self.direct_domains):
            flow.response.headers["Access-Control-Allow-Origin"] = "*"
            flow.response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            flow.response.headers["Access-Control-Allow-Headers"] = "*"
            return

        # 处理资源文件响应
        if flow.request.pretty_url.endswith(('.woff2', '.js', '.css')):
            flow.response.headers["Cache-Control"] = "public, max-age=31536000"
            flow.response.headers["Access-Control-Allow-Origin"] = "*"
            return

        # 只处理 layeredge.io 相关的响应
        if 'layeredge.io' in host:
            try:
                # 跳过资源文件的记录
                if flow.request.pretty_url.endswith(('.woff2', '.js', '.css', '.png', '.jpg', '.gif')):
                    return

                for req in self.requests:
                    if req.get('request', {}).get('url') == flow.request.pretty_url:
                        resp_data = {
                            'status_code': flow.response.status_code,
                            'headers': dict(flow.response.headers),
                            'content': flow.response.content.decode('utf-8', 'ignore') if flow.response.content else None
                        }
                        req['response'] = resp_data
                        self._save_to_file()
                        print(f"记录响应: {flow.request.method} {flow.request.pretty_url} - {flow.response.status_code}")
            except Exception as e:
                print(f"Error: {str(e)}")

    def _save_to_file(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.requests, f, ensure_ascii=False, indent=2)

addons = [
    LayeredgeLogger()
]
