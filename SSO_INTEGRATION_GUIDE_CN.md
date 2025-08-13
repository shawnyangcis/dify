# Dify 自定义 SSO 集成指南

本指南介绍如何配置和使用已添加到 Dify 的自定义单点登录（SSO）功能。

## 概述

自定义 SSO 集成允许 Dify 通过任何兼容 OAuth 2.0 的 SSO 提供商进行用户身份验证。该实现支持：

- OAuth 2.0 授权码流程
- 自动用户创建和登录
- 用户属性同步（邮箱和公司）
- 针对不同环境的灵活配置

## 配置

### 1. 环境变量

在您的 `.env` 文件中添加以下配置或设置为环境变量：

```bash
# 启用自定义 SSO 功能
SSO_ENABLED=true

# SSO OAuth 端点
SSO_AUTH_ENDPOINT=http://wm.stg.paic.com.cn/gw/oauth/v2/authorize
SSO_TOKEN_ENDPOINT=http://wm.stg.paic.com.cn/gw/oauth/v2/token
SSO_USERINFO_ENDPOINT=http://wm.stg.paic.com.cn/gw/oauth/v2/userInfo

# SSO OAuth 凭据
SSO_CLIENT_ID=Ov23lirUopDC7TuZ3eeD
SSO_CLIENT_SECRET=479eac814f270a0fad2fe682a8cdbef6bc936b7f

# SSO OAuth 重定向 URI（必须匹配您的 Dify 实例 URL）
SSO_REDIRECT_URI=http://gaadp.fat001.qa.pab.com/console/api/oauth/authorize/sso

# OAuth 作用域（空格分隔，可以为空）
SSO_SCOPES=
```

### 2. 数据库迁移

该实现在 accounts 表中添加了 `company` 字段。运行数据库迁移：

```bash
cd api
flask db upgrade
```

### 3. 配置说明

- **SSO_ENABLED**：必须为 `true` 才能在登录页面启用 SSO 按钮
- **SSO_REDIRECT_URI**：必须在您的 SSO 提供商中注册并指向您的 Dify 实例
- **所有必需字段**：必须提供所有 SSO 配置字段才能显示 SSO 选项
- **SSO_SCOPES**：如果您的 SSO 提供商不需要特定作用域，可以留空

## 工作原理

### 身份验证流程

1. **用户发起**：用户点击登录页面上的"使用 SSO 继续"按钮
2. **授权请求**：Dify 将用户重定向到 SSO 提供商的授权端点
3. **用户认证**：用户通过 SSO 提供商进行身份验证
4. **授权许可**：SSO 提供商使用授权码重定向回 Dify
5. **令牌交换**：Dify 使用授权码交换访问令牌
6. **用户信息**：Dify 使用访问令牌检索用户信息
7. **账户管理**：Dify 创建新账户或更新现有账户
8. **登录**：用户自动登录到 Dify

### 用户数据映射

SSO 集成按如下方式映射用户属性：

| SSO 属性 | Dify 字段 | 说明 |
|----------|-----------|------|
| `sub`, `id`, `user_id` | 账户 ID | 用于链接账户 |
| `name`, `username`, `display_name` | 用户名 | 在 Dify 中的显示名称 |
| `email` | 邮箱地址 | 主要标识符 |
| `company`, `organization` | 公司 | 组织信息的新字段 |

### 账户关联

- **新用户**：使用 SSO 信息自动创建新的 Dify 账户
- **现有用户**：将 SSO 身份链接到现有账户（通过邮箱匹配）
- **公司同步**：每次登录时更新公司信息

## 测试集成

### 1. 验证配置

通过调用系统功能 API 检查您的配置是否正确：

```bash
curl -X GET "http://your-dify-instance/console/api/system-features"
```

在响应中查找 `enable_custom_sso: true`。

### 2. 测试 SSO 流程

1. **访问登录页面**：导航到您的 Dify 实例登录页面
2. **验证 SSO 按钮**：确认出现"使用 SSO 继续"按钮
3. **点击 SSO 按钮**：应该重定向到您的 SSO 提供商
4. **身份验证**：使用您的 SSO 提供商完成身份验证
5. **验证重定向**：应该返回 Dify 并自动登录

### 3. 验证用户创建

检查数据库以确认用户已正确创建：

```sql
SELECT id, name, email, company, created_at 
FROM accounts 
WHERE email = 'your-sso-email@company.com';
```

### 4. 测试账户关联

1. 使用与您的 SSO 账户相同的邮箱手动创建一个 Dify 账户
2. 使用 SSO 登录 - 应该链接到现有账户
3. 验证如果 SSO 提供了公司信息，该信息已更新

## 故障排除

