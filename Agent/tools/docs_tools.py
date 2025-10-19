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


def extract_info_from_docx_table(file_path):
    """
    只提取单元格内容，不加额外标注
    
    :param file_path: docx文件路径
    :return: 简洁的表格内容字符串
    """
    import os
    import zipfile
    
    if not os.path.exists(file_path):
        return {"text": f"error in reading {file_path}: 文件不存在"}
    
    try:
        # 直接尝试用宽容模式读取，忽略损坏的图片
        import xml.etree.ElementTree as ET
        
        result = []
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            if 'word/document.xml' not in zip_ref.namelist():
                return {"text": f"error in reading {file_path}: 不是有效的.docx文件"}
            
            xml_content = zip_ref.read('word/document.xml')
            root = ET.fromstring(xml_content)
            
            # 提取表格中的文本
            namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            for table in root.findall('.//w:tbl', namespaces):
                for row in table.findall('.//w:tr', namespaces):
                    for cell in row.findall('.//w:tc', namespaces):
                        cell_texts = cell.findall('.//w:t', namespaces)
                        cell_content = ''.join([t.text for t in cell_texts if t.text])
                        if cell_content.strip():
                            result.append(cell_content.strip())
        
        if not result:
            return {"text": f"error in reading {file_path}: 文档中没有找到表格内容"}
        
        return {"text": "\n".join(result)}
    
    except zipfile.BadZipFile:
        return {"text": f"error in reading {file_path}: 文件格式错误，不是有效的.docx文件"}
    except Exception as e:
        return {"text": f"error in reading {file_path}: {str(e)}"}




if __name__ == "__main__":
    print(str(extract_info_from_docx_table("gydl/入会申请书[2].docx")))