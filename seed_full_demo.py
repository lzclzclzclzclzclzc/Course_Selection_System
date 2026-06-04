"""扩展演示数据：3 学期、4 院系、12 教师、80 学生、30 门课。"""
import random
from datetime import date, datetime, timedelta

from run import app
from app import db
from app.models import (
    Course,
    CourseSelection,
    LessonProgress,
    Semester,
    Student,
    Teacher,
    User,
)

random.seed(42)  # 保证每次跑生成的数据一致

# ---- 院系 ----
DEPARTMENTS = ["计算机系", "软件工程系", "信息安全系", "数学系"]

# ---- 教师姓名池 ----
TEACHER_NAMES = [
    ["王建国", "李文静", "张振华"],   # 计算机系
    ["陈雅婷", "刘国梁", "赵芳"],     # 软件工程系
    ["孙明远", "周丽娜", "吴启明"],   # 信息安全系
    ["郑思成", "黄丽华", "徐志远"],   # 数学系
]

# ---- 学生姓的常用字 ----
SURNAMES = "王李张刘陈杨赵黄周吴徐孙马朱胡郭何高林罗郑梁谢宋唐许韩冯邓曹彭曾肖田董袁潘于蒋蔡余杜叶程苏魏吕丁任沈姚卢姜崔钟谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严赖覃洪武莫孔"
GIVEN_NAMES_M = "伟刚强磊军洋勇毅俊峰超平辉健明亮永杰锋刚波宁明波鸿宇睿哲昊然博文俊豪轩然子轩泽宇浩然鹏程振华建国国强国华文博"
GIVEN_NAMES_F = "芳娜静秀艳娟敏静丽强艳英华慧巧美娜静雪婷雯丹晴雪丽娜茜怡馨思琪雅文雨彤梦琪静怡欣怡梓涵雨欣晓彤婉清"


def random_chinese_name(gender):
    surname = random.choice(SURNAMES)
    pool = GIVEN_NAMES_M if gender == "男" else GIVEN_NAMES_F
    if random.random() < 0.5:
        given = random.choice(pool) + random.choice(pool)
    else:
        given = random.choice(pool)
    return surname + given


# ---- 学期 ----
SEMESTERS_SPEC = [
    ("2024-2025 Autumn", date(2024, 9, 1), date(2025, 1, 18), False),  # 历史
    ("2024-2025 Spring", date(2025, 2, 24), date(2025, 7, 5), False),  # 历史
    ("2025-2026 Spring", date(2026, 2, 24), date(2026, 7, 5), True),   # 当前
]

# ---- 课程模板：30 门，按系归类 ----
COURSES_BY_DEPT = {
    "计算机系": [
        ("CS101", "程序设计基础", 3.0, "required"),
        ("CS102", "数据结构", 3.5, "required"),
        ("CS201", "数据库原理", 3.5, "required"),
        ("CS202", "操作系统", 4.0, "required"),
        ("CS301", "计算机网络", 3.0, "required"),
        ("CS302", "编译原理", 4.0, "elective"),
        ("CS303", "人工智能导论", 2.5, "elective"),
        ("CS304", "机器学习", 3.0, "elective"),
    ],
    "软件工程系": [
        ("SE101", "软件工程概论", 3.0, "required"),
        ("SE201", "软件需求分析", 2.5, "required"),
        ("SE202", "软件设计模式", 3.0, "required"),
        ("SE301", "敏捷开发实践", 2.0, "elective"),
        ("SE302", "软件测试", 2.5, "elective"),
        ("SE303", "DevOps 实战", 2.0, "elective"),
        ("SE401", "项目管理", 2.0, "general"),
    ],
    "信息安全系": [
        ("IS101", "信息安全导论", 3.0, "required"),
        ("IS201", "密码学基础", 3.5, "required"),
        ("IS202", "网络安全", 3.0, "required"),
        ("IS301", "Web 安全", 2.5, "elective"),
        ("IS302", "移动端安全", 2.5, "elective"),
        ("IS303", "渗透测试", 3.0, "elective"),
        ("IS401", "安全合规", 2.0, "general"),
    ],
    "数学系": [
        ("MA101", "高等数学 A", 5.0, "required"),
        ("MA102", "线性代数", 3.5, "required"),
        ("MA201", "概率论与数理统计", 4.0, "required"),
        ("MA202", "离散数学", 3.5, "required"),
        ("MA301", "数值分析", 3.0, "elective"),
        ("MA302", "运筹学", 3.0, "elective"),
        ("MA303", "数学建模", 2.5, "elective"),
        ("MA401", "数学史", 1.5, "general"),
    ],
}

