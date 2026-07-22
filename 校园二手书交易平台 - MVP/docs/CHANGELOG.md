# 开发日志（CHANGELOG）

## [V1.0.0] - 2024-07-22

### 项目初始化
- 创建项目骨架：`app.py` / `models.py` / `config.py` / `init_db.py`
- 基于《校园二手书交易平台 - MVP 设计草案》实现全部 MVP 功能

### 已实现功能

| 模块 | 功能 | 状态 |
|------|------|------|
| 用户系统 | 注册（学号 + 昵称 + 密码，bcrypt 哈希） | ✅ |
| 用户系统 | 登录 / 登出（Flask session） | ✅ |
| 首页 | 书籍卡片列表，按发布时间倒序 | ✅ |
| 首页 | 关键字模糊搜索 + 分页 | ✅ |
| 发布页 | 书名 / 售价 / 原价 / 描述 / 联系方式 / 图片上传 | ✅ |
| 详情页 | 完整信息展示 + 一键复制联系方式 | ✅ |
| 状态管理 | 发布者本人可上架/下架 | ✅ |
| API | RESTful 接口（register / login / books CRUD） | ✅ |

### 技术栈
- **后端**：Python Flask 3.1
- **数据库**：SQLite3（原生 `sqlite3` 模块，无 ORM 依赖）
- **密码**：bcrypt 5.0 加盐哈希
- **前端**：Jinja2 模板 + 原生 CSS（移动优先，响应式布局）
- **安全**：SECRET_KEY / 数据库路径 存放于 `.env`，已加入 `.gitignore`

### 文件结构

```
校园二手书交易平台 - MVP/
├── .env                    # 敏感配置（不入库）
├── .gitignore
├── requirements.txt        # Python 依赖
├── config.py               # 配置加载
├── models.py               # SQLite 数据模型
├── init_db.py              # 建表脚本
├── app.py                  # Flask 主应用（路由 + API）
├── utils/
│   └── helpers.py          # 登录装饰器、文件上传等工具函数
├── static/
│   ├── css/style.css       # 移动优先全局样式
│   └── uploads/            # 用户上传的书籍图片
├── templates/
│   ├── base.html           # 基础布局（导航栏 + flash 消息 + 底部）
│   ├── index.html          # 首页（搜索 + 书籍卡片 + 分页）
│   ├── login.html          # 登录
│   ├── register.html       # 注册
│   ├── publish.html        # 发布书籍
│   └── detail.html         # 书籍详情 + 复制联系方式
└── docs/
    └── CHANGELOG.md        # 本文件
```

### 待办（V2.0+）
- [ ] 忘记密码 / 重置密码
- [ ] 管理员后台
- [ ] 在线支付集成
- [ ] 站内即时通讯
- [ ] 智能推荐
- [ ] 用户头像
- [ ] 书籍收藏功能
- [ ] 评价/评论系统

---

## 启动方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
python app.py

# 3. 浏览器访问
# http://127.0.0.1:5000
```
