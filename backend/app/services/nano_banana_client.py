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
        self.thinking_model = settings.gemini_thinking_model

        if not self.api_key:
            logger.warning("NANO_BANANA_API_KEY not set. Image generation will fail.")

    def _encode_image_to_base64(self, image_path: str) -> str:
        """
        將圖片編碼為 base64

        支持：
        - 本地文件路徑
        - HTTP/HTTPS URL（從 R2 使用 boto3 SDK 下載）
        """
        try:
            # 檢測是否為 URL
            if image_path.startswith(('http://', 'https://')):
                # 從 R2 下載圖片（使用 StorageService）
                logger.info(f"Downloading image from R2: {image_path}")

                # 從完整 URL 提取 R2 Key
                # URL 格式：https://.../bucket-name/path/to/file.jpg
                # 需要提取 path/to/file.jpg
                storage = get_storage()
                if settings.use_r2_storage and settings.r2_public_url in image_path:
                    # 提取相對路徑（移除 public_url_base）
                    r2_key = image_path.replace(f"{settings.r2_public_url}/", "")
                    logger.info(f"Extracted R2 key: {r2_key}")

                    # 使用 boto3 從 R2 下載
                    response = storage.s3_client.get_object(
                        Bucket=storage.bucket,
                        Key=r2_key
                    )
                    image_data = response['Body'].read()
                    logger.info(f"Downloaded {len(image_data)} bytes from R2")
                else:
                    # 其他 URL（非 R2），使用 HTTP 下載
                    logger.info(f"Downloading from external URL: {image_path}")
                    response = httpx.get(image_path, timeout=30.0)
                    response.raise_for_status()
                    image_data = response.content
            else:
                # 本地文件路徑
                logger.info(f"Reading local image: {image_path}")
                with open(image_path, "rb") as image_file:
                    image_data = image_file.read()

            return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            raise

    # ==================== 第一階段：AI 圖片分析 ====================

    def analyze_image_for_generation(
        self,
        image_path: str,
        mode: str,
        style_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        使用 Gemini Thinking 模型分析圖片並生成定制化 prompt

        Args:
            image_path: 輸入圖片路徑（本地或 R2 URL）
            mode: 生成模式 (white_bg_topview / professional_photo)
            style_description: 用戶提供的風格描述（可選）

        Returns:
            {
                "visual_description": "圖片的視覺描述",
                "generated_prompt": "生成的定制化 prompt",
                "product_type": "檢測到的產品類型"
            }
        """
        try:
            # 編碼圖片為 base64
            encoded_image = self._encode_image_to_base64(image_path)
            logger.info(f"Analyzing image: {image_path}, mode: {mode}")

            # 構建分析 prompt
            analysis_prompt = self._build_analysis_prompt(mode, style_description)

            # 調用 Gemini Thinking API
            response = self._call_thinking_api(encoded_image, analysis_prompt)

            # 解析響應
            result = self._parse_analysis_response(response, mode, style_description)

            logger.info(f"Image analysis completed. Product type: {result.get('product_type', 'unknown')}")
            return result

        except Exception as e:
            logger.error(f"Failed to analyze image {image_path}: {e}", exc_info=True)
            # 分析失敗時返回默認結果，使用原有的硬編碼 prompt
            return self._get_fallback_analysis(mode, style_description)

    def _build_analysis_prompt(self, mode: str, style_description: Optional[str] = None) -> str:
        """構建圖片分析 prompt - 日本高級食材電商海報風格"""

        # 用戶自定義風格（如有）
        style_info = f"\n\nUSER STYLE REQUEST: {style_description}" if style_description else ""

        return f"""You are an elite E-Commerce Art Director specializing in premium Japanese gourmet (日本高級食材) product key visuals, inspired by top-tier Japanese department store food halls (デパ地下), kaiseki photography, and refined washoku aesthetics.

GOAL:
Analyze the input image and output ONE final generation prompt (English description) that keeps the product faithful and upgrades it into a luxury Japanese gourmet e-commerce poster with elegant graphic typography.

CRITICAL RULES (must follow):
1) Product fidelity: do NOT redesign product/label/colors/shape/branding; preserve visible Japanese text, materials, textures, and proportions exactly.
2) Mandatory packaging: if any packaging appears in the input, include it clearly in the final shot together with the product contents (full set).
3) Floating graphic overlay (must be 2D on-top overlay): add a floating marketing graphic banner/badge/label that sits ABOVE the photo (not printed on packaging, not a physical prop).
4) Overlay text content must be Traditional Chinese only (繁體中文). No English words in overlay.
5) Place "logo.png" at the bottom-right corner with safe margin; flat vector graphics style, high opacity, undeformed, do not recolor, visually distinct from packaging. You may add a very subtle neutral shadow behind it ONLY to separate from background (no glow, no outline).
6) Output ONLY the final prompt string, end with: --ar 1:1

