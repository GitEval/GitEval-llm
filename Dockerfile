# 使用官方 Python 作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 将项目的依赖文件复制到工作目录
COPY requirements.txt /app/

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 将项目代码复制到工作目录
COPY . /app/

# 设置环境变量（可选，根据需要配置）
ENV PYTHONUNBUFFERED=1

# 暴露应用端口（如果有，依据你的应用需求）
EXPOSE 5000

# 启动应用（假设你的主程序是 main.py）
CMD ["python", "main.py"]
