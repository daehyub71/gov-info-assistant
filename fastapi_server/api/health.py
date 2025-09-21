"""
헬스체크 API 엔드포인트
"""
import time
import psutil
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

from fastapi_server.core.config import settings
from fastapi_server.core.logging_config import get_logger, log_api_request

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["Health"])


class HealthStatus(BaseModel):
    """헬스체크 응답 모델"""
    status: str
    timestamp: str
    version: str
    uptime: float
    environment: str


class DetailedHealthStatus(BaseModel):
    """상세 헬스체크 응답 모델"""
    status: str
    timestamp: str
    version: str
    uptime: float
    environment: str
    system: Dict[str, Any]
    services: Dict[str, Any]
    database: Dict[str, Any]
    disk_usage: Dict[str, Any]


# 애플리케이션 시작 시간
app_start_time = time.time()


def check_azure_openai() -> Dict[str, Any]:
    """Azure OpenAI 서비스 상태 확인"""
    try:
        # 실제 환경에서는 간단한 API 호출로 확인
        # 여기서는 설정 유효성만 검사
        if not settings.AOAI_ENDPOINT or not settings.AOAI_API_KEY:
            return {
                "status": "unhealthy",
                "message": "Azure OpenAI configuration missing",
                "response_time": None
            }
        
        return {
            "status": "healthy",
            "message": "Configuration valid",
            "response_time": 0.1,
            "endpoint": settings.AOAI_ENDPOINT[:50] + "..." if len(settings.AOAI_ENDPOINT) > 50 else settings.AOAI_ENDPOINT
        }
    except Exception as e:
        logger.error(f"Azure OpenAI health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": str(e),
            "response_time": None
        }


def check_vector_database() -> Dict[str, Any]:
    """벡터 데이터베이스 상태 확인"""
    try:
        vector_db_path = Path(settings.VECTOR_DB_PATH)
        
        if not vector_db_path.exists():
            return {
                "status": "warning",
                "message": "Vector database not initialized",
                "path": str(vector_db_path),
                "size": 0
            }
        
        # 디렉토리 크기 계산
        total_size = sum(f.stat().st_size for f in vector_db_path.rglob('*') if f.is_file())
        
        return {
            "status": "healthy",
            "message": "Vector database accessible",
            "path": str(vector_db_path),
            "size": total_size,
            "size_mb": round(total_size / (1024 * 1024), 2)
        }
    except Exception as e:
        logger.error(f"Vector database health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": str(e),
            "path": settings.VECTOR_DB_PATH,
            "size": 0
        }


def check_session_database() -> Dict[str, Any]:
    """세션 데이터베이스 상태 확인"""
    try:
        session_db_path = Path(settings.SESSION_DB_PATH)
        
        if not session_db_path.exists():
            return {
                "status": "warning",
                "message": "Session database not initialized",
                "path": str(session_db_path),
                "size": 0
            }
        
        size = session_db_path.stat().st_size
        
        return {
            "status": "healthy", 
            "message": "Session database accessible",
            "path": str(session_db_path),
            "size": size,
            "size_mb": round(size / (1024 * 1024), 2)
        }
    except Exception as e:
        logger.error(f"Session database health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": str(e),
            "path": settings.SESSION_DB_PATH,
            "size": 0
        }


def get_system_metrics() -> Dict[str, Any]:
    """시스템 메트릭 수집"""
    try:
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 메모리 사용률
        memory = psutil.virtual_memory()
        
        # 디스크 사용률
        disk = psutil.disk_usage('/')
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2)
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": round((disk.used / disk.total) * 100, 2),
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2)
            }
        }
    except Exception as e:
        logger.error(f"System metrics collection failed: {e}")
        return {
            "cpu": {"percent": 0, "count": 0},
            "memory": {"total": 0, "available": 0, "percent": 0, "used": 0},
            "disk": {"total": 0, "used": 0, "free": 0, "percent": 0}
        }


