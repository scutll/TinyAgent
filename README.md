# TinyAgent : a small agent to help you do something

Api 启动方式:

- 部署模型和api:

```bash
python -m uvicorn llmApi.API.api_genResponse:app --host 0.0.0.0 --port 5200
```

- 因为autodl禁止了外部设备访问容器ip，因此要使用cloudflared来转发到其他地址:
  - 重新开一个终端：

```bash
cloudflared tunnel --url http://localhost:5200
```

- 可以找到一个地址: 

```bash
2025-10-14T06:56:47Z INF |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
2025-10-14T06:56:47Z INF |  https://few-nikon-minister-prospects.trycloudflare.com 
```

然后在apifox上将这个作为根地址就行了(注意：需要用raw data的json格式发送请求)

