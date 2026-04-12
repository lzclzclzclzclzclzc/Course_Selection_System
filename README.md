## 运行说明

1. 安装依赖  
`pip install -r requirements.txt`

2. 创建数据库表  
`flask --app run.py init-db`

3. 初始化演示数据  
`flask --app run.py seed-demo`

4. 启动服务（默认局域网可访问）  
`python run.py`

## 局域网多用户登录

- 服务默认监听 `0.0.0.0:5000`，同一局域网内其他设备可访问。  
- 在服务端机器查看本机 IP（例如 `192.168.1.20`）。  
- 其他设备浏览器访问：`http://192.168.1.20:5000`

如需修改端口/地址，可设置环境变量：

- `FLASK_RUN_HOST`（默认 `0.0.0.0`）
- `FLASK_RUN_PORT`（默认 `5000`）
- `FLASK_DEBUG`（`1` 或 `0`）

示例：

`$env:FLASK_RUN_PORT=8000; python run.py`

