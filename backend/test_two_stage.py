# -*- coding: utf-8 -*-
# =============================================
# 两阶段 AI 流程快速测试脚本
# =============================================
#
# 使用方法：
#   cd backend
#   python test_two_stage.py
#
# 或测试特定图片：
#   python test_two_stage.py /path/to/your/image.jpg
#

import sys
import os

# 设置 stdout 编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path

# 添加 app 到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.nano_banana_client import NanoBananaClient
from app.config import get_settings

settings = get_settings()


def test_analysis_prompt():
    """测试 1：检查分析 prompt 构建"""
    print("\n" + "=" * 60)
    print("Test 1: Analysis Prompt Building")
    print("=" * 60)

    client = NanoBananaClient()

    # 白底图模式
    prompt_white = client._build_analysis_prompt("white_bg_topview", None)
    print(f"\n[White BG Mode] Prompt length: {len(prompt_white)} chars")
    print(f"Contains keyword 'JSON': {'JSON' in prompt_white}")

    # 专业摄影模式（带风格）
    prompt_pro = client._build_analysis_prompt("professional_photo", "Warm natural light")
    print(f"\n[Professional Mode] Prompt length: {len(prompt_pro)} chars")
    print(f"Contains user style: {'Warm natural light' in prompt_pro}")

    print("\n[PASS] Analysis Prompt test passed")


def test_fallback():
    """测试 2：检查降级方案"""
    print("\n" + "=" * 60)
    print("Test 2: Fallback Mechanism")
    print("=" * 60)

    client = NanoBananaClient()

    # 白底图降级
    fallback_white = client._get_fallback_analysis("white_bg_topview", None)
    print(f"\n[White BG Fallback]")
    print(f"  - fallback flag: {fallback_white.get('fallback', False)}")
    print(f"  - has generated_prompt: {bool(fallback_white.get('generated_prompt'))}")
    print(f"  - prompt length: {len(fallback_white.get('generated_prompt', ''))}")

    # 专业摄影降级
    fallback_pro = client._get_fallback_analysis("professional_photo", "test style")
    print(f"\n[Professional Fallback]")
    print(f"  - fallback flag: {fallback_pro.get('fallback', False)}")
    print(f"  - has generated_prompt: {bool(fallback_pro.get('generated_prompt'))}")

    print("\n[PASS] Fallback test passed")


def test_api_config():
    """测试 3：检查 API 配置"""
    print("\n" + "=" * 60)
    print("Test 3: API Configuration")
    print("=" * 60)

    client = NanoBananaClient()

    print(f"\nAPI Base: {client.api_base}")
    print(f"Thinking Model: {client.thinking_model}")
    print(f"Generation Model: {client.model}")
    print(f"API Key configured: {'Yes' if client.api_key else 'No'}")

    if not client.api_key:
        print("\n[WARN] NANO_BANANA_API_KEY not set, real API calls will fail")
    else:
        print(f"API Key (first 8 chars): {client.api_key[:8]}...")

    print("\n[PASS] API config test passed")


def test_real_analysis(image_path: str):
    """测试 4：真实 API 调用（需要有效的图片和 API Key）"""
    print("\n" + "=" * 60)
    print("Test 4: Real API Call")
    print("=" * 60)

    client = NanoBananaClient()

    if not client.api_key:
        print("\n[SKIP] Need NANO_BANANA_API_KEY")
        return

    if not Path(image_path).exists() and not image_path.startswith('http'):
        print(f"\n[SKIP] Image not found - {image_path}")
        return

    print(f"\nTest image: {image_path}")
    print("Calling Gemini Thinking API...")

    try:
        result = client.analyze_image_for_generation(
            image_path=image_path,
            mode="white_bg_topview",
            style_description=None
        )

        print("\n=== Analysis Result ===")
        print(f"  - Product type: {result.get('product_type', 'N/A')}")

        desc = result.get('visual_description', 'N/A')
        if len(desc) > 100:
            desc = desc[:100] + "..."
        print(f"  - Visual description: {desc}")

        print(f"  - Key features: {result.get('key_features', [])}")
        print(f"  - Generated prompt length: {len(result.get('generated_prompt', ''))}")
        print(f"  - Is fallback: {result.get('fallback', False)}")

        if result.get('generated_prompt'):
            prompt = result['generated_prompt']
            if len(prompt) > 200:
                prompt = prompt[:200] + "..."
            print(f"\n=== Generated Prompt (preview) ===")
            print(f"  {prompt}")

        print("\n[PASS] Real API call test passed")

    except Exception as e:
        print(f"\n[FAIL] API call failed: {e}")


def main():
    print("\n" + "=" * 60)
    print("Two-Stage AI Flow Test")
    print("=" * 60)

    # 基础测试（不需要 API）
    test_analysis_prompt()
    test_fallback()
    test_api_config()

    # 如果提供了图片路径，进行真实 API 测试
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        test_real_analysis(image_path)
    else:
        print("\n" + "-" * 60)
        print("TIP: To test real API call, provide an image path:")
        print("   python test_two_stage.py /path/to/image.jpg")
        print("   python test_two_stage.py https://example.com/image.jpg")

    print("\n" + "=" * 60)
    print("[DONE] All basic tests completed")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
