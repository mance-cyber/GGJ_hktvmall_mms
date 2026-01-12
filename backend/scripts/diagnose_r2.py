#!/usr/bin/env python
# =============================================
# R2 連接診斷腳本
# =============================================

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# 設置控制台編碼（Windows 兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import boto3
from botocore.exceptions import ClientError
from app.config import get_settings

settings = get_settings()

print("=" * 60)
print("R2 連接診斷")
print("=" * 60)

print("\n【配置信息】")
print(f"Account ID (from endpoint): 43f382b11b94c725408508e1280bb173")
print(f"Bucket Name: {settings.r2_bucket}")
print(f"Endpoint: {settings.r2_endpoint}")
print(f"Access Key: {settings.r2_access_key[:10]}...")
print(f"Secret Key: {settings.r2_secret_key[:10]}...")

print("\n【測試 1: 初始化 S3 客戶端】")
try:
    s3_client = boto3.client(
        's3',
        endpoint_url=settings.r2_endpoint,
        aws_access_key_id=settings.r2_access_key,
        aws_secret_access_key=settings.r2_secret_key,
        region_name='auto',
    )
    print("✓ S3 客戶端初始化成功")
except Exception as e:
    print(f"❌ 初始化失敗：{e}")
    sys.exit(1)

print("\n【測試 2: 列出所有 Buckets】")
try:
    response = s3_client.list_buckets()
    buckets = response.get('Buckets', [])

    if buckets:
        print(f"✓ 找到 {len(buckets)} 個 Bucket(s)：")
        for bucket in buckets:
            print(f"  - {bucket['Name']}")
            print(f"    創建時間: {bucket['CreationDate']}")
    else:
        print("⚠️  未找到任何 Bucket")
        print("\n可能原因：")
        print("  1. API Token 權限不足")
        print("  2. Bucket 尚未創建")
        print("  3. Account ID 不正確")
except ClientError as e:
    print(f"❌ 列出 Buckets 失敗：{e}")
    error_code = e.response.get('Error', {}).get('Code', '')
    if error_code == 'InvalidAccessKeyId':
        print("\n診斷：Access Key ID 無效")
        print("解決方案：請檢查 R2_ACCESS_KEY 是否正確")
    elif error_code == 'SignatureDoesNotMatch':
        print("\n診斷：Secret Access Key 無效")
        print("解決方案：請檢查 R2_SECRET_KEY 是否正確")
except Exception as e:
    print(f"❌ 未知錯誤：{e}")

print("\n【測試 3: 檢查特定 Bucket】")
try:
    s3_client.head_bucket(Bucket=settings.r2_bucket)
    print(f"✓ Bucket '{settings.r2_bucket}' 存在且可訪問")
except ClientError as e:
    error_code = e.response.get('Error', {}).get('Code', '')
    if error_code == '404':
        print(f"❌ Bucket '{settings.r2_bucket}' 不存在")
        print("\n可能原因：")
        print("  1. Bucket 名稱拼寫錯誤")
        print("  2. Bucket 未成功創建")
        print("  3. API Token 沒有訪問此 Bucket 的權限")
    elif error_code == '403':
        print(f"❌ 無權訪問 Bucket '{settings.r2_bucket}'")
        print("\n解決方案：")
        print("  1. 檢查 API Token 權限")
        print("  2. 確保 Token 有 'Object Read & Write' 權限")
    else:
        print(f"❌ 錯誤：{e}")

print("\n【測試 4: API Token 權限測試】")
print("嘗試列出 Bucket 內容...")
try:
    response = s3_client.list_objects_v2(
        Bucket=settings.r2_bucket,
        MaxKeys=1
    )
    print("✓ API Token 有讀取權限")
except ClientError as e:
    error_code = e.response.get('Error', {}).get('Code', '')
    if error_code == 'NoSuchBucket':
        print(f"❌ Bucket '{settings.r2_bucket}' 不存在")
    elif error_code == 'AccessDenied':
        print("❌ API Token 權限不足")
    else:
        print(f"❌ 錯誤：{e}")

print("\n" + "=" * 60)
print("診斷完成")
print("=" * 60)