JAPANESE FOOD CATEGORY PRESENTATION (choose based on product type):

【鮮魚・海鮮 Sashimi/Seafood】
- Whole fish: show on cedar/hinoki board with one sashimi-cut portion arranged beside it; add bamboo leaves (笹の葉) as accent.
- Sashimi blocks (柵): display block with 3-5 slices cut and fanned elegantly; include daikon tsuma garnish and wasabi accent.
- Shellfish/Uni/Ikura: show in original container plus a portion presented in a small ceramic dish or wooden masu box.
- Dried seafood (干物/珍味): keep original packaging upright; arrange loose pieces on washi paper or small ceramic plate.

【肉類 Premium Meat】
- Wagyu/beef block: show whole piece with one thick slice cut revealing marbling (霜降り); add premium steak knife.
- Shabu-shabu/sukiyaki slices: fan out slices elegantly on black or earth-tone ceramic plate; show original tray packaging behind.
- Specialty cuts (タン/ホルモン/レバー): display on traditional cast-iron plate or wooden board with rock salt accent.

【加工食品 Processed/Preserved】
- Dried goods (昆布/鰹節/乾物): keep original packaging; scatter loose product artfully on natural wood surface.
- Pickles (漬物): show jar/package with portion served in small ceramic dish (豆皿).
- Mentaiko/Tarako: display in original wooden box with one piece lifted to show texture.

【調味料 Seasonings/Condiments】
- Soy sauce/Miso/Dashi: show original bottle/container prominently; add small ceramic dish with product poured/scooped.
- Specialty oils/vinegars: elegant pour shot or bottle with condensation; add droplet on spoon.

【和菓子・甘味 Japanese Sweets】
- Wagashi: keep original box; arrange 2-3 pieces on black lacquer tray or ceramic plate.
- Packaged snacks: original packaging upright; pile contents generously in foreground.

【酒類 Japanese Beverages】
- Sake/Shochu: original bottle with traditional ceramic cup (お猪口/ぐい呑み) filled; add water droplets on bottle.
- Japanese whisky: bottle with crystal glass; one large ice sphere.

JAPANESE AESTHETIC DIRECTION (enforce consistently):

Lighting:
- Soft, warm key light (3200K-4000K) suggesting high-end izakaya or kaiseki atmosphere
- Gentle diffused shadows; avoid harsh contrast
- Subtle rim light to separate product from background

Background/Surface:
- Primary: aged hinoki wood, dark walnut, or charcoal slate
- Secondary: natural linen cloth (麻布), washi paper texture, or muted ceramic tile
- Accent props (minimal): seasonal leaf (maple/bamboo/shiso), small ceramic dish, chopstick rest
- Keep backgrounds uncluttered; product is the hero

Color Palette:
- Dominant: warm wood tones, charcoal, deep indigo, moss green
- Accent: subtle gold foil, vermillion red (朱色) used sparingly
- Avoid: bright primary colors, neon, pure white backgrounds

TYPOGRAPHY & OVERLAY DESIGN (Japanese luxury aesthetic):

Font Selection (AI chooses based on product mood):
- Headline: Refined Mincho-style serif (明朝体) — elegant, editorial, never heavy
- Supporting: Clean Gothic sans (ゴシック体) — light weight, generous tracking
- Badge/Seal: May use tasteful calligraphy ONLY if extremely refined (no brush-stroke mess)
- Forbidden: cheap brush fonts, rounded fonts, bubble text, heavy outlines, plastic bevel, WordArt effects

