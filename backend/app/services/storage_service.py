# =============================================
# 存儲服務抽象層
# =============================================

"""
存儲服務 - 支持本地和 Cloudflare R2 存儲

使用方式：
    storage = StorageService()

    # 保存文件
    url = storage.save_file(
        file_data=b"...",
        file_path="input/task-123/image.jpg"
    )

    # 獲取公開 URL
    url = storage.get_public_url("input/task-123/image.jpg")

    # 刪除文件
    storage.delete_file("input/task-123/image.jpg")
"""

import logging
from pathlib import Path
from typing import Optional
import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """統一存儲服務 - 自動切換本地/R2"""

    def __init__(self):
        self.use_r2 = settings.use_r2_storage

        if self.use_r2:
            # 初始化 R2 客戶端（使用 S3 API）
            self._init_r2_client()
            logger.info("StorageService initialized with R2 storage")
        else:
            # 本地存儲
            self.local_base_dir = Path(settings.upload_dir)
            self.local_base_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"StorageService initialized with local storage: {self.local_base_dir}")

    def _init_r2_client(self):
        """初始化 Cloudflare R2 客戶端"""
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.r2_endpoint,
                aws_access_key_id=settings.r2_access_key,
                aws_secret_access_key=settings.r2_secret_key,
                region_name='auto',  # R2 使用 'auto' 區域
            )
            self.bucket = settings.r2_bucket
            self.public_url_base = settings.r2_public_url.rstrip('/')

            # 測試連接（使用 list_objects_v2 代替 head_bucket，更可靠）
            try:
                self.s3_client.list_objects_v2(Bucket=self.bucket, MaxKeys=1)
                logger.info(f"Successfully connected to R2 bucket: {self.bucket}")
            except ClientError as test_error:
                # 如果是 NoSuchBucket 錯誤，抛出異常
                if test_error.response.get('Error', {}).get('Code') == 'NoSuchBucket':
                    raise Exception(f"Bucket '{self.bucket}' does not exist")
                # 其他錯誤（如 AccessDenied）記錄警告但繼續
                logger.warning(f"Could not verify bucket access: {test_error}")
                logger.info(f"R2 client initialized for bucket: {self.bucket}")

        except ClientError as e:
            logger.error(f"Failed to initialize R2 client: {e}")
            raise Exception(f"R2 initialization failed: {str(e)}")

    def save_file(self, file_data: bytes, file_path: str) -> str:
        """
        保存文件到存儲

        Args:
            file_data: 文件二進制數據
            file_path: 相對路徑（例如：input/task-123/image.jpg）

        Returns:
            文件的公開 URL 或本地路徑
        """
        if self.use_r2:
            return self._save_to_r2(file_data, file_path)
        else:
            return self._save_to_local(file_data, file_path)

    def _save_to_r2(self, file_data: bytes, file_path: str) -> str:
        """保存文件到 Cloudflare R2"""
        try:
            # 上傳到 R2
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=file_path,
                Body=file_data,
                ContentType=self._guess_content_type(file_path)
            )

            # 返回公開 URL
            public_url = f"{self.public_url_base}/{file_path}"
            logger.info(f"Saved file to R2: {file_path}")
            return public_url

        except ClientError as e:
            logger.error(f"Failed to save file to R2: {e}")
            raise Exception(f"R2 upload failed: {str(e)}")

    def _save_to_local(self, file_data: bytes, file_path: str) -> str:
        """保存文件到本地文件系統"""
        try:
            full_path = self.local_base_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, 'wb') as f:
                f.write(file_data)

            logger.info(f"Saved file to local: {full_path}")
            return str(full_path)

        except Exception as e:
            logger.error(f"Failed to save file to local: {e}")
            raise Exception(f"Local save failed: {str(e)}")

    def get_public_url(self, file_path: str) -> str:
        """
        獲取文件的公開 URL

        Args:
            file_path: 文件路徑（本地完整路徑或 R2 相對路徑）

        Returns:
            公開 URL
        """
        if self.use_r2:
            # R2 模式：構建公開 URL
            # 如果已經是完整 URL，直接返回
            if file_path.startswith('http'):
                return file_path
            return f"{self.public_url_base}/{file_path}"
        else:
            # 本地模式：返回相對路徑（供前端訪問）
            # 將絕對路徑轉換為相對路徑
            if Path(file_path).is_absolute():
                try:
                    rel_path = Path(file_path).relative_to(self.local_base_dir)
                    return f"/uploads/{rel_path.as_posix()}"
                except ValueError:
                    return file_path
            return f"/uploads/{file_path}"

    def delete_file(self, file_path: str) -> bool:
        """
        刪除文件

        Args:
            file_path: 文件路徑

        Returns:
            是否成功刪除
        """
        if self.use_r2:
            return self._delete_from_r2(file_path)
        else:
            return self._delete_from_local(file_path)

    def _delete_from_r2(self, file_path: str) -> bool:
        """從 R2 刪除文件"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket,
                Key=file_path
            )
            logger.info(f"Deleted file from R2: {file_path}")
            return True

        except ClientError as e:
            logger.error(f"Failed to delete file from R2: {e}")
            return False

    def _delete_from_local(self, file_path: str) -> bool:
        """從本地刪除文件"""
        try:
            full_path = self.local_base_dir / file_path
            if full_path.exists():
                full_path.unlink()
                logger.info(f"Deleted file from local: {full_path}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to delete file from local: {e}")
            return False

    def file_exists(self, file_path: str) -> bool:
        """檢查文件是否存在"""
        if self.use_r2:
            try:
                self.s3_client.head_object(Bucket=self.bucket, Key=file_path)
                return True
            except ClientError:
                return False
        else:
            full_path = self.local_base_dir / file_path
            return full_path.exists()

    def _guess_content_type(self, file_path: str) -> str:
        """根據文件擴展名猜測 MIME 類型"""
        ext = Path(file_path).suffix.lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
        }
        return content_types.get(ext, 'application/octet-stream')


# =============================================
# 全局單例實例
# =============================================

_storage_instance: Optional[StorageService] = None


def get_storage() -> StorageService:
    """獲取存儲服務單例"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = StorageService()
    return _storage_instance
