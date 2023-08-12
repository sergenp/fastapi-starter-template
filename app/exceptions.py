from typing import Callable, List, Tuple, Type

import jwt
import minio
from fastapi import status
from fastapi.responses import JSONResponse


def jwt_decode_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid Token"}
    )


def jwt_expired_signature_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Expired token"}
    )


def minio_exc_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )


def get_exception_handlers() -> List[Tuple[Type[Exception], Callable]]:
    return [
        (minio.error.MinioException, minio_exc_handler),
        (jwt.ExpiredSignatureError, jwt_expired_signature_error_handler),
        (jwt.InvalidTokenError, jwt_decode_error_handler),
    ]
