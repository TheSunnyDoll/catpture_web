from mitmproxy import ctx
import json
from datetime import datetime
import os

class LayeredgeLogger:
    def __init__(self):
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, f'layeredge_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        self.requests = []

    def request(self, flow):
        # 只记录 layeredge.io 相关的请求
        if 'layeredge.io' in flow.request.pretty_host:
            req_data = {
                'timestamp': datetime.now().isoformat(),
                'method': flow.request.method,
                'url': flow.request.pretty_url,
                'headers': dict(flow.request.headers),
                'content': flow.request.content.decode('utf-8', 'ignore') if flow.request.content else None
            }
            ctx.log.info(f"捕获请求: {flow.request.method} {flow.request.pretty_url}")
            self.requests.append({'request': req_data})

    def response(self, flow):
        # 只处理 layeredge.io 相关的响应
        if 'layeredge.io' in flow.request.pretty_host:
            for req in self.requests:
                if req['request']['url'] == flow.request.pretty_url:
                    resp_data = {
                        'status_code': flow.response.status_code,
                        'headers': dict(flow.response.headers),
                        'content': flow.response.content.decode('utf-8', 'ignore') if flow.response.content else None
                    }
                    req['response'] = resp_data
                    # 保存到文件
                    self._save_to_file()
                    ctx.log.info(f"记录响应: {flow.request.method} {flow.request.pretty_url} - {flow.response.status_code}")

    def _save_to_file(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.requests, f, ensure_ascii=False, indent=2)

addons = [
    LayeredgeLogger()
]