### 常见问题

1. **SSO 按钮未出现**
   - 检查 `SSO_ENABLED=true`
   - 验证所有必需的 SSO_* 环境变量已设置
   - 重启 Dify 服务

2. **重定向 URI 不匹配**
   - 确保 `SSO_REDIRECT_URI` 与 SSO 提供商注册的完全匹配
   - 检查尾随斜杠或协议不匹配

3. **令牌交换失败**
   - 验证 `SSO_CLIENT_ID` 和 `SSO_CLIENT_SECRET` 是否正确
   - 检查 `SSO_TOKEN_ENDPOINT` URL 是否可从 Dify 服务器访问
   - 查看服务器日志中的详细错误消息

4. **用户信息错误**
   - 验证 `SSO_USERINFO_ENDPOINT` 返回预期的用户属性
   - 检查 `SSO_SCOPES` 中是否需要其他作用域

### 调试日志

启用调试日志以查看详细的 OAuth 流程信息：

```bash
LOG_LEVEL=DEBUG
```

在 `/app/logs/server.log` 中查看与 OAuth 相关的消息。

### 使用 cURL 手动测试

手动测试您的 SSO 端点：

```bash
# 测试授权端点
curl -I "http://wm.stg.paic.com.cn/gw/oauth/v2/authorize?client_id=Ov23lirUopDC7TuZ3eeD&response_type=code&redirect_uri=http://gaadp.fat001.qa.pab.com/console/api/oauth/authorize/sso"

# 测试令牌端点（获取授权码后）
curl -X POST "http://wm.stg.paic.com.cn/gw/oauth/v2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=Ov23lirUopDC7TuZ3eeD&client_secret=479eac814f270a0fad2fe682a8cdbef6bc936b7f&code=YOUR_CODE&grant_type=authorization_code&redirect_uri=http://gaadp.fat001.qa.pab.com/console/api/oauth/authorize/sso"
```

## 安全考虑

1. **HTTPS**：生产部署使用 HTTPS
2. **客户端密钥**：保持 `SSO_CLIENT_SECRET` 安全并定期轮换
3. **重定向 URI**：在 SSO 提供商中注册确切的重定向 URI
4. **作用域限制**：从 SSO 提供商请求最少必需的作用域

## 特定环境配置

### 开发环境

```bash
SSO_ENABLED=true
SSO_AUTH_ENDPOINT=http://wm.stg.paic.com.cn/gw/oauth/v2/authorize
SSO_TOKEN_ENDPOINT=http://wm.stg.paic.com.cn/gw/oauth/v2/token
SSO_USERINFO_ENDPOINT=http://wm.stg.paic.com.cn/gw/oauth/v2/userInfo
SSO_CLIENT_ID=Ov23lirUopDC7TuZ3eeD
SSO_CLIENT_SECRET=479eac814f270a0fad2fe682a8cdbef6bc936b7f
SSO_REDIRECT_URI=http://localhost:3000/console/api/oauth/authorize/sso
SSO_SCOPES=
```

### 生产环境

```bash
SSO_ENABLED=true
SSO_AUTH_ENDPOINT=http://wm.prod.paic.com.cn/gw/oauth/v2/authorize
SSO_TOKEN_ENDPOINT=http://wm.prod.paic.com.cn/gw/oauth/v2/token
SSO_USERINFO_ENDPOINT=http://wm.prod.paic.com.cn/gw/oauth/v2/userInfo
SSO_CLIENT_ID=PROD_CLIENT_ID
SSO_CLIENT_SECRET=PROD_CLIENT_SECRET
SSO_REDIRECT_URI=https://your-production-dify.com/console/api/oauth/authorize/sso
SSO_SCOPES=
```

## 实现细节

### 修改的文件

**后端：**
- `api/configs/feature/__init__.py` - 添加了 SSO 配置
- `api/libs/oauth.py` - 添加了 CustomSSOOAuth 类
- `api/controllers/console/auth/oauth.py` - 添加了 SSO 提供商支持
- `api/models/account.py` - 添加了 company 字段
- `api/services/feature_service.py` - 添加了 SSO 功能标志
- `docker/.env.example` - 添加了 SSO 配置示例

**前端：**
- `web/app/signin/components/custom-sso-auth.tsx` - SSO 登录按钮组件
- `web/app/signin/normal-form.tsx` - 集成了 SSO 按钮
- `web/types/feature.ts` - 添加了 SSO 类型定义

**数据库：**
- `api/migrations/versions/2025_01_16_1200-add_company_field_to_accounts.py` - company 字段的迁移

该实现遵循 Dify 现有的 OAuth 模式，并与当前的身份验证系统无缝集成。