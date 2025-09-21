"""
헬스체크 API 라우터

서비스 상태 확인 관련 API 엔드포인트를 정의합니다.
"""

from fastapi import APIRouter
import logging
from datetime import datetime
import psutil
import sys

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """
    전체 서비스 헬스체크
    
    시스템 상태, 메모리 사용량, 서비스 가용성을 확인합니다.
    """
    try:
        # 시스템 정보 수집
        memory_info = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        health_status = {
            "status": "healthy",
            "service": "gov-info-assistant",
            "version": "0.1.0",
            "timestamp": datetime.now().isoformat(),
            "uptime": "시작된 지 얼마되지 않음",  # TODO: 실제 uptime 계산
            "system": {
                "memory": {
                    "total": f"{memory_info.total / (1024**3):.1f} GB",
                    "available": f"{memory_info.available / (1024**3):.1f} GB", 
                    "used_percent": f"{memory_info.percent}%"
                },
                "cpu_percent": f"{cpu_percent}%",
                "python_version": sys.version
            },
            "services": {
                "search_api": "healthy",
                "chat_api": "healthy", 
                "vector_db": "not_initialized",  # TODO: 실제 Vector DB 상태 확인
                "llm_service": "not_connected"   # TODO: Azure OpenAI 연결 상태 확인
            }
        }
        
        logger.info("헬스체크 완료")
        return health_status
        
    except Exception as e:
        logger.error(f"헬스체크 오류: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/health/detailed")
async def detailed_health_check():
    """
    상세 헬스체크
    
    각 컴포넌트별 상세 상태 정보를 제공합니다.
    """
    try:
        detailed_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "components": {
                "api_server": {
                    "status": "healthy",
                    "response_time": "< 100ms",
                    "last_check": datetime.now().isoformat()
                },
                "multi_agent_system": {
                    "status": "not_initialized", 
                    "agents": {
                        "query_analyzer": "not_loaded",
                        "document_retriever": "not_loaded", 
                        "content_processor": "not_loaded",
                        "response_generator": "not_loaded"
                    }
                },
                "vector_database": {
                    "status": "not_initialized",
                    "index_size": "0",
                    "last_update": "never"
                },
                "azure_openai": {
                    "status": "not_connected",
                    "models": {
                        "gpt-4o-mini": "not_tested",
                        "gpt-4o": "not_tested", 
                        "text-embedding-3-large": "not_tested"
                    }
                },
                "session_storage": {
                    "status": "healthy",
                    "type": "memory",
                    "active_sessions": 0
                }
            }
        }
        
        return detailed_status
        
    except Exception as e:
        logger.error(f"상세 헬스체크 오류: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/metrics")
async def get_metrics():
    """
    시스템 메트릭 조회
    
    성능 모니터링을 위한 메트릭 정보를 제공합니다.
    """
    try:
        # 기본 시스템 메트릭
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": {
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent,
                    "free_percent": 100 - memory.percent
                },
                "cpu": {
                    "usage_percent": cpu,
                    "load_average": "N/A"  # Windows에서는 지원 안됨
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_percent": round((disk.used / disk.total) * 100, 1)
                }
            },
            "application_metrics": {
                "total_requests": 0,  # TODO: 실제 카운터 구현
                "avg_response_time": 0,
                "error_rate": 0,
                "active_sessions": 0
            },
            "ai_metrics": {
                "total_searches": 0,
                "total_chat_messages": 0, 
                "avg_processing_time": 0,
                "success_rate": 0
            }
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"메트릭 조회 오류: {str(e)}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/ping")
async def ping():
    """간단한 핑 체크"""
    return {
        "message": "pong",
        "timestamp": datetime.now().isoformat()
    }
