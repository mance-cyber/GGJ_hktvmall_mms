# =============================================
# Nano-Banana API 客戶端
# =============================================

import httpx
import base64
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from app.config import get_settings
from app.services.storage_service import get_storage

logger = logging.getLogger(__name__)
settings = get_settings()


class NanoBananaClient:
    """Nano-Banana (Gemini 2.5 Flash Image) API 客戶端"""

    def __init__(self):
        self.api_base = settings.nano_banana_api_base
        self.api_key = settings.nano_banana_api_key
        self.model = settings.nano_banana_model

        if not self.api_key:
            logger.warning("NANO_BANANA_API_KEY not set. Image generation will fail.")

    def _encode_image_to_base64(self, image_path: str) -> str:
        """將圖片編碼為 base64"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            raise

    def generate_white_bg_topview(
        self,
        input_images: List[str],
        product_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成白底 TopView 正面圖

        Args:
            input_images: 輸入圖片路徑列表（最多 5 張）
            product_analysis: Google Vision AI 分析結果（可選）

        Returns:
            API 響應字典
        """
        # 構建 prompt
        prompt = self._build_white_bg_prompt(product_analysis)

        # 調用 API
        return self._call_api(
            input_images=input_images,
            prompt=prompt,
            num_outputs=1
        )

    def generate_professional_photos(
        self,
        input_images: List[str],
        style_description: Optional[str] = None,
        product_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成專業美食攝影圖（2-3 張）

        Args:
            input_images: 輸入圖片路徑列表（最多 5 張）
            style_description: 用戶提供的風格描述
            product_analysis: Google Vision AI 分析結果（可選）

        Returns:
            API 響應字典
        """
        # 構建 prompt
        prompt = self._build_professional_photo_prompt(style_description, product_analysis)

        # 調用 API（生成 2-3 張）
        return self._call_api(
            input_images=input_images,
            prompt=prompt,
            num_outputs=3
        )

    def _build_white_bg_prompt(self, product_analysis: Optional[Dict[str, Any]] = None) -> str:
        """構建白底圖 prompt"""
        base_prompt = """Create a professional product photograph with these exact specifications:

BACKGROUND:
- Pure white background (RGB 255,255,255)
- No shadows, gradients, or textures
- Perfectly clean and uniform

PRODUCT POSITIONING:
- Top-view perspective (bird's eye view)
- Product centered in the frame
- Maintain product's natural shape and proportions

LIGHTING:
- Soft, even lighting
- No harsh shadows
- Highlight product details clearly

STYLE:
- E-commerce product photography standard
- High resolution and sharp details
- Professional studio quality

OUTPUT:
- Single product image
- White background only
- Top-down view"""

        # 如果有產品分析，添加產品特徵描述
        if product_analysis and "labels" in product_analysis:
            labels = product_analysis["labels"][:5]  # 取前 5 個標籤
            product_desc = ", ".join(labels)
            base_prompt += f"\n\nPRODUCT TYPE: {product_desc}"

        return base_prompt

    def _build_professional_photo_prompt(
        self,
        style_description: Optional[str],
        product_analysis: Optional[Dict[str, Any]] = None
    ) -> str:
        """構建專業攝影圖 prompt（針對日本食品、香港市場優化）"""
        base_prompt = """Create 3 premium Japanese food photography images optimized for Hong Kong market with these exact specifications:

VISUAL STYLE - JAPANESE CULINARY ARTISTRY:
- Emphasize "Shokunin" (職人) craftsmanship and attention to detail
- Capture the essence of Japanese aesthetics: simplicity, elegance, and precision
- Showcase ingredients' natural colors and textures authentically
- Color palette: Vibrant yet natural (avoid over-saturation)
- Temperature: Warm (2800K-3200K) for inviting, appetizing mood

COMPOSITION VARIETY:
Image 1 - HERO CLOSE-UP (主打特寫):
- Extreme close-up (macro lens effect) with selective focus
- Highlight textures: rice grains, fish marbling, noodle strands
- Shallow depth of field (f/1.8-2.8 bokeh effect)
- Focus on the most appetizing element
- Show steam, moisture, or freshness indicators

Image 2 - STYLED SCENE (情境美食):
- 45-degree angle overhead shot (Hong Kong Instagram style)
- Include complementary Japanese elements: chopsticks, ceramic plates, bamboo mat
- Clean, minimal background with subtle wood or stone textures
- Negative space for text overlay capability
- Props: authentic Japanese tableware, natural materials

Image 3 - EDITORIAL DRAMA (雜誌級構圖):
- Artistic angle with dramatic but natural lighting
- Side lighting with soft shadows (3/4 lighting setup)
- Show the full dish in context with atmospheric background
- Add depth with layered composition
- Professional food magazine quality

LIGHTING SPECIFICATIONS:
- Soft directional light (mimics natural window light)
- Key light at 45° angle from above
- Gentle fill light to preserve shadow details
- No harsh reflections or blown highlights
- Preserve color accuracy of ingredients

AUTHENTICITY & DETAILS:
- Photo-realistic textures (no AI-looking smoothness)
- Visible imperfections for authenticity (slight irregularities)
- Natural condensation, gloss, or sheen on appropriate surfaces
- Proper food physics (gravity, stacking, sauce flow)
- Micro-details visible in close-ups

HONG KONG MARKET OPTIMIZATION:
- Appeal to Hong Kong's sophisticated food culture
- Clean, modern aesthetic (avoid overly traditional or rustic)
- Instagram-ready composition (suitable for Stories and Feed)
- Premium positioning (高級感) without being unapproachable
- Color grading: Rich, appetizing, but true-to-life

BRAND CONSISTENCY:
- Maintain consistent color temperature across all 3 images
- Unified mood and atmosphere
- Same quality level for each composition
- Cohesive visual language suitable for brand campaigns

TECHNICAL REQUIREMENTS:
- High resolution (suitable for print and digital)
- Sharp focus on key elements
- Proper exposure with retained highlight and shadow details
- Professional retouching level (natural, not over-processed)
- Ready for immediate commercial use

OUTPUT STANDARDS:
- 3 distinct but complementary images
- Each image tells a different story but shares the same premium quality
- Suitable for: e-commerce, social media, advertising campaigns
- Industry standard: Michelin Guide / VOGUE / Kinfolk photography level"""

        # 添加用戶風格描述
        if style_description:
            base_prompt += f"\n\nCUSTOM STYLE DIRECTION: {style_description}"

        # 添加產品分析
        if product_analysis and "labels" in product_analysis:
            labels = product_analysis["labels"][:5]
            product_desc = ", ".join(labels)
            base_prompt += f"\n\nSPECIFIC PRODUCT: {product_desc}"
            base_prompt += "\nEnsure all visual elements align with this product category's characteristics."

        return base_prompt

    def _call_api(
        self,
        input_images: List[str],
        prompt: str,
        num_outputs: int = 1
    ) -> Dict[str, Any]:
        """
        調用 Nano-Banana API

        Args:
            input_images: 輸入圖片路徑列表
            prompt: 生成 prompt
            num_outputs: 輸出圖片數量

        Returns:
            API 響應
        """
        try:
            # 編碼圖片
            encoded_images = [
                self._encode_image_to_base64(img_path)
                for img_path in input_images
            ]

            # 構建請求 payload
            # 注意：這裡的格式可能需要根據實際 API 文檔調整
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": encoded_images,
                "n": num_outputs,
                "size": "1024x1024",  # 可調整
                "response_format": "b64_json"
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # 發送請求
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{self.api_base}/images/generations",  # 端點可能需要調整
                    json=payload,
                    headers=headers
                )

                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"Nano-Banana API HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"API request failed: {e.response.text}")
        except Exception as e:
            logger.error(f"Nano-Banana API error: {str(e)}")
            raise Exception(f"Image generation failed: {str(e)}")

    def save_generated_images(
        self,
        api_response: Dict[str, Any],
        output_dir: str
    ) -> List[str]:
        """
        保存生成的圖片（使用 StorageService）

        Args:
            api_response: API 響應
            output_dir: 輸出目錄相對路徑（例如：generated/task-123）

        Returns:
            保存的圖片 URL/路徑列表
        """
        output_paths = []
        storage = get_storage()

        try:
            # 提取並保存圖片
            # 注意：響應格式可能需要根據實際 API 調整
            if "data" in api_response:
                for idx, item in enumerate(api_response["data"]):
                    if "b64_json" in item:
                        # 解碼 base64 圖片
                        image_data = base64.b64decode(item["b64_json"])

                        # 生成相對路徑
                        relative_path = f"{output_dir}/generated_{idx + 1}.png"

                        # 使用 StorageService 保存
                        file_url = storage.save_file(
                            file_data=image_data,
                            file_path=relative_path
                        )

                        output_paths.append(file_url)
                        logger.info(f"Saved generated image: {relative_path}")

            return output_paths

        except Exception as e:
            logger.error(f"Failed to save generated images: {e}")
            raise Exception(f"Failed to save images: {str(e)}")
