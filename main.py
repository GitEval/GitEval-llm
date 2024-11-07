import grpc
from api import llm_pb2_grpc
from server.handlers import LLMServiceServicer
from config import config
import logging
from datetime import datetime
import asyncio

# 加载配置
config.get_config('./config/config.yaml')

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 日志中间件
class LoggingInterceptor(grpc.aio.ServerInterceptor):  # 使用 grpc.aio.ServerInterceptor
    async def intercept_service(self, continuation, handler_call_details):
        # 记录请求开始时间
        start_time = datetime.now()

        # 获取请求方法名
        method_name = handler_call_details.method
        logger.info("Received gRPC request: %s", method_name)

        # 获取处理结果
        response = await continuation(handler_call_details)  # 等待处理结果

        # 请求结束时间
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("Completed gRPC request: %s, duration: %.2f seconds", method_name, duration)

        return response

# 异步的服务器启动函数
async def serve():
    server = grpc.aio.server(interceptors=[LoggingInterceptor()])
    llm_pb2_grpc.add_LLMServiceServicer_to_server(LLMServiceServicer(), server)
    server.add_insecure_port(config.port)
    logger.info(f"Starting server on port {config.port}")
    await server.start()
    await server.wait_for_termination()

# 主函数：启动服务器
if __name__ == '__main__':
    asyncio.run(serve())  # 使用 asyncio.run 来启动异步服务器