# ---- 大纲模板（每门课 3-5 句）----
SYLLABUS_TEMPLATES = {
    "程序设计基础": "1. 编程语言基本概念与历史\n2. 变量、数据类型与表达式\n3. 控制结构：分支与循环\n4. 函数定义与参数传递\n5. 数组与字符串处理",
    "数据结构": "1. 线性表：数组、链表\n2. 栈与队列\n3. 树：二叉树、平衡树、堆\n4. 图论基础与图算法\n5. 哈希表与高级数据结构",
    "数据库原理": "1. 关系模型与关系代数\n2. SQL 语言基础与高级查询\n3. 事务、并发控制与恢复\n4. 数据库设计与规范化\n5. 索引、查询优化与分布式数据库简介",
    "操作系统": "1. 操作系统结构与进程管理\n2. CPU 调度与同步\n3. 内存管理：分页、分段、虚拟内存\n4. 文件系统与 I/O 子系统\n5. 操作系统安全与保护机制",
    "计算机网络": "1. 网络体系结构与参考模型\n2. 物理层与链路层协议\n3. 网络层：IP、路由\n4. 传输层：TCP、UDP\n5. 应用层协议与网络安全基础",
    "编译原理": "1. 词法分析\n2. 语法分析与语法树\n3. 语义分析与中间代码\n4. 代码优化\n5. 目标代码生成",
    "人工智能导论": "1. AI 的历史与流派\n2. 搜索算法：BFS、DFS、A*\n3. 知识表示与推理\n4. 机器学习基础\n5. 自然语言处理与计算机视觉概览",
    "机器学习": "1. 监督学习：回归与分类\n2. 决策树与随机森林\n3. 支持向量机\n4. 神经网络与深度学习入门\n5. 模型评估与调优",
    "软件工程概论": "1. 软件工程基本概念\n2. 软件生命周期与开发模型\n3. 需求工程导论\n4. 软件设计与架构\n5. 软件质量与项目管理",
    "软件需求分析": "1. 需求获取与利益相关者\n2. 需求分类与规格说明\n3. 用例建模\n4. 需求验证与变更管理\n5. 需求文档编写实践",
    "软件设计模式": "1. 设计模式概述与原则\n2. 创建型模式\n3. 结构型模式\n4. 行为型模式\n5. 模式应用与重构",
    "敏捷开发实践": "1. 敏捷宣言与原则\n2. Scrum 框架\n3. 用户故事与迭代规划\n4. 持续集成与持续交付\n5. 团队协作与回顾",
    "软件测试": "1. 测试基础与分类\n2. 单元测试与 TDD\n3. 集成测试与系统测试\n4. 自动化测试框架\n5. 性能测试与安全测试",
    "DevOps 实战": "1. DevOps 文化与原则\n2. 容器化与 Docker\n3. CI/CD 流水线\n4. 基础设施即代码\n5. 监控与日志",
    "项目管理": "1. 项目管理框架与 PMBOK\n2. 项目计划与范围管理\n3. 进度与成本控制\n4. 风险管理\n5. 质量与沟通管理",
    "信息安全导论": "1. 信息安全的目标与威胁\n2. 安全模型与策略\n3. 访问控制\n4. 审计与监控\n5. 法律法规与伦理",
    "密码学基础": "1. 古典密码与对称加密\n2. AES 与分组密码模式\n3. 公钥密码：RSA、ECC\n4. 散列函数与数字签名\n5. 密钥管理与协议",
    "网络安全": "1. 网络威胁与攻击模型\n2. 防火墙与入侵检测\n3. VPN 与加密通信\n4. DDoS 防护\n5. 零信任架构",
    "Web 安全": "1. HTTP 协议与 Cookie/Session\n2. XSS 与 CSRF\n3. SQL 注入与文件上传\n4. 身份认证与授权\n5. 安全开发生命周期",
    "移动端安全": "1. 移动 OS 安全模型\n2. 应用沙箱与权限\n3. 移动应用逆向\n4. 通信安全\n5. 移动端漏洞与修复",
    "渗透测试": "1. 渗透测试方法论\n2. 信息收集与扫描\n3. 漏洞利用\n4. 后渗透阶段\n5. 报告撰写",
    "安全合规": "1. 等保 2.0 与 ISO 27001\n2. GDPR 与个人信息保护法\n3. 数据分类与分级\n4. 风险评估流程\n5. 合规审计",
    "高等数学 A": "1. 极限与连续\n2. 导数与微分\n3. 微分中值定理与导数应用\n4. 不定积分与定积分\n5. 多元函数微分学与重积分",
    "线性代数": "1. 行列式\n2. 矩阵与矩阵运算\n3. 向量空间与线性变换\n4. 特征值与特征向量\n5. 二次型与正交化",
    "概率论与数理统计": "1. 随机事件与概率\n2. 随机变量及其分布\n3. 多维随机变量\n4. 大数定律与中心极限定理\n5. 参数估计与假设检验",
    "离散数学": "1. 命题逻辑与谓词逻辑\n2. 集合、关系、函数\n3. 图论基础\n4. 代数结构\n5. 组合数学",
    "数值分析": "1. 误差分析\n2. 插值与逼近\n3. 数值微分与积分\n4. 线性方程组数值解\n5. 常微分方程数值解",
    "运筹学": "1. 线性规划与单纯形法\n2. 对偶理论与灵敏度分析\n3. 整数规划\n4. 网络流模型\n5. 排队论与决策分析",
    "数学建模": "1. 建模方法论\n2. 常用模型类型\n3. 模型求解工具\n4. 模型验证\n5. 案例研究",
    "数学史": "1. 古代数学发展\n2. 近代数学的兴起\n3. 微积分的诞生\n4. 现代数学流派\n5. 中国数学家与贡献",
}

