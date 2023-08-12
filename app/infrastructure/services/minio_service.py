import pathlib
import uuid
from typing import Iterator, List

from fastapi import HTTPException, UploadFile
from minio import Minio, datatypes, deleteobjects

from app.config import settings


class MinioService:
    def __init__(self) -> None:
        self.client = Minio(
            f"{settings.MINIO_HOSTNAME}:{settings.MINIO_PORT}",
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_STORAGE_USE_HTTPS,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.max_file_size = settings.MINIO_MAX_UPLOAD_SIZE

    async def _upload_file(self, file: UploadFile, file_path: str = uuid.uuid4().hex) -> str:
        """
        Returns file_path of the uploaded file
        """
        await file.seek(0)
        self.client.put_object(
            self.bucket_name,
            file_path,
            file.file,
            file.size,
            part_size=5 * 1024 * 1024,
        )
        return file_path

    def _delete_file(self, file_path: str) -> bool:
        self.client.remove_object(
            self.bucket_name,
            file_path,
        )
        return True

    async def upload_image(self, file: UploadFile, file_path: str) -> str:
        """
        Returns file_path of the uploaded file
        """
        if file.size > self.max_file_size:
            raise HTTPException(status_code=400, detail="File too large")

        content_type = file.content_type
        if content_type not in ["image/jpeg", "image/png", "image/gif"]:
            raise HTTPException(status_code=400, detail="Invalid file type")

        return await self._upload_file(file, file_path)

    async def upload_image_for_user(
        self, file: UploadFile, user_id: int, bucket_filename=None
    ) -> str:
        """
        Appends user_id to the given bucket_filename before uploading,
        Returns file_path of the uploaded file
        """
        if not bucket_filename or not file.filename:
            bucket_filename = uuid.uuid4().hex
        ext = pathlib.Path(file.filename).suffix
        file_path = f"{user_id}/{bucket_filename}{ext}"
        return await self.upload_image(file, file_path)

    def delete_image(self, image_path: str) -> bool:
        """
        Returns True if file was deleted successfully
        """
        return self._delete_file(image_path)

    def _bulk_list(self, path: str, recursive: bool = True) -> List[datatypes.Object]:
        return self.client.list_objects(self.bucket_name, prefix=path, recursive=recursive)

    def _bulk_delete(self, obj_list: List[datatypes.Object]) -> Iterator[deleteobjects.DeleteError]:
        delete_objects = map(lambda x: deleteobjects.DeleteObject(x.object_name), obj_list)
        return self.client.remove_objects(self.bucket_name, delete_objects)

    def bulk_delete_for_user(self, folder_name: str, user_id: int) -> bool:
        objects = self._bulk_list(f"{user_id}/{folder_name}/", recursive=True)
        if not objects:
            return True

        errors = self._bulk_delete(objects)
        if next(errors, None):
            raise HTTPException(status_code=500, detail="Failed to delete images")
        return True
