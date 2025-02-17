from mitmproxy import ctx, options
import json
from datetime import datetime
import os
from mitmproxy import exceptions
import os

class LayeredgeLogger:
    def __init__(self):
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, f'layeredge_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        self.requests = []
        self.ignore_domains = [
            'infura.io', 
            'ethereum.org',
            'etherscan.io',
            'opensea.io'
        ]
        
        # 设置环境变量代理
        os.environ['HTTP_PROXY'] = 'http://192.168.0.12:7890'
        os.environ['HTTPS_PROXY'] = 'http://192.168.0.12:7890'
        
        # 静默所有默认日志
        ctx.options.termlog_verbosity = 'error'
        ctx.options.flow_detail = 0

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
        ctx.options.termlog_verbosity = 'error'
        ctx.options.flow_detail = 0

    def clientconnect(self, layer):
        # 静默处理客户端连接
        pass

    def serverconnect(self, layer):
        # 静默处理服务器连接
        pass

    def request(self, flow):
        # 检查域名是否需要忽略
        host = flow.request.pretty_host
        if any(domain in host for domain in self.ignore_domains):
            flow.request.verify = False
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
                print(f"捕获请求: {flow.request.method} {flow.request.pretty_url}")
                self.requests.append({'request': req_data})
            except Exception as e:
                print(f"处理请求时出错: {str(e)}")

    def response(self, flow):
        # 检查域名是否需要忽略
        host = flow.request.pretty_host
        if any(domain in host for domain in self.ignore_domains):
            return

        # 只处理 layeredge.io 相关的响应
        if 'layeredge.io' in host:
            try:
                for req in self.requests:
                    if req['request']['url'] == flow.request.pretty_url:
                        resp_data = {
                            'status_code': flow.response.status_code,
                            'headers': dict(flow.response.headers),
                            'content': flow.response.content.decode('utf-8', 'ignore') if flow.response.content else None
                        }
                        req['response'] = resp_data
                        self._save_to_file()
                        print(f"记录响应: {flow.request.method} {flow.request.pretty_url} - {flow.response.status_code}")
            except Exception as e:
                print(f"处理响应时出错: {str(e)}")

    def error(self, flow):
        # 忽略所有错误
        pass

    def _save_to_file(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.requests, f, ensure_ascii=False, indent=2)

addons = [
    LayeredgeLogger()
]