# ---- 教学进度模板（按周展开主题）----
LESSON_TOPICS = {
    "程序设计基础": ["编程语言概述", "变量与基本类型", "运算符与表达式", "条件语句", "循环结构", "函数与递归", "数组", "字符串", "结构体", "指针入门", "文件 I/O", "综合编程实战"],
    "数据结构": ["导论与算法分析", "线性表与数组", "链表", "栈与队列", "字符串与 KMP", "二叉树", "堆与优先队列", "图的存储与遍历", "最短路径算法", "最小生成树", "排序算法", "查找与哈希"],
    "数据库原理": ["关系模型", "SQL DDL", "SQL DML 进阶", "视图与索引", "事务与并发", "锁与隔离级别", "范式理论", "ER 模型", "查询优化", "存储与索引", "分布式数据库", "课程项目"],
    "操作系统": ["导论与体系结构", "进程概念", "线程与同步", "CPU 调度", "死锁", "内存管理基础", "虚拟内存", "文件系统", "I/O 子系统", "存储管理", "保护与安全", "实例研究 Linux"],
    "计算机网络": ["概述与参考模型", "物理层", "数据链路层", "MAC 与以太网", "IP 协议", "路由协议", "TCP", "UDP 与拥塞控制", "DNS 与 HTTP", "邮件与文件传输", "网络安全", "新兴网络技术"],
    "人工智能导论": ["AI 概述", "搜索算法", "对抗搜索", "约束满足", "知识表示", "贝叶斯网络", "机器学习入门", "决策树", "神经网络", "强化学习", "NLP 基础", "CV 基础"],
    "机器学习": ["导论", "线性回归", "逻辑回归", "决策树", "集成学习", "SVM", "聚类", "PCA 与降维", "神经网络", "卷积网络", "模型评估", "实战项目"],
    "软件工程概论": ["软件危机", "生命周期", "瀑布与敏捷", "需求分析", "系统设计", "详细设计", "编码规范", "软件测试", "维护与演化", "项目管理", "质量保证", "案例研究"],
    "密码学基础": ["导论与历史", "古典密码", "信息论基础", "DES 与 AES", "分组密码模式", "RSA", "椭圆曲线", "散列函数", "数字签名", "密钥交换", "PKI", "应用案例"],
    "高等数学 A": ["极限定义", "极限计算", "连续性", "导数定义", "求导法则", "中值定理", "极值与最值", "不定积分", "定积分", "多元微分", "二重积分", "三重积分"],
    "线性代数": ["行列式定义", "行列式性质与计算", "矩阵运算", "矩阵求逆", "线性方程组", "向量空间", "线性相关性", "基与维数", "特征值", "对角化", "二次型", "正交矩阵"],
}


def clear_all():
    print("[清空] 删除现有数据...")
    LessonProgress.query.delete()
    CourseSelection.query.delete()
    Course.query.delete()
    Teacher.query.delete()
    Student.query.delete()
    User.query.delete()
    Semester.query.delete()
    db.session.commit()


