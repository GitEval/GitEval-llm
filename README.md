





# GitEval-llm仓库

#### 介绍

GitEval-llm主要实现了GitEval项目的大模型部分,并作为GitEval-Backend的一个依赖服务运行

### 涉及技术

- 通信：grpc通信
- 大模型实现：langChain

#### 软件架构

软件架构说明 

```
GitEval-llm/
├── api/                   # API 定义文件夹
│   ├── __init__.py        # 初始化文件
│   ├── llm.proto          # gRPC 和 Protobuf 文件，用于定义 LLM 服务的接口
│   ├── llm_pb2.py         # 通过 Protobuf 编译生成的 Python 文件
│   └── llm_pb2_grpc.py    # 通过 Protobuf 编译生成的 gRPC 代码
│
├── config/                # 配置文件夹
│   ├── __init__.py        # 初始化文件
│   ├── config.py          # 配置相关的 Python 文件，负责加载和管理配置
│   ├── config.yaml        # 默认配置文件，包含数据库、服务端口等基本信息
│   └── dev.yaml           # 开发环境的配置文件
│
├── server/                # 服务器主模块，包含业务逻辑
│   ├── __init__.py        # 初始化文件
│   ├── handlers.py        # 请求处理器，用于处理不同的 API 请求
│   ├── models.py          # 数据模型定义文件，用于定义数据库模型或数据结构
│   └── service.py         # 服务层文件，包含主要的业务逻辑
│
├── .dockerignore          # Docker 忽略文件，指定哪些文件或文件夹不被包含在 Docker 镜像中
├── .gitignore             # Git 忽略文件，指定哪些文件或文件夹不被提交到版本控制
├── Dockerfile             # Docker 配置文件，用于构建 Docker 镜像
├── main.py                # 主程序入口，启动项目
├── README.md              # 项目说明文档，包含项目概述和使用说明
└── requirements.txt       # Python 依赖文件，列出项目依赖的第三方库

```



主要提供三个接口：

1. getDomain获取用户对应的领域列表,基于用户的仓库中的readme文件和用户的常用语言
2. getEvaluation获取对用户的整体评价
3. getNation基于用户关系网络推断用户国籍