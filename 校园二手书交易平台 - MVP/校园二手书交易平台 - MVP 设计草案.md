# 校园二手书交易平台 - MVP 设计草案

## 一、MVP 核心目标
解决校内二手书信息分散、难查找的问题。学生可**发布**闲置书籍，并**搜索/浏览**他人发布的书籍，通过预留联系方式线下交易。**不做支付、物流、站内聊天。**

## 二、功能范围
1. **首页/列表页**：顶部搜索框（按书名模糊搜索)
2. **发布页**：表单（书名、售价、原价（选填）、新旧程度描述、联系方式（手机/微信）、上传图片（选填））。

## 三、数据表设计（SQLite）
**用户表 (users)**
- id, student_id (学号/账号), password_hash (存储哈希), nickname, created_at

**书籍表 (books)**
- id, user_id (关联用户), title, price, original_price(选填), description(书况), contact(联系方式), image_url(选填), status(1在售/0已下架), created_at

## 四、后端接口（API）
- `POST /api/register`：注册（密码需哈希处理）
- `POST /api/login`：登录（返回session或简单token）
- `POST /api/books`：发布书籍（需登录）
- `GET /api/books?keyword=`：搜索书籍列表
- `GET /api/books/:id`：获取书籍详情

## 五、安全规范（必须执行）
1. **密码**：后端使用 `bcrypt` 加盐哈希存储，**绝不存明文**。
2. **密钥管理**：所有密钥（SECRET_KEY、数据库连接）存入 `.env` 文件，并在 `.gitignore` 中排除该文件。
3. **Git提交**：严禁将 `.env` 或含敏感信息的代码提交至GitHub。若已误提交，需立即清理历史记录或重置仓库。

## 六、技术栈（选最快上手的）
- 后端：Python Flask / Node.js Express
- 数据库：SQLite3（无需额外安装）
- 前端：HTML + CSS + 原生JS（或Vue CDN），优先保证移动端适配。

