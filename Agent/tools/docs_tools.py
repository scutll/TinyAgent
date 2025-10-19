from docx import Document
import base64
from typing import List, Dict

def read_word_document(path: str) -> List[Dict]:
    """
    读取包含图片的Word文档,返回文本和图片的Base64编码内容,按顺序排列。

    Args:
        path (str): Word文档的路径。

    Returns:
        List[Dict]: 包含文本和图片Base64编码的列表,每个元素是{"type": "text", "text": ...}或{"type": "image_url", "image_url": {"url": ...}}。
    """
    doc = Document(path)
    contents = []
    
    # 遍历文档中的所有段落
    for paragraph in doc.paragraphs:
        # 添加段落文本
        if paragraph.text.strip():
            contents.append({"type": "text", "text": paragraph.text})
        
        # 检查段落中的图片
        for run in paragraph.runs:
            if run._element.xpath('.//a:blip'):
                for blip in run._element.xpath('.//a:blip'):
                    r_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    if r_id:
                        image_part = doc.part.related_parts[r_id]
                        image_bytes = image_part.blob
                        image_format = image_part.content_type.split('/')[-1]
                        base64_image = base64.b64encode(image_bytes).decode('utf-8')
                        image_url = f"data:image/{image_format};base64,{base64_image}"
                        contents.append({"type": "image_url", "image_url": {"url": image_url}})
    
    return contents


if __name__ == "__main__":
    print(read_word_document("docs/JavaHW20251015.docx"))