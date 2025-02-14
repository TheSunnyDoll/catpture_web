# Layeredge API 分析工具

这个项目用于分析 Layeredge 的 API 请求，使用 mitmproxy 进行请求捕获和分析。

## 项目结构

```
mitm/
├── logs/          # 存放捕获的请求日志
├── scripts/       # mitmproxy 脚本
└── analysis/      # 分析工具和结果
```

## 使用方法

1. 启动 mitmproxy 并加载脚本：

```bash
mitmdump -s scripts/layeredge_mitm.py
```

2. 配置浏览器代理：
   - 代理地址：127.0.0.1
   - 代理端口：8080
   - 安装 mitmproxy 证书（访问 mitm.it）

3. 完成注册流程：
   - 打开 Layeredge 网站
   - 完成完整的注册流程
   - 所有请求将被自动记录到 logs 目录

4. 分析日志：
   - 日志文件格式为 JSON
   - 包含完整的请求和响应信息
   - 按时间戳排序

## 注意事项

1. 确保系统信任了 mitmproxy 的 CA 证书
2. 所有敏感信息（如密码、私钥）都会被记录，请注意安全
3. 建议使用测试账号进行捕获

## 下一步计划

1. 分析捕获的请求
2. 提取关键 API 端点
3. 实现纯 API 的注册流程
