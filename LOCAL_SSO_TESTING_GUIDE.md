# 本地SSO测试指南

由于客户的SSO服务器无法直接访问，我为你创建了一个完整的本地测试环境，可以在不依赖外部SSO服务的情况下验证SSO功能。

## 🎯 测试目标

- 验证SSO登录按钮是否正确显示
- 测试完整的OAuth 2.0授权流程
- 验证用户创建和登录功能
- 确认用户属性同步（email和company）

## 📁 文件结构

```
dify/
├── test-sso-server/                    # Mock SSO服务器
│   ├── mock_sso_server.py             # Flask服务器
│   ├── requirements.txt               # Python依赖
│   ├── run_mock_server.sh            # 启动脚本
│   ├── test_sso_endpoints.py         # 测试脚本
│   ├── Dockerfile.mock-sso           # Docker镜像
│   └── docker-compose.mock-sso.yml   # Docker Compose配置
├── .env.local.test                    # Dify测试配置
└── LOCAL_SSO_TESTING_GUIDE.md        # 本文档
```

## 🚀 快速开始

### 方法1：直接运行（推荐）

#### 1. 启动Mock SSO服务器

```bash
cd test-sso-server
./run_mock_server.sh
```

服务器将启动在 `http://localhost:8000`

#### 2. 配置Dify

复制测试配置：
```bash
cp .env.local.test .env
```

或者手动在 `.env` 文件中添加：

```bash
# 启用SSO
SSO_ENABLED=true

# Mock SSO服务器端点
SSO_AUTH_ENDPOINT=http://localhost:8000/oauth/authorize
SSO_TOKEN_ENDPOINT=http://localhost:8000/oauth/token
SSO_USERINFO_ENDPOINT=http://localhost:8000/oauth/userinfo

# Mock OAuth凭据
SSO_CLIENT_ID=test_client_id
SSO_CLIENT_SECRET=test_client_secret

# 本地回调地址
SSO_REDIRECT_URI=http://localhost:5001/console/api/oauth/authorize/sso

# OAuth范围（Mock服务器不需要）
SSO_SCOPES=

# 其他登录选项
ENABLE_EMAIL_PASSWORD_LOGIN=true
ENABLE_EMAIL_CODE_LOGIN=true
ALLOW_REGISTER=true
ALLOW_CREATE_WORKSPACE=true
```

#### 3. 启动Dify

```bash
# 运行数据库迁移
cd api
flask db upgrade

# 启动API服务器
cd api
python app.py

# 启动Web服务器（新终端）
cd web
npm install
npm run dev
```

#### 4. 测试SSO功能

1. 打开浏览器访问 `http://localhost:3000`
2. 在登录页面应该看到"Continue with SSO"按钮
3. 点击SSO按钮会跳转到Mock SSO服务器
4. 选择测试用户并登录

### 方法2：使用Docker（可选）

```bash
cd test-sso-server
docker-compose -f docker-compose.mock-sso.yml up --build
```

## 👥 测试用户

Mock SSO服务器提供两个测试用户：

| 用户 | 邮箱 | 姓名 | 公司 |
|------|------|------|------|
| 测试用户 | `test@company.com` | Test User | Test Company Ltd |
| 管理员用户 | `admin@company.com` | Admin User | Test Company Ltd |

## 🧪 验证测试

### 自动测试脚本

运行自动测试脚本验证所有端点：

```bash
cd test-sso-server
python test_sso_endpoints.py
```

测试脚本将验证：
- ✅ Mock SSO服务器健康状态
- ✅ 授权端点可访问性
- ✅ 完整OAuth 2.0流程
- ✅ Dify系统特性配置

### 手动测试步骤

#### 1. 验证Mock SSO服务器

访问 `http://localhost:8000`，应该看到：
```
Mock SSO Server
This is a test OAuth 2.0 server for Dify SSO integration testing.

Available Test Users:
• test@company.com - Test User (Test Company Ltd)
• admin@company.com - Admin User (Test Company Ltd)

OAuth Endpoints:
• Authorization: /oauth/authorize
• Token: /oauth/token
• UserInfo: /oauth/userinfo
```

#### 2. 验证Dify配置

调用Dify系统特性API：
```bash
curl http://localhost:5001/console/api/system-features
```

查找响应中的 `"enable_custom_sso": true`

#### 3. 测试完整SSO流程

1. **访问Dify登录页面**
   ```
   http://localhost:3000/signin
   ```

2. **检查SSO按钮**
   - 应该显示"Continue with SSO"按钮
   - 按钮使用锁图标

3. **点击SSO登录**
   - 跳转到Mock SSO服务器：`http://localhost:8000/oauth/authorize?...`
   - 显示用户选择表单

4. **选择测试用户**
   - 选择 `test@company.com` 或 `admin@company.com`
   - 点击"Login & Authorize"

5. **验证自动登录**
   - 自动跳转回Dify
   - 成功登录到Dify控制台

6. **检查用户信息**
   - 查看右上角用户信息
   - 验证邮箱和姓名正确显示

