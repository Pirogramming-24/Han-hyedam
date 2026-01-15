from paddleocr import PaddleOCR
import cv2
import numpy as np
import os

class NutritionOCRService:
    """영양성분표 OCR 서비스"""
    
    def __init__(self):
        self.ocr = PaddleOCR(
            use_angle_cls=True, 
            lang='korean'
        )
    
    def preprocess_image(self, image_path):
        """이미지 전처리 - OCR 인식률 향상"""
        
        img = cv2.imread(image_path)
        
        if img is None:
            raise ValueError(f"이미지를 읽을 수 없습니다: {image_path}")
        
        # 1. 그레이스케일 변환
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. 가우시안 블러로 노이즈 제거
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # 3. 대비 향상 (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(blurred)
        
        # 4. 선명하게 (Sharpening)
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        # 5. 이진화 (Otsu's method)
        _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 전처리된 이미지 저장
        base, ext = os.path.splitext(image_path)
        processed_path = f"{base}_processed{ext}"
        cv2.imwrite(processed_path, binary)
        
        return processed_path
    
    def extract_text(self, image_path):
        """OCR 실행하여 텍스트 추출 (원본 + 전처리 병합)"""
        
        try:
            print(f"📸 이미지 경로: {image_path}")
            
            # 1차 시도: 원본 이미지
            print("🔍 1단계: 원본 이미지로 OCR 실행...")
            result_original = self.ocr.ocr(image_path, cls=True)
            
            texts_original = []
            if result_original and result_original[0]:
                for line in result_original[0]:
                    if line and len(line) > 1 and line[1]:
                        texts_original.append(line[1][0])
            
            full_text_original = ' '.join(texts_original)
            print(f"   ✓ 원본: {len(texts_original)}개 추출")
            
            # 2차 시도: 전처리 이미지
            print("🔍 2단계: 전처리 이미지로 OCR 실행...")
            processed_path = self.preprocess_image(image_path)
            result_processed = self.ocr.ocr(processed_path, cls=True)
            
            texts_processed = []
            if result_processed and result_processed[0]:
                for line in result_processed[0]:
                    if line and len(line) > 1 and line[1]:
                        texts_processed.append(line[1][0])
            
            full_text_processed = ' '.join(texts_processed)
            print(f"   ✓ 전처리: {len(texts_processed)}개 추출")
            
            # 전처리 이미지 삭제
            try:
                os.remove(processed_path)
            except:
                pass
            
            # 3. 더 많이 추출된 결과 선택
            if len(texts_processed) > len(texts_original):
                print(f"✅ 전처리 이미지 선택! ({len(texts_processed)} > {len(texts_original)})")
                final_text = full_text_processed
            else:
                print(f"✅ 원본 이미지 선택! ({len(texts_original)} >= {len(texts_processed)})")
                final_text = full_text_original
            
            print(f"📝 최종 텍스트: {final_text[:100]}...")
            
            return final_text
        
        except Exception as e:
            print(f"❌ OCR 에러: {e}")
            import traceback
            traceback.print_exc()
            return ""