Overlay Material Aesthetic:
- Washi paper texture with subtle fiber visibility
- Gold foil stamping (箔押し) — thin lines only, never heavy fills
- Letterpress emboss effect — extremely subtle
- Delicate drop shadow — soft, short distance

Layout Archetype (choose ONE that fits negative space):
A) 「掛軸風」Hanging scroll header — horizontal banner at top, centered or left-aligned
B) 「短冊風」Vertical tag — slim vertical label on left or right edge
C) 「題字＋落款」Headline + seal badge — main text top area, small round seal (落款風) at upper corner

Layout Rules:
- Total overlay area: 10%-18% of frame
- Never cover the product; use negative space only
- Reserve bottom-right strictly for logo.png
- Maintain generous safe margins (minimum 5% from edges)

TRADITIONAL CHINESE COPY GUIDELINES (AI generates):

Main Headline (4-10 characters):
- Premium, refined tone; evoke quality/craftsmanship/seasonality
- Good examples: 「匠心嚴選」「旬之美味」「料亭風味」「職人手作」「鮮度直送」
- Avoid: slang, emojis, exaggerated claims

Supporting Line (8-18 characters):
- Safe, truthful benefit statement about taste/texture/quality/gift-worthiness
- Good examples: 「細緻油花 入口即化」「傳承百年 醇厚回甘」「嚴選素材 品質保證」
- Forbidden: medical/health claims, superlatives (最/第一/100%), unverified origin claims

Optional Badge (2-4 characters, only if appropriate):
- 「嚴選」「限定」「人氣」「推薦」「熱賣」「珍味」
- Use maximum ONE badge; place as small seal element

ANTI-FAILSAFE CHECKLIST:
✗ No extra brands/logos besides original packaging and bottom-right logo.png
✗ No warping or recoloring of original Japanese packaging text
✗ Overlay must NOT appear printed on packaging — clearly separate 2D layer
✗ No watermarks, QR codes, English words in overlay, random decorative patterns
✗ No cheap/tacky visual effects (glow, heavy outline, gradient fills, plastic texture)
✗ No overcrowded composition — maintain breathing room (余白の美){style_info}