#### 4. 验证数据库记录

检查用户是否正确创建：

```sql
-- SQLite示例
sqlite3 db.sqlite
.mode column
.headers on
SELECT id, name, email, company, created_at FROM accounts WHERE email LIKE '%@company.com';
```

应该看到：
```
id    name      email               company           created_at
---   --------  ------------------  ----------------  -------------------
...   Test User test@company.com    Test Company Ltd  2025-01-16 12:00:00
```

## 🔍 故障排除

### 常见问题

#### 1. SSO按钮不显示

**检查清单：**
- [ ] `SSO_ENABLED=true`
- [ ] 所有必需的`SSO_*`环境变量都已设置
- [ ] Dify API服务器已重启
- [ ] 浏览器缓存已清除

**调试：**
```bash
# 检查系统特性API
curl http://localhost:5001/console/api/system-features | jq .enable_custom_sso

# 检查环境变量
grep SSO_ .env
```

#### 2. Mock SSO服务器无法访问

**检查清单：**
- [ ] Mock服务器在端口8000运行
- [ ] 防火墙没有阻止端口8000
- [ ] 依赖已正确安装

**调试：**
```bash
# 检查服务器状态
curl http://localhost:8000/health

# 检查端口占用
lsof -i :8000
```

#### 3. OAuth流程失败

**检查清单：**
- [ ] `SSO_REDIRECT_URI`与配置匹配
- [ ] Client ID和Secret正确
- [ ] Mock服务器日志无错误

**调试：**
```bash
# 查看Dify API日志
tail -f api/logs/server.log

# 查看Mock服务器日志（在Mock服务器终端）
```

#### 4. 用户创建失败

**检查清单：**
- [ ] 数据库迁移已运行
- [ ] 数据库连接正常
- [ ] `ALLOW_REGISTER=true`

**调试：**
```bash
# 检查数据库迁移
cd api
flask db current

# 测试数据库连接
python -c "from extensions.ext_database import db; print('DB connected')"
```

### 高级调试

#### 启用详细日志

在 `.env` 中添加：
```bash
LOG_LEVEL=DEBUG
FLASK_DEBUG=true
ENABLE_REQUEST_LOGGING=true
```

#### 使用cURL测试OAuth端点

```bash
# 1. 测试授权端点
curl -I "http://localhost:8000/oauth/authorize?client_id=test_client_id&response_type=code&redirect_uri=http://localhost:5001/console/api/oauth/authorize/sso"

# 2. 测试令牌端点（需要先获取授权码）
curl -X POST "http://localhost:8000/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=test_client_id&client_secret=test_client_secret&code=YOUR_CODE&grant_type=authorization_code&redirect_uri=http://localhost:5001/console/api/oauth/authorize/sso"

# 3. 测试用户信息端点（需要先获取访问令牌）
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://localhost:8000/oauth/userinfo"
```

## 📋 测试检查清单

完成以下检查清单确保测试环境正常：

### 环境准备
- [ ] Mock SSO服务器在 `http://localhost:8000` 运行
- [ ] Dify API在 `http://localhost:5001` 运行  
- [ ] Dify Web在 `http://localhost:3000` 运行
- [ ] 所有SSO环境变量已配置
- [ ] 数据库迁移已执行

### 功能测试
- [ ] 登录页面显示"Continue with SSO"按钮
- [ ] 点击SSO按钮跳转到Mock服务器
- [ ] Mock服务器显示用户选择表单
- [ ] 选择用户后成功跳转回Dify
- [ ] 用户自动登录到Dify控制台
- [ ] 用户信息正确显示（姓名、邮箱）
- [ ] 数据库中创建了正确的用户记录
- [ ] 公司信息正确同步

### 边缘情况测试
- [ ] 已存在用户的账户关联测试
- [ ] 无效授权码处理
- [ ] 过期令牌处理
- [ ] 网络连接失败处理

## 🎉 成功标志

如果看到以下结果，说明SSO集成测试成功：

1. **Mock SSO服务器**响应健康检查
2. **Dify登录页面**显示SSO按钮
3. **OAuth流程**完整执行无错误
4. **用户创建**在数据库中成功
5. **用户登录**到Dify控制台
6. **用户属性**正确同步

## 📞 下一步

测试成功后，你可以：

1. **适配生产环境**：将Mock服务器配置替换为真实SSO服务器
2. **自定义用户属性**：根据需要修改用户信息映射
3. **安全加固**：在生产环境中启用HTTPS和其他安全措施
4. **监控和日志**：配置生产环境的监控和日志记录

## 💡 提示

- Mock服务器模拟了标准的OAuth 2.0流程，与大多数真实SSO服务器兼容
- 测试数据是硬编码的，可以根据需要修改`MOCK_USERS`字典
- 服务器支持多个并发用户测试
- 所有OAuth令牌都有适当的过期时间

这个本地测试环境让你可以完全验证SSO功能，确保在连接真实SSO服务器时一切正常工作！