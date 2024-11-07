# GitEval-llm 仓库

## 项目介绍

**GitEval-llm** 是 GitEval 项目的大模型部分，并作为 GitEval-Backend 的一个依赖服务运行。该服务提供了基于大模型的 Git 数据分析与推断功能，包括领域识别、用户评估和国籍推断等。

## 涉及技术

- **通信**：gRPC
- **大模型实现**：LangChain
- **向量搜索**：Faiss

## 主要功能

1. **getDomain**：获取用户对应的领域列表
2. **getEvaluation**：获取用户的整体评价
3. **getNation**：基于用户关系网络推断用户国籍

## 软件架构

项目文件结构：

```
GitEval-llm/
├── api/                   # API 定义文件夹
│   ├── __init__.py        # 初始化文件
│   ├── llm.proto          # gRPC 和 Protobuf 文件，定义 LLM 服务接口
│   ├── llm_pb2.py         # 通过 Protobuf 编译生成的 Python 文件
│   └── llm_pb2_grpc.py    # 通过 Protobuf 编译生成的 gRPC 代码
│
├── config/                # 配置文件夹
│   ├── __init__.py        # 初始化文件
│   ├── config.py          # 配置相关文件，负责加载和管理配置
│   ├── config.yaml        # 默认配置文件，包含数据库、服务端口等基本信息
│   └── dev.yaml           # 开发环境配置文件
│
├── server/                # 服务器主模块，包含业务逻辑
│   ├── __init__.py        # 初始化文件
│   ├── handlers.py        # 请求处理器，处理不同 API 请求
│   ├── models.py          # 数据模型定义文件，定义运算过程中的结构体
│   ├── search.py          # 向量搜索工具，主要用于国家的预搜索，提高命中率
│   └── service.py         # 服务层文件，包含主要业务逻辑
│
├── .dockerignore          # Docker 忽略文件，指定哪些文件不包含在 Docker 镜像中
├── .gitignore             # Git 忽略文件，指定哪些文件不提交到版本控制
├── Dockerfile             # Docker 配置文件，用于构建 Docker 镜像
├── main.py                # 主程序入口，启动项目
├── README.md              # 项目说明文档，包含项目概述和使用说明
└── requirements.txt       # Python 依赖文件，列出项目依赖的第三方库
```

## 功能模块

### API 部分

- 使用 Proto 定义 gRPC 接口，借助 `protoc` 编译器生成 `llm_pb2.py` 和 `llm_pb2_grpc.py` 文件，定义了服务接口、消息类型等，供客户端与服务器之间进行通信。

### Config 部分

- 包含配置文件和读取配置的相关功能。配置文件管理服务运行所需的参数，如 `api_key`、数据库配置等。

### Server 层

Server 层主要包含三个部分：**Model、Controller 和 Service**。

#### Model 部分

定义了涉及运算过程中的数据模型，如仓库信息、用户信息等。

#### Controller 部分

- 负责分发请求并将 RPC 请求转换为 Model 可识别的数据结构。
- 接收来自客户端的请求，调用 Service 层进行处理。

#### Service 部分

包含核心业务逻辑，具体功能如下：

##### 1. getDomain：

- 预先定义技术领域列表。
- 客户端通过 gRPC 发送仓库信息（repo）。
- 使用仓库的 **编程语言** 和 **README 文件** 来推测涉及的技术领域及其置信度。
- 使用 **正则匹配** 进行格式清洗，提取出技术领域。
- 合并多个仓库的技术领域信息，并进行去重。
- 对领域进行筛选：去除出现次数低于一定比例的领域，去除置信度低的领域。
- 对剩余领域进行 **加权平均**，根据仓库的贡献大小调整权重。
- 返回最终的领域列表。

##### 2. getEvaluation：

- 根据用户信息（包括贡献、个人信息等）对用户进行综合评估。
- 对于数据库量大的情况，使用 **上下文构建** 来优化评价过程。

##### 3. getNation：

- 通过用户的关系网络推断其可能的国籍。
- 客户端发送用户的 **follower**、**following**、个人简介等信息。
- 使用 **FAISS** 进行 **向量搜索** 获取可能的地区列表。
- 最终通过大模型对地区进行推断，返回匹配的地区及置信度。

### Main.py 部分

- 作为程序的入口，启动异步路由。
- 使用 gRPC 中间件 **grpc.aio.ServerInterceptor** 进行请求监测。
- 初始化相关配置，并使用中间件记录日志、捕获异常，确保服务稳定运行。

## 如何使用

1. 修改 `config/config.yaml` 配置文件为您的实际配置。
2. **python运行**：
    
    - 安装依赖并启动项目：
    ```bash
    pip install --no-cache-dir -r requirements.txt
    python main.py
    ```
    
3. **通过 Docker 启动**：
    - 构建并运行 Docker 镜像：
    ```bash
    docker build -t llm:v1 . && docker run --name llm_container -p 11028:11028 llm:v1
    ```

