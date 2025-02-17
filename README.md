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
# 默认使用 8080 端口
mitmdump -s scripts/layeredge_mitm.py

# 如果 8080 端口被占用，使用其他端口（如 8082）
mitmdump -s scripts/layeredge_mitm.py --listen-port 8082

# 使用上游代理（比如本地的 Clash 代理）
mitmdump -s scripts/layeredge_mitm.py --mode upstream:http://127.0.0.1:7890 --listen-port 8082

# 查看占用端口的进程
sudo lsof -i :8080

# 关闭占用端口的进程
sudo kill <PID>
```

2. 配置浏览器代理：
   - 代理地址：127.0.0.1
   - 代理端口：8082（或你指定的其他端口）
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
4. 如果遇到端口冲突，可以使用 `--listen-port <port>` 指定其他端口
5. 如果需要访问外网，可以使用 `--mode upstream:` 指定上游代理

## 代理配置说明

1. mitmproxy 作为中间人代理：
   - 监听端口：8082（可通过 --listen-port 修改）
   - 浏览器连接到这个端口

2. 上游代理配置：
   - 如果使用 Clash：--mode upstream:http://127.0.0.1:7890
   - 如果使用其他代理，修改相应的地址和端口

3. 完整的代理链：
   浏览器 -> mitmproxy(8082) -> Clash(7890) -> 外网

## 下一步计划

1. 分析捕获的请求
2. 提取关键 API 端点
3. 实现纯 API 的注册流程
