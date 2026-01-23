# Lesson Plan Agent

Lesson Plan Agent 是一个基于 FastAPI 和 LLM (大语言模型) 的智能教案生成服务。它能够根据用户输入的学科、年级、主题、时长和教学风格，实时流式生成结构化的教案内容。

## ✨ 特性

-   **智能生成**: 集成阿里云 DashScope (Qwen 模型)，生成高质量教案。
-   **流式响应**: 使用 Server-Sent Events (SSE) 技术，实现打字机效果的实时响应。
-   **并发控制**: 内置信号量机制，限制同时请求大模型的并发数，保护服务稳定性。
-   **Docker 支持**: 提供 Docker 和 Docker Compose 配置，一键部署。
-   **上下文支持**: 支持上传本地文件（.md, .txt 等）动态插入上下文辅助生成。
-   **结构化展示**: 实时展示 Token 消耗、生成延迟、关键概念、难度等级等结构化数据。

## 🛠️ 技术栈

-   Python 3.10+
-   FastAPI
-   AsyncIO
-   DashScope SDK (通义千问)
-   Docker & Docker Compose

## 🏗️ 架构说明

本服务采用典型的分层架构：

1.  **API Layer (FastAPI)**: 处理 HTTP 请求，验证输入参数 (Pydantic)，管理 SSE 连接。
2.  **Service Layer**:
    *   `LessonPlanService`: 编排生成逻辑，加载 Prompt，处理上下文文件，解析流式响应中的元数据。
    *   `LLMService`: 封装与阿里云 DashScope 的交互，实现流式调用，并负责**并发控制** (Semaphore)。
3.  **Infrastructure**:
    *   Docker: 容器化运行环境。
    *   Logging: 统一日志管理。

## 📂 项目结构

```text
.
├── app/
│   ├── core/           # 核心配置 (Config, Logging, Lifespan)
│   ├── prompts/        # Prompt 模板管理
│   ├── routers/        # API 路由定义 (Lesson Plan, Health)
│   ├── schemas/        # Pydantic 数据模型
│   ├── services/       # 业务逻辑 (LLM Service, Lesson Plan Service)
│   ├── utils/          # 工具函数
│   └── main.py         # 应用入口
├── Dockerfile          # Docker 构建文件
├── docker-compose.yaml # Docker Compose 编排文件
├── requirements.txt    # Python 依赖列表
└── README.md           # 项目文档
```

## 🚀 快速开始

### 前置要求

-   Python 3.10+
-   有效的 DashScope API Key (阿里云)

### 1. 本地运行

1.  **克隆项目**
    ```bash
    git clone https://github.com/zhkanc/Agent.git
    cd Agent
    ```

2.  **创建虚拟环境并安装依赖**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/macOS
    source venv/bin/activate

    pip install -r requirements.txt
    ```

3.  **配置环境变量**
    在项目根目录创建 `.env` 文件，并填入以下内容：
    ```env
    DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx  # 替换为你的 API Key
    # 可选配置
    # MODEL_NAME=qwen-plus
    # LOG_LEVEL=info
    # LLM_CONCURRENCY_LIMIT=5
    ```

4.  **启动服务**
    ```bash
    python app/main.py
    ```
    服务将在 `http://0.0.0.0:8000` 启动。

### 2. Docker 运行

#### 使用 Docker Compose (推荐)

1.  **配置环境变量**
    同样需要创建 `.env` 文件并配置 `DASHSCOPE_API_KEY`。

2.  **启动服务**
    ```bash
    docker-compose up -d --build
    ```

#### 使用 Docker Run (手动)

1.  **构建镜像**
    ```bash
    docker build -t lesson-plan-agent .
    ```

2.  **运行容器**
    ```bash
    docker run -d \
      --name lesson-plan-agent \
      -p 8000:8000 \
      --env-file .env \
      lesson-plan-agent
    ```

## 🔌 API 接口

### 1. 在线文档 (Swagger UI)

启动服务后，访问以下地址查看交互式 API 文档：

-   **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. 健康检查

-   **URL**: `/health`
-   **Method**: `GET`
-   **Response**: `{"status": "ok"}`

### 3. 生成教案 (流式)

-   **URL**: `/lesson-plan/generate`
-   **Method**: `POST`
-   **Content-Type**: `application/json`
-   **Response Type**: `text/event-stream`

**请求示例**:

```bash
curl -X POST "http://localhost:8000/lesson-plan/generate" \
     -H "Content-Type: application/json" \
     -d '{
           "subject": "IGCSE Economics",
           "grade_level": "Grade 10",
           "topic": "Supply and Demand",
           "duration": 45,
           "teaching_style": "Inquiry-based Learning"
         }'
```

**响应数据流**:

响应为 SSE 格式，包含以下事件类型：
-   `content`: 教案文本内容片段。
-   `error`: 发生错误时的信息。
-   `end`: 生成结束，包含元数据 (Metadata) 和 Token 使用统计。

## ⚙️ 配置说明

主要配置项位于 `app/core/config.py`，可通过环境变量覆盖：

| 环境变量 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `DASHSCOPE_API_KEY` | **(必填)** 阿里云 DashScope API 密钥 | - |
| `MODEL_NAME` | 使用的模型名称 | `qwen-plus` |
| `LOG_LEVEL` | 日志级别 | `info` |
| `LLM_CONCURRENCY_LIMIT` | LLM 请求并发限制 | `5` |

## 📝 开发指南

-   **添加依赖**: 修改 `requirements.txt`。
-   **Prompt 修改**: 编辑 `app/prompts/lesson_plan/outline.yaml`。
-   **上下文文件**: 可在 `app/context/` 目录(需自行创建)下添加本地上下文文件，用于辅助生成。
-   **并发调整**: 修改配置中的 `LLM_CONCURRENCY_LIMIT` 可控制同时请求大模型的数量。
