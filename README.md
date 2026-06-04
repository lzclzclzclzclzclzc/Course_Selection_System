# 学生选课与成绩管理系统

基于 Flask 的学生选课与成绩管理系统，支持 SQLite 和 OpenGauss 双数据库模式，可通过 Docker 快速部署。

## 一、系统要求

- Python 3.8+
- Docker & Docker Compose（可选，用于容器化部署）

## 二、项目需求与功能要求完成情况

### 2.1 总体完成情况总览

| 序号 | 要求内容 | 完成状态 |
|------|---------|---------|
| 1 | 系统必须是在B/S结构下实现 | ✅ 已完成 |
| 2 | 数据库在原理1的School数据库基础下自行修改，只能添加，不能删除 | ⚠️ 部分完成（需验证） |
| 3 | 系统具有为不同的角色（系统管理员、教师、学生）提供不同操作权限的功能 | ✅ 已完成 |
| 4 | 系统为系统管理员提供具有学分制教务管理特色的各类功能 | ✅ 已完成 |
| 5 | 学生根据每个学期所开设的课程进行自主选课并具有查询有关信息的功能 | ✅ 已完成 |
| 6 | 教师根据学生所选课程进行成绩登录并且具有日常教学管理的功能 | ✅ 已完成 |
| 7 | 系统为不同的角色提供各类统计分析 | ✅ 已完成 |
| 8 | 数据库中至少包含一个触发器和一个存储过程在系统中使用和调用 | ✅ 已完成 |
| 9 | 其他辅助功能 | ✅ 已完成 |

---

### 2.2 详细功能要求逐条说明

#### ✅ 1. B/S结构
**完成情况：** 已完成

**说明：** 项目基于 Flask Web 框架，使用 Browser/Server 架构，通过浏览器访问。

---

#### ⚠️ 2. 数据库基于 School 数据库
**完成情况：** 需验证

**说明：** 当前数据库是独立设计的，包含以下表结构：
- `user` - 用户表
- `student` - 学生表
- `teacher` - 学生表
- `course` - 课程表
- `course_selection` - 选课表

**待验证：** 需要确认是否基于 School 数据库进行扩展。

---

#### ✅ 3. 角色权限管理
**完成情况：** 已完成

**实现：**
- 三个角色：admin（管理员）、teacher（教师）、student（学生）
- 使用 `@role_required` 装饰器进行权限控制
- 每个角色有独立的路由前缀和功能模块

---

#### ✅ 4. 系统管理员功能
**完成情况：** 已完成

**实现：**
- 用户管理（创建、删除、重置密码）
- 课程管理（创建、删除，支持按学期开设）
- 学期管理（创建、激活、删除；同一时间唯一活动学期）
- 数据备份（一键导出 JSON）
- 教务统计报表（学生选课、教师授课、成绩分布、学分完成）

---

#### ✅ 5. 学生功能
**完成情况：** 已完成

**实现：**
- 课程浏览
- 自主选课（人数限制检查）
- 退课功能
- 成绩查询
- 成绩单导出（Excel、PDF）

---

#### ✅ 6. 教师功能
**完成情况：** 已完成

**实现：**
- 查看所授课程
- 查看选课学生
- 成绩录入和修改
- 成绩统计分析

---

#### ✅ 7. 统计分析功能
**完成情况：** 已完成

**实现：**
- 教师端：课程成绩分段统计、平均分、最高分、最低分
- 学生端：个人成绩统计
- 管理员端整体教务统计：
  - 学生选课情况统计（每门课的人数、容量、平均分，按学期归类）
  - 教师授课情况统计（每位教师所授课程数与学生总数）
  - 成绩分布统计（每门课 0-59 / 60-69 / 70-79 / 80-89 / 90-100 五段分布）
  - 学分完成情况统计（每个学生已获学分与平均分）

---

#### ✅ 8. 触发器和存储过程
**完成情况：** 已完成

**实现：**
- 触发器 `trg_sync_course_current_students`：在 `course_selection` 表上 AFTER INSERT/UPDATE/DELETE 自动维护 `course.current_students`，确保选课人数实时准确。
- 存储过程 `calculate_student_average_grade(p_student_id, OUT p_avg_grade, OUT p_total_credit)`：计算指定学生的学分加权平均成绩与已修学分总数。
- 在 OpenGauss 模式下由 `app/utils/db_objects.py` 的 `ensure_academic_schema()` 在应用启动时自动注册。

---

#### ✅ 9. 其他辅助功能
**完成情况：** 已完成

**实现：**
- 用户登录/登出
- 数据备份功能
- 成绩单导出（Excel、PDF）
- 密码加密存储

---

### 2.3 待完成功能优先级

#### 高优先级（必须完成） — ✅ 全部完成

1. ✅ **触发器和存储过程**
   - 触发器：选课人数自动统计（`trg_sync_course_current_students`）
   - 存储过程：计算学生平均绩点（`calculate_student_average_grade`）

2. ✅ **管理员统计功能**
   - 学生选课统计、教师授课统计、成绩分布统计、学分完成统计
   - 全部呈现在管理员控制台

3. ✅ **学期和课程开设管理**
   - 学期管理：创建 / 激活 / 删除
   - 课程按学期开设（创建课程时绑定 `semester_id`）

#### 中优先级（建议完成）

1. **完善统计分析**
   - 图表化展示
   - 多维度数据对比

2. **优化教师日常管理**
   - 课程大纲管理
   - 教学进度记录

---

## 三、快速启动（推荐：Docker 部署）

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

## 四、默认账户

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 系统管理员 |
| 学生 | 20240001-20240020 | 123456 | 学生账号共 20 个 |
| 教师 | T0001-T0005 | 123456 | 教师账号共 5 个 |

## 五、访问方式

- 系统首页：http://localhost:5000
- 登录页面：http://localhost:5000/login

**局域网访问：**
- 查看本机 IP（例如为 `192.168.1.20`）
- 其他设备访问：`http://192.168.1.20:5000`

## 六、常用管理命令

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

## 七、数据库配置

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

## 八、项目结构

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

## 九、常见问题

### 1. Docker 容器启动失败

**问题：** `connection to server at "opengauss" (xxx), port 5432 failed: Connection refused`

**解决方案：** 等待数据库完全启动后再初始化数据（约 10-20 秒）。

### 2. 登录后显示 Internal Server Error

**问题：** SQLAlchemy 实例未注册到 Flask app

**解决方案：** 确保项目使用统一的 `db` 实例，参考 `app/models.py` 和 `app/__init__.py`。

### 3. 数据库密码错误

**问题：** OpenGauss 密码不符合复杂度要求

**解决方案：** OpenGauss 要求密码包含大小写字母、数字和特殊字符，例如 `Enmo@123`。

## 十、技术栈

- **后端框架：** Flask 2.3+
- **ORM：** Flask-SQLAlchemy 3.1+
- **数据库：** SQLite / OpenGauss
- **容器化：** Docker & Docker Compose
- **前端框架：** Bootstrap 5
