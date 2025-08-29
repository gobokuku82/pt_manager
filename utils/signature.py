"""
서명 처리 유틸리티
"""

import base64
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import io
import qrcode
import streamlit as st

class SignatureProcessor:
    """서명 처리 클래스"""
    
    @staticmethod
    def generate_signature_link(contract_id: str, base_url: Optional[str] = None) -> Dict[str, str]:
        """서명 링크 생성"""
        token = str(uuid.uuid4())
        
        if not base_url:
            base_url = st.secrets.get("BASE_URL", "http://localhost:8501")
        
        sign_url = f"{base_url}/sign?token={token}"
        
        return {
            "token": token,
            "url": sign_url,
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
    
    @staticmethod
    def generate_qr_code(url: str) -> bytes:
        """QR 코드 생성"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 바이트로 변환
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
    
    @staticmethod
    def process_signature_image(canvas_data) -> str:
        """캔버스 데이터를 base64 이미지로 변환"""
        if canvas_data is None:
            return ""
        
        # PIL 이미지로 변환
        img = Image.fromarray(canvas_data.astype('uint8'), 'RGBA')
        
        # 투명 배경을 흰색으로 변경
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3] if len(img.split()) > 3 else None)
        
        # base64로 인코딩
        buffer = io.BytesIO()
        background.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def add_watermark(signature_data: str, text: str) -> str:
        """서명 이미지에 워터마크 추가"""
        # base64 디코딩
        if signature_data.startswith('data:image'):
            signature_data = signature_data.split(',')[1]
        
        img_data = base64.b64decode(signature_data)
        img = Image.open(io.BytesIO(img_data))
        
        # 워터마크 추가
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # 텍스트 추가 (우측 하단)
        try:
            # 기본 폰트 사용
            font = ImageFont.load_default()
        except:
            font = None
        
        text_color = (200, 200, 200)  # 연한 회색
        draw.text((10, height - 20), text, fill=text_color, font=font)
        
        # 다시 base64로 인코딩
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def validate_signature(signature_data: str) -> bool:
        """서명 데이터 유효성 검사"""
        if not signature_data:
            return False
        
        if not signature_data.startswith('data:image'):
            return False
        
        try:
            # base64 디코딩 테스트
            data = signature_data.split(',')[1]
            base64.b64decode(data)
            return True
        except:
            return False
    
    @staticmethod
    def create_signature_pdf(contract_content: str, signature_data: str, 
                           signer_info: Dict) -> bytes:
        """서명된 계약서 PDF 생성"""
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
        
        # PDF 버퍼 생성
        buffer = io.BytesIO()
        
        # PDF 문서 생성
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # 제목
        title = Paragraph("PT 계약서", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # 계약서 내용
        for line in contract_content.split('\n'):
            if line.strip():
                p = Paragraph(line, styles['Normal'])
                story.append(p)
                story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 20))
        
        # 서명 정보
        sign_info = f"서명자: {signer_info.get('name', '')}<br/>"
        sign_info += f"서명일: {signer_info.get('signed_at', '')}<br/>"
        sign_info += f"전화번호: {signer_info.get('phone', '')}"
        
        p = Paragraph(sign_info, styles['Normal'])
        story.append(p)
        story.append(Spacer(1, 20))
        
        # 서명 이미지 추가
        if signature_data and signature_data.startswith('data:image'):
            try:
                # base64 이미지를 PIL 이미지로 변환
                img_data = signature_data.split(',')[1]
                img_bytes = base64.b64decode(img_data)
                img = Image.open(io.BytesIO(img_bytes))
                
                # 임시 버퍼에 저장
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                # ReportLab 이미지로 추가
                rl_img = RLImage(img_buffer, width=200, height=100)
                story.append(rl_img)
            except Exception as e:
                print(f"서명 이미지 추가 실패: {e}")
        
        # PDF 생성
        doc.build(story)
        
        # 버퍼 내용 반환
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data

def generate_signature_link(contract_id: str, base_url: Optional[str] = None) -> str:
    """서명 링크 생성 헬퍼 함수"""
    processor = SignatureProcessor()
    result = processor.generate_signature_link(contract_id, base_url)
    return result['url']