@router.get("/", response_model=HealthStatus)
async def basic_health_check():
    """기본 헬스체크"""
    start_time = time.time()
    
    try:
        current_time = datetime.now(timezone.utc)
        uptime = time.time() - app_start_time
        
        response = HealthStatus(
            status="healthy",
            timestamp=current_time.isoformat(),
            version=settings.APP_VERSION,
            uptime=round(uptime, 2),
            environment="development" if settings.is_development else "production"
        )
        
        response_time = time.time() - start_time
        log_api_request(
            endpoint="/health",
            method="GET",
            status_code=200,
            response_time=response_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        response_time = time.time() - start_time
        log_api_request(
            endpoint="/health",
            method="GET", 
            status_code=500,
            response_time=response_time,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )


@router.get("/detailed", response_model=DetailedHealthStatus)
async def detailed_health_check():
    """상세 헬스체크"""
    start_time = time.time()
    
    try:
        current_time = datetime.now(timezone.utc)
        uptime = time.time() - app_start_time
        
        # 시스템 메트릭 수집
        system_metrics = get_system_metrics()
        
        # 서비스 상태 확인
        azure_openai_status = check_azure_openai()
        vector_db_status = check_vector_database()
        session_db_status = check_session_database()
        
        # 전체 상태 결정
        service_statuses = [
            azure_openai_status["status"],
            vector_db_status["status"],
            session_db_status["status"]
        ]
        
        if "unhealthy" in service_statuses:
            overall_status = "unhealthy"
        elif "warning" in service_statuses:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        # 디스크 사용량 체크
        disk_usage = {}
        for path_name, path_value in [
            ("vector_db", settings.VECTOR_DB_PATH),
            ("session_db", settings.SESSION_DB_PATH),
            ("logs", Path(settings.LOG_FILE_PATH).parent)
        ]:
            try:
                path_obj = Path(path_value)
                if path_obj.exists():
                    if path_obj.is_file():
                        size = path_obj.stat().st_size
                    else:
                        size = sum(f.stat().st_size for f in path_obj.rglob('*') if f.is_file())
                    
                    disk_usage[path_name] = {
                        "path": str(path_obj),
                        "size": size,
                        "size_mb": round(size / (1024 * 1024), 2)
                    }
                else:
                    disk_usage[path_name] = {
                        "path": str(path_obj),
                        "size": 0,
                        "size_mb": 0
                    }
            except Exception as e:
                disk_usage[path_name] = {
                    "path": str(path_value),
                    "size": 0,
                    "size_mb": 0,
                    "error": str(e)
                }
        
        response = DetailedHealthStatus(
            status=overall_status,
            timestamp=current_time.isoformat(),
            version=settings.APP_VERSION,
            uptime=round(uptime, 2),
            environment="development" if settings.is_development else "production",
            system=system_metrics,
            services={
                "azure_openai": azure_openai_status,
                "vector_database": vector_db_status,
                "session_database": session_db_status
            },
            database={
                "vector_db": vector_db_status,
                "session_db": session_db_status
            },
            disk_usage=disk_usage
        )
        
        response_time = time.time() - start_time
        log_api_request(
            endpoint="/health/detailed",
            method="GET",
            status_code=200,
            response_time=response_time,
            overall_status=overall_status
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        response_time = time.time() - start_time
        log_api_request(
            endpoint="/health/detailed",
            method="GET",
            status_code=500,
            response_time=response_time,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Detailed health check failed"
        )


@router.get("/readiness")
async def readiness_check():
    """준비 상태 확인 (Kubernetes 등에서 사용)"""
    start_time = time.time()
    
    try:
        # 필수 서비스 상태 확인
        azure_openai_status = check_azure_openai()
        
        if azure_openai_status["status"] == "unhealthy":
            response_time = time.time() - start_time
            log_api_request(
                endpoint="/health/readiness",
                method="GET",
                status_code=503,
                response_time=response_time,
                ready=False
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not ready"
            )
        
        response_time = time.time() - start_time
        log_api_request(
            endpoint="/health/readiness",
            method="GET",
            status_code=200,
            response_time=response_time,
            ready=True
        )
        
        return {"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        response_time = time.time() - start_time
        log_api_request(
            endpoint="/health/readiness",
            method="GET",
            status_code=500,
            response_time=response_time,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Readiness check failed"
        )


@router.get("/liveness")
async def liveness_check():
    """생존 상태 확인 (Kubernetes 등에서 사용)"""
    start_time = time.time()
    
    try:
        # 기본적인 애플리케이션 상태만 확인
        current_time = datetime.now(timezone.utc)
        
        response_time = time.time() - start_time
        log_api_request(
            endpoint="/health/liveness",
            method="GET",
            status_code=200,
            response_time=response_time,
            alive=True
        )
        
        return {"status": "alive", "timestamp": current_time.isoformat()}
        
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        response_time = time.time() - start_time
        log_api_request(
            endpoint="/health/liveness",
            method="GET",
            status_code=500,
            response_time=response_time,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Liveness check failed"
        )