def seed_semesters():
    semesters = {}
    for name, start, end, active in SEMESTERS_SPEC:
        s = Semester(name=name, start_date=start, end_date=end, is_active=active)
        db.session.add(s)
        semesters[name] = s
    db.session.flush()
    print(f"[学期] {len(semesters)} 个")
    return semesters


def seed_admin():
    admin = User(username="admin", role="admin")
    admin.set_password("admin123")
    db.session.add(admin)


def seed_teachers():
    teachers = []
    teacher_no = 1
    for dept_idx, dept in enumerate(DEPARTMENTS):
        for name in TEACHER_NAMES[dept_idx]:
            u = User(username=f"T{teacher_no:04d}", role="teacher")
            u.set_password("123456")
            db.session.add(u)
            db.session.flush()
            t = Teacher(user_id=u.id, teacher_no=u.username, name=name, department=dept)
            db.session.add(t)
            teachers.append(t)
            teacher_no += 1
    db.session.flush()
    print(f"[教师] {len(teachers)} 人，分布于 {len(DEPARTMENTS)} 系")
    return teachers


def seed_students():
    """80 学生：每系 20 人，按入学年份分散（让历史学期有较多年级）。
    学号编号：cohort=2023 从 20230001 起递增，cohort=2024 从 20240001，cohort=2025 从 20250001。"""
    students = []
    counters = {2023: 0, 2024: 0, 2025: 0}
    for dept in DEPARTMENTS:
        for j in range(1, 21):
            # 学生年级：1/4 大三（2023 入学）、1/4 大二（2024）、1/2 大一（2025）
            r = random.random()
            if r < 0.25:
                cohort = 2023
            elif r < 0.50:
                cohort = 2024
            else:
                cohort = 2025
            counters[cohort] += 1
            student_no = f"{cohort}{counters[cohort]:04d}"
            gender = random.choice(["男", "女"])
            name = random_chinese_name(gender)
            u = User(username=student_no, role="student")
            u.set_password("123456")
            db.session.add(u)
            db.session.flush()
            s = Student(
                user_id=u.id,
                student_no=student_no,
                name=name,
                age=random.randint(18, 23),
                gender=gender,
                department=dept,
            )
            s._cohort = cohort  # 临时挂个属性方便后面选课逻辑用
            db.session.add(s)
            students.append(s)
    db.session.flush()
    print(f"[学生] {len(students)} 人，分布于 {len(DEPARTMENTS)} 系")
    return students


def seed_courses(semesters, teachers):
    """30 门课：每个系的课程在 3 个学期中开设；状态/类型多样。"""
    teachers_by_dept = {dept: [] for dept in DEPARTMENTS}
    for t in teachers:
        teachers_by_dept[t.department].append(t)

    semester_list = list(semesters.values())  # [autumn_2024, spring_2025, spring_2026_active]
    courses = []

    for dept, course_specs in COURSES_BY_DEPT.items():
        dept_teachers = teachers_by_dept[dept]
        for course_no, course_name, credit, course_type in course_specs:
            # 必修课每个学期都开；选修/通识只开 1-2 个学期
            if course_type == "required":
                offer_in = semester_list  # 全开
            else:
                # 选 1 或 2 个学期
                offer_in = random.sample(semester_list, k=random.choice([1, 2]))

            for sem_idx, sem in enumerate(offer_in):
                # 不同学期开同一门课时，加 .v2 后缀避开 unique 约束
                if len([c for c in courses if c.course_no.startswith(course_no)]) == 0:
                    actual_no = course_no
                else:
                    actual_no = f"{course_no}-{sem.name.split()[1][:1]}{sem.start_date.year % 100}"

                # 状态：当前学期 open，过去学期 closed
                if sem.is_active:
                    status = random.choices(["open", "planned"], weights=[9, 1])[0]
                else:
                    status = "closed"

                # 容量：必修宽，选修严
                if course_type == "required":
                    max_students = random.randint(60, 100)
                else:
                    max_students = random.randint(20, 50)

                c = Course(
                    course_no=actual_no,
                    course_name=course_name,
                    credit=credit,
                    department=dept,
                    teacher_id=random.choice(dept_teachers).id,
                    semester_id=sem.id,
                    course_type=course_type,
                    max_students=max_students,
                    status=status,
                    syllabus=SYLLABUS_TEMPLATES.get(course_name, ""),
                )
                db.session.add(c)
                courses.append(c)
    db.session.flush()
    print(f"[课程] {len(courses)} 门（覆盖 {len(semesters)} 学期）")
    return courses


