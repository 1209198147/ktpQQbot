# 课堂派QQ助手使用指南

> 本项目基于ncatbot实现

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

## 🗄️ 数据库配置

### 1. 连接MySQL服务器
```bash
mysql -u root -p
```

### 2. 执行建表语句
```sql
SOURCE sql/robot-vue.sql;
```

## ⚙️ 配置文件设置

### 主配置文件 (`config.yml`)
```yaml
qq: 机器人QQ号  # 替换为你的机器人QQ号
reply_p: 0.4    # 群聊中回复别人的概率（0.0-1.0）
group_uin: "群号1,群号2"  # 白名单群聊群号，用英文逗号分隔

# AI模型配置
model: "gemini"  # 或 "deepseek"
apiKey: "你的API密钥"  # 替换为对应模型的API密钥
system_prompt: "系统提示词文件路径"  # 提示词文件路径

# 会话管理
group_conversation_maxLen: 50   # 群聊对话最大保存数（负数表示无限制）
private_conversation_maxLen: 100 # 私聊对话最大保存数（负数表示无限制）
```

### 数据库配置文件 (`database_config.yaml`)
```yaml
user: "数据库用户名"     # 替换为你的数据库用户名
password: "数据库密码"   # 替换为你的数据库密码
host: "数据库地址"       # 如 localhost 或 IP
port: 3306              # 数据库端口号
database: "数据库名"     # 替换为你的数据库名称
charset: "utf8mb4"       # 字符集编码
```

## 🚀 启动机器人

```bash
python main.py
```

## 📌 使用说明

1. **配置文件注意事项**：
   - 请确保两个配置文件都放在项目根目录
   - 所有字符串值都需要用引号包裹
   - 数值类型（如概率、最大长度）不要加引号

2. **白名单群聊**：
   - 只有在`group_uin`中指定的群聊才会响应
   - 多个群号用英文逗号分隔，**不要加空格**

3. **AI模型选择**：
   - 支持 Gemini 或 DeepSeek 模型
   - 确保提供对应模型的正确API密钥

4. **会话长度限制**：
   - 设置为负数表示无限保存历史消息
   - 根据服务器性能合理设置，避免内存溢出

> **提示**：首次运行前，请仔细检查所有配置项是否正确填写！