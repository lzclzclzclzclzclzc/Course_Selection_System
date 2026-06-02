# 学生选课与成绩管理系统

基于 Flask 的学生选课与成绩管理系统，支持 SQLite 和 OpenGauss 双数据库模式，可通过 Docker 快速部署。

## 一、系统要求

- Python 3.8+
- Docker & Docker Compose（可选，用于容器化部署）

## 二、快速启动（推荐：Docker 部署）

### 方式一：一键启动（OpenGauss 数据库）

```bash
# 1. 构建并启动所有服务
docker-compose up -d --build

# 2. 等待数据库启动（约 10 秒），然后初始化数据
docker exec course-selection-app python init_db.py
```

### 方式二：本地开发环境（SQLite 数据库）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 创建数据库表
flask --app run.py init-db

# 3. 初始化演示数据
flask --app run.py seed-demo

# 4. 启动服务
python run.py
```

## 三、默认账户

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 系统管理员 |
| 学生 | 20240001-20240020 | 123456 | 学生账号共 20 个 |
| 教师 | T0001-T0005 | 123456 | 教师账号共 5 个 |

## 四、访问方式

- 系统首页：http://localhost:5000
- 登录页面：http://localhost:5000/login

**局域网访问：**
- 查看本机 IP（例如 `192.168.1.20`）
- 其他设备访问：`http://192.168.1.20:5000`

## 五、常用管理命令

### Docker 部署命令

```bash
# 启动服务
docker-compose up -d

# 停止服务（保留数据）
docker-compose down

# 停止服务（清除数据）
docker-compose down -v

# 查看实时日志
docker logs course-selection-app -f

# 查看数据库日志
docker logs opengauss -f
```

### 本地开发命令

```bash
# 设置运行端口
$env:FLASK_RUN_PORT=8000; python run.py

# 开启调试模式
$env:FLASK_DEBUG=1; python run.py
```

## 六、数据库配置

### 使用 OpenGauss（Docker 默认）

配置文件：`config.py` → `OpenGaussConfig`

```python
DB_USER = os.getenv("DB_USER", "gaussdb")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Enmo@123")
DB_HOST = os.getenv("DB_HOST", "opengauss")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "student_course_db")
```

### 使用 SQLite（本地开发默认）

配置文件：`config.py` → `SQLiteConfig`

```python
SQLALCHEMY_DATABASE_URI = "sqlite:///instance/student_course.db"
```

## 七、项目结构

```
Course_Selection_System/
├── app/                      # 应用主目录
│   ├── __init__.py          # Flask 应用初始化
│   ├── models.py            # 数据模型
│   ├── routes/              # 路由定义
│   │   ├── auth.py          # 认证路由
│   │   ├── student.py       # 学生路由
│   │   ├── teacher.py       # 教师路由
│   │   └── admin.py         # 管理员路由
│   ├── templates/           # HTML 模板
│   ├── static/              # 静态资源
│   └── utils/               # 工具函数
├── config.py                # 配置文件
├── run.py                   # 启动脚本
├── init_db.py               # 数据库初始化脚本
├── docker-compose.yml       # Docker Compose 配置
├── Dockerfile               # Docker 镜像构建文件
├── requirements.txt         # Python 依赖
└── scripts/
    └── init_opengauss.sql   # OpenGauss 初始化脚本
```

## 八、常见问题

### 1. Docker 容器启动失败

**问题：** `connection to server at "opengauss" (xxx), port 5432 failed: Connection refused`

**解决方案：** 等待数据库完全启动后再初始化数据（约 10-20 秒）。

### 2. 登录后显示 Internal Server Error

**问题：** SQLAlchemy 实例未注册到 Flask app

**解决方案：** 确保项目使用统一的 `db` 实例，参考 `app/models.py` 和 `app/__init__.py`。

### 3. 数据库密码错误

**问题：** OpenGauss 密码不符合复杂度要求

**解决方案：** OpenGauss 要求密码包含大小写字母、数字和特殊字符，例如 `Enmo@123`。

## 九、技术栈

- **后端框架：** Flask 2.3+
- **ORM：** Flask-SQLAlchemy 3.1+
- **数据库：** SQLite / OpenGauss
- **容器化：** Docker & Docker Compose
- **前端框架：** Bootstrap 5
