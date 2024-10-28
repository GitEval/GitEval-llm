from fastapi import APIRouter, Depends
from . import models
from . import service

router = APIRouter()


def get_service() -> service.Service:
    return service.Service()


@router.post("/getDomain", response_model=models.DomainResponse)
async def get_domain(req: models.DomainRequest, service: service.Service = Depends(get_service)):
    # 创建响应结构体
    return service.get_domain(req)


@router.post("/getEvaluation", response_model=models.EvaluationResponse)
async def get_evaluation(req: models.EvaluationRequest, service: service.Service = Depends(get_service)):
    # 创建响应结构体
    return service.get_evaluation(req)