FINAL OUTPUT FORMAT:
Return your analysis as valid JSON:
```json
{{
    "visual_description": "對圖片的詳細中文描述（50-100字）",
    "product_type": "產品類型（如：和牛、海鮮、調味料、和菓子等）",
    "detected_category": "Category from above list (e.g., Premium Meat, Sashimi/Seafood, etc.)",
    "key_features": ["特徵1", "特徵2", "特徵3"],
    "suggested_headline": "建議的繁體中文標題（4-10字）",
    "suggested_subline": "建議的繁體中文副標題（8-18字）",
    "generated_prompt": "The final English prompt describing: [faithful product + packaging] + [category-specific presentation with props] + [Japanese aesthetic lighting & surface] + [elegant thin border or washi frame] + [overlay archetype + Traditional Chinese text content] + [bottom-right logo.png requirement]. End with: --ar 1:1"
}}
```"""

    def _call_thinking_api(self, encoded_image: str, prompt: str) -> Dict[str, Any]:
        """調用 Gemini Thinking API 進行圖片分析"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 構建 Chat Completions 請求（帶圖片）
        payload = {
            "model": self.thinking_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }

        logger.info(f"Calling Gemini Thinking API with model: {self.thinking_model}")

        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.api_base}/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            return response.json()

    def _parse_analysis_response(
        self,
        response: Dict[str, Any],
        mode: str,
        style_description: Optional[str]
    ) -> Dict[str, Any]:
        """解析 AI 分析響應"""
        import json
        import re

        try:
            # 提取 AI 回覆內容
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not content:
                logger.warning("Empty response from Thinking API")
                return self._get_fallback_analysis(mode, style_description)

            # 嘗試從回覆中提取 JSON
            # 支持 ```json ... ``` 格式和純 JSON
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 嘗試直接解析整個內容
                json_str = content

            # 解析 JSON
            result = json.loads(json_str)

            # 驗證必要欄位
            if "generated_prompt" not in result:
                logger.warning("Missing generated_prompt in response")
                return self._get_fallback_analysis(mode, style_description)

            return {
                "visual_description": result.get("visual_description", ""),
                "product_type": result.get("product_type", "unknown"),
                "detected_category": result.get("detected_category", ""),
                "key_features": result.get("key_features", []),
                "suggested_headline": result.get("suggested_headline", ""),
                "suggested_subline": result.get("suggested_subline", ""),
                "generated_prompt": result["generated_prompt"],
                "raw_response": content  # 保留原始響應用於調試
            }

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from response: {e}")
            logger.debug(f"Raw content: {content[:500]}")
            return self._get_fallback_analysis(mode, style_description)

    def _get_fallback_analysis(self, mode: str, style_description: Optional[str]) -> Dict[str, Any]:
        """分析失敗時的降級方案，使用原有的硬編碼 prompt"""
        logger.info("Using fallback analysis with default prompt")

        if mode == "white_bg_topview":
            prompt = self._build_white_bg_prompt(None)
        else:
            prompt = self._build_professional_photo_prompt(style_description, None)

        return {
            "visual_description": "AI 分析未能完成，使用默認設置",
            "product_type": "unknown",
            "key_features": [],
            "generated_prompt": prompt,
            "fallback": True
        }

    # ==================== 第二階段：圖片生成 ====================

    def generate_white_bg_topview(
        self,
        input_images: List[str],
        product_analysis: Optional[Dict[str, Any]] = None,
        num_outputs: int = 1
    ) -> Dict[str, Any]:
        """
        生成白底 TopView 正面圖

        Args:
            input_images: 輸入圖片路徑列表（最多 5 張）
            product_analysis: Google Vision AI 分析結果（可選）
            num_outputs: 每張輸入圖片生成的輸出數量

        Returns:
            API 響應字典
        """
        # 構建 prompt
        prompt = self._build_white_bg_prompt(product_analysis)

        # 調用 API
        return self._call_api(
            input_images=input_images,
            prompt=prompt,
            num_outputs=num_outputs
        )

    def generate_professional_photos(
        self,
        input_images: List[str],
        style_description: Optional[str] = None,
        product_analysis: Optional[Dict[str, Any]] = None,
        num_outputs: int = 3
    ) -> Dict[str, Any]:
        """
        生成專業美食攝影圖

        Args:
            input_images: 輸入圖片路徑列表（最多 5 張）
            style_description: 用戶提供的風格描述
            product_analysis: Google Vision AI 分析結果（可選）
            num_outputs: 每張輸入圖片生成的輸出數量

        Returns:
            API 響應字典
        """
        # 構建 prompt
        prompt = self._build_professional_photo_prompt(style_description, product_analysis)

        # 調用 API
        return self._call_api(
            input_images=input_images,
            prompt=prompt,
            num_outputs=num_outputs
        )

    def _build_white_bg_prompt(self, product_analysis: Optional[Dict[str, Any]] = None) -> str:
        """構建白底圖 prompt（針對 HKTVmall 電商、日本食品優化）"""
        base_prompt = """Create a professional e-commerce product photograph optimized for Hong Kong online marketplace (HKTVmall standard) with these exact specifications:

BACKGROUND REQUIREMENTS - STRICT:
- Pure white background (RGB 255, 255, 255) - absolutely no variations
- Zero shadows, gradients, textures, or any background elements
- Perfectly clean and uniform across entire frame
- No floor or surface visible - product appears to float
- Clinical white studio environment

PRODUCT POSITIONING - TOP VIEW STANDARD:
- Strict 90-degree bird's eye view (directly overhead)
- Product perfectly centered in frame with equal margins
- Maintain product's authentic shape, proportions, and dimensions
- Natural arrangement (not artificially styled)
- If multiple pieces: organized neatly but authentically

LIGHTING SETUP - FOOD OPTIMIZED:
- Soft, diffused overhead lighting (mimics professional lightbox)
- Even illumination with no harsh shadows or hotspots
- Gentle directional light from 12 o'clock position
- Preserve natural colors accurately (no color cast)
- Highlight surface textures and details clearly
- Slight specular highlights on glossy surfaces (soy sauce, oil, packaging)

FOOD TEXTURE & DETAIL EMPHASIS - CRITICAL:
For Japanese food products, capture these micro-details:
- Rice grains: Individual grain definition, natural sheen, slight moisture
- Fish/Seafood: Marbling texture, natural color variation, fresh appearance
- Noodles: Individual strand separation, texture patterns, natural curves
- Sauces: Glossy sheen, viscosity indicators, natural pooling
- Packaging: Label clarity, material texture (plastic sheen, paper matte)
- Freshness indicators: Natural condensation, slight imperfections, organic irregularities

AUTHENTICITY & REALISM - ANTI-AI:
- Photo-realistic textures (avoid AI-smooth, over-perfect look)
- Preserve natural imperfections: slight asymmetry, minor irregularities
- Realistic product physics: natural stacking, authentic arrangement
- True-to-life colors (avoid oversaturation or artificial enhancement)
- Visible micro-details that prove authenticity
- Natural material properties: matte vs glossy surfaces accurately rendered

HONG KONG E-COMMERCE OPTIMIZATION:
- Meet HKTVmall product image standards
- Clean, professional presentation appealing to HK consumers
- Show product clearly for online purchase decision
- Accurate color representation for customer expectations
- Suitable for mobile device viewing (clear even when scaled down)

CONSISTENCY CONTROL - BRAND STANDARDS:
- Maintain identical lighting setup (color temperature: 5500K daylight neutral)
- Consistent perspective angle (90° top-down, no variation)
- Uniform background white level (RGB 255,255,255 exact)
- Same product-to-frame ratio across generations
- Predictable and repeatable style for product catalog uniformity

TECHNICAL SPECIFICATIONS:
- High resolution suitable for zoom functionality
- Sharp focus across entire product (infinite depth of field)
- No motion blur or softness
- Proper exposure: no clipped highlights or blocked shadows
- Professional product photography quality ready for commercial use

OUTPUT REQUIREMENTS:
- Single product image only
- Pure white background with no exceptions
- Top-down perspective maintained
- Clean, professional, catalog-ready
- Optimized for e-commerce platform display

REFERENCE STANDARD:
- HKTVmall professional product photography
- Wellcome, ParknShop online grocery photography
- Don Don Donki product catalog style
- Meets Hong Kong consumer expectations for online food shopping"""

        # 如果有產品分析，添加產品特徵描述和針對性指引
        if product_analysis and "labels" in product_analysis:
            labels = product_analysis["labels"][:5]  # 取前 5 個標籤
            product_desc = ", ".join(labels)
            base_prompt += f"\n\nSPECIFIC PRODUCT CATEGORY: {product_desc}"
            base_prompt += "\nApply appropriate texture rendering and detail emphasis based on this product type."
            base_prompt += "\nEnsure all visual characteristics match authentic product photography for this category."

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

    def _call_api_single(
        self,
        input_images: List[str],
        prompt: str,
        aspect_ratio: str = "1:1"
    ) -> Dict[str, Any]:
        """
        調用 Nano-Banana API（單次調用，生成 1 張圖片）

        Args:
            input_images: 輸入圖片路徑列表（參考圖）
            prompt: 生成 prompt
            aspect_ratio: 圖片比例（1:1, 4:3, 3:4, 16:9, 9:16 等）

        Returns:
            API 響應（包含 1 張圖片）
        """
        try:
            # 編碼圖片為 base64
            encoded_images = [
                self._encode_image_to_base64(img_path)
                for img_path in input_images
            ]

            # 構建請求 payload（根據 API 文檔）
            # 關鍵修正：
            # 1. 參數名是 "image"（單數），不是 "images"
            # 2. API 不支持 "n" 參數，每次只生成 1 張
            payload = {
                "model": self.model,
                "prompt": prompt,
                "image": encoded_images,  # ✅ 正確：使用 "image" 而不是 "images"
                "aspect_ratio": aspect_ratio,
                "response_format": "b64_json"
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Calling Nano-Banana API with {len(encoded_images)} reference images")
            logger.info(f"Prompt length: {len(prompt)} chars")

            # 發送請求
            with httpx.Client(timeout=180.0) as client:  # 增加超時時間
                response = client.post(
                    f"{self.api_base}/images/generations",
                    json=payload,
                    headers=headers
                )

                response.raise_for_status()
                response_data = response.json()

                # 調試日志
                logger.info(f"API response keys: {list(response_data.keys())}")
                if "data" in response_data:
                    logger.info(f"Number of images in response: {len(response_data['data'])}")
                    if response_data["data"]:
                        logger.info(f"First item keys: {list(response_data['data'][0].keys())}")

                return response_data

        except httpx.HTTPStatusError as e:
            logger.error(f"Nano-Banana API HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"API request failed: {e.response.text}")
        except Exception as e:
            logger.error(f"Nano-Banana API error: {str(e)}")
            raise Exception(f"Image generation failed: {str(e)}")

    def _call_api(
        self,
        input_images: List[str],
        prompt: str,
        num_outputs: int = 1
    ) -> Dict[str, Any]:
        """
        調用 Nano-Banana API（多次調用以生成多張圖片）

        由於 API 不支持 n 參數，需要多次調用來生成多張圖片。
        每張輸入圖片會生成 num_outputs 張輸出圖片。

        Args:
            input_images: 輸入圖片路徑列表
            prompt: 生成 prompt
            num_outputs: 每張輸入圖片要生成的輸出數量

        Returns:
            合併的 API 響應（包含所有生成的圖片）
        """
        all_data = []

        # 對每張輸入圖片，生成 num_outputs 張圖片
        for img_idx, input_image in enumerate(input_images):
            logger.info(f"Processing input image {img_idx + 1}/{len(input_images)}: {input_image}")

            for output_idx in range(num_outputs):
                logger.info(f"  Generating output {output_idx + 1}/{num_outputs} for input image {img_idx + 1}")

                # 調用 API（使用單張輸入圖片）
                response = self._call_api_single(
                    input_images=[input_image],  # 單張輸入圖片
                    prompt=prompt,
                    aspect_ratio="1:1"
                )

                # 收集生成的圖片
                if "data" in response:
                    for item in response["data"]:
                        all_data.append(item)
                        logger.info(f"    Generated image {len(all_data)}")

        logger.info(f"Total generated images: {len(all_data)}")

        # 返回合併的響應
        return {
            "data": all_data,
            "model": self.model,
            "created": int(__import__('time').time())
        }

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
                        # 解碼 base64 圖片（加入防御性處理）
                        b64_string = item["b64_json"]

                        # 去除空白字符
                        b64_string = b64_string.strip()

                        # 檢測並移除 Data URL 前綴（如果存在）
                        # 格式：data:image/png;base64,<actual_base64>
                        if b64_string.startswith('data:'):
                            # 查找 base64 數據開始位置（逗號後面）
                            comma_index = b64_string.find(',')
                            if comma_index != -1:
                                b64_string = b64_string[comma_index + 1:]
                                logger.info(f"Removed Data URL prefix, new length: {len(b64_string)}")

                        # 修復 padding（base64 需要是 4 的倍數）
                        missing_padding = len(b64_string) % 4
                        if missing_padding:
                            b64_string += '=' * (4 - missing_padding)
                            logger.info(f"Added {4 - missing_padding} padding characters")

                        try:
                            image_data = base64.b64decode(b64_string)
                        except Exception as decode_error:
                            # 打印詳細錯誤信息用於調試
                            logger.error(f"Base64 decode failed for image {idx + 1}")
                            logger.error(f"Original length: {len(item['b64_json'])}")
                            logger.error(f"After processing length: {len(b64_string)}")
                            logger.error(f"First 100 chars: {b64_string[:100]}")
                            logger.error(f"Last 100 chars: {b64_string[-100:]}")
                            raise decode_error

                        # 生成相對路徑
                        relative_path = f"{output_dir}/generated_{idx + 1}.png"

                        # 使用 StorageService 保存
                        file_url = storage.save_file(
                            file_data=image_data,
                            file_path=relative_path
                        )

                        output_paths.append(file_url)
                        logger.info(f"Saved generated image {idx + 1}: {relative_path} ({len(image_data)} bytes)")

            if not output_paths:
                logger.error(f"No images generated. API response: {api_response}")
                raise Exception("No images were generated by the API")

            return output_paths

        except Exception as e:
            logger.error(f"Failed to save generated images: {e}")
            raise Exception(f"Failed to save images: {str(e)}")