def seed_selections(students, courses, semesters):
    """选课：依学生年级、学期决定选课规模与是否有成绩。"""
    selections = []
    sem_list = sorted(semesters.values(), key=lambda s: s.start_date)
    autumn_2024, spring_2025, spring_2026 = sem_list

    for student in students:
        cohort = getattr(student, "_cohort", 2025)
        # 哪些学期能选？基于入学年份
        eligible_sems = []
        if cohort <= 2023:
            eligible_sems = [autumn_2024, spring_2025, spring_2026]
        elif cohort <= 2024:
            eligible_sems = [autumn_2024, spring_2025, spring_2026]
        else:  # 2025
            eligible_sems = [spring_2026]  # 大一只在当前学期

        for sem in eligible_sems:
            # 每学期 3-6 门课
            sem_courses = [c for c in courses if c.semester_id == sem.id and c.status != "planned"]
            # 优先本系课程
            own_dept = [c for c in sem_courses if c.department == student.department]
            other_dept = [c for c in sem_courses if c.department != student.department]
            n_courses = random.randint(3, min(6, len(sem_courses)))
            n_own = min(len(own_dept), random.randint(2, 4))
            picks = random.sample(own_dept, k=min(n_own, len(own_dept)))
            n_other = n_courses - len(picks)
            if n_other > 0 and other_dept:
                picks += random.sample(other_dept, k=min(n_other, len(other_dept)))

            for course in picks:
                # 容量上限保护
                count = sum(1 for s in selections if s.course_id == course.id)
                if count >= course.max_students:
                    continue

                # 成绩：历史学期一定有；当前学期 50% 有成绩
                if sem.is_active:
                    has_grade = random.random() < 0.5
                else:
                    has_grade = True

                if has_grade:
                    # 成绩分布：偏正态向 78 集中
                    g = random.gauss(78, 12)
                    g = max(40, min(99, g))
                    grade = round(g, 2)
                else:
                    grade = None

                selected_at = sem.start_date + timedelta(days=random.randint(0, 21))
                sel = CourseSelection(
                    student_id=student.id,
                    course_id=course.id,
                    grade=grade,
                    selected_at=datetime.combine(selected_at, datetime.min.time()),
                )
                db.session.add(sel)
                selections.append(sel)

    db.session.flush()
    print(f"[选课] {len(selections)} 条；其中已录成绩 {sum(1 for s in selections if s.grade is not None)} 条")


def seed_lessons(courses):
    """给主要课程添加教学进度记录。"""
    n = 0
    for course in courses:
        topics = LESSON_TOPICS.get(course.course_name)
        if not topics:
            continue
        # 进度只给当前/历史学期；planned 课跳过
        if course.status == "planned":
            continue
        # 每门课记录 8-12 周
        weeks = random.randint(8, min(len(topics), 12))
        for w in range(1, weeks + 1):
            db.session.add(LessonProgress(
                course_id=course.id,
                week=w,
                topic=topics[w - 1],
                note=random.choice([
                    "课堂讨论 + 课后习题",
                    "实验室实践",
                    "案例分析",
                    "小组项目演示",
                    "随堂测验",
                    "",
                ]),
            ))
            n += 1
    db.session.flush()
    print(f"[教学进度] {n} 条记录")


def main():
    with app.app_context():
        clear_all()
        semesters = seed_semesters()
        seed_admin()
        teachers = seed_teachers()
        students = seed_students()
        courses = seed_courses(semesters, teachers)
        seed_selections(students, courses, semesters)
        db.session.commit()  # 提交后让触发器把 current_students 同步好
        seed_lessons(courses)
        db.session.commit()

        # 摘要
        print()
        print("=" * 50)
        print(f"[完成] users={User.query.count()}  students={Student.query.count()}  teachers={Teacher.query.count()}")
        print(f"       semesters={Semester.query.count()}  courses={Course.query.count()}")
        sel_total = CourseSelection.query.count()
        sel_graded = CourseSelection.query.filter(CourseSelection.grade.isnot(None)).count()
        print(f"       selections={sel_total}  graded={sel_graded}")
        print(f"       lessons={LessonProgress.query.count()}")
        print()
        print("默认账户：")
        print("  admin / admin123")
        print("  学生学号 (20230001-20250080) / 123456")
        print("  教师工号 T0001-T0012 / 123456")


if __name__ == "__main__":
    main()
