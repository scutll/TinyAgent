from docx import Document
import base64
from Agent.tools.Tools import Tool_
from Agent.prompts.tools_prompt import read_word_document_prompt, extract_info_from_docx_table_prompt
from typing import Any, List, Dict
import json

class read_word_document(Tool_):
    def __init__(self):
        super().__init__(read_word_document_prompt)
        
    def __call__(self, path: str, openai_schema=False) -> List[Dict]:
        """
        读取包含图片的Word文档,返回文本和图片的Base64编码内容,按顺序排列。
        文本部分会保留基本样式信息，并用字符串表示每个段落的键值对，方便传给LLM。

        Args:
            path (str): Word文档的路径。
            openai_schema (bool): 是否使用OpenAI schema输出。

        Returns:
            List[Dict]: 每个元素是文本或图片，文本为字符串化的键值对，图片为Base64。
        """
        doc = Document(path)
        contents = []
        para_id_counter = 0  # 段落唯一ID

        for paragraph in doc.paragraphs:
            # 拼接段落文本，保留段落内部换行
            paragraph_text = ""
            for run in paragraph.runs:
                paragraph_text += run.text  # 保留空格
                # 检查 run 内是否有换行符（Shift+Enter）
                if run._element.xpath('.//w:br'):
                    paragraph_text += "\n"
                else:
                    paragraph_text += " "

            if paragraph_text.strip():  # 非空段落才处理
                run_info = {
                    "para_id": para_id_counter,
                    "content": paragraph_text
                }
                para_id_counter += 1
                text_str = json.dumps(run_info, ensure_ascii=False)

                if openai_schema:
                    contents.append({"type": "input_text", "text": text_str})
                else:
                    contents.append({"type": "text", "text": text_str})

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
                            image_url= "image"
                            if openai_schema:
                                contents.append({"type": "input_image", "image_url": {"url": image_url}})
                            else:
                                contents.append({"type": "image_url", "image_url": {"url": image_url}})
                            from Agent.Core.agent_core import set_doc_with_imgs
                            set_doc_with_imgs()

        return contents
        
        
class extract_info_from_docx_table(Tool_):
    def __init__(self):
        super().__init__(extract_info_from_docx_table_prompt)
        
    def __call__(self, file_path):
        """
        只提取单元格内容，不加额外标注
        
        :param file_path: docx文件路径
        :return: 简洁的表格内容字符串
        """
        import os
        import zipfile
        
        if not os.path.exists(file_path):
            return f"error in reading {file_path}: file not found"
        
        try:
            # 直接尝试用宽容模式读取，忽略损坏的图片
            import xml.etree.ElementTree as ET
            
            result = []
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                if 'word/document.xml' not in zip_ref.namelist():
                    return f"error in reading {file_path}: not a valid .docx file"
                
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
                return f"error in reading {file_path}: no table content found in document"

            return "\n".join(result)
        
        except zipfile.BadZipFile:
            return f"error in reading {file_path}: file format error: not a valid .docx file"
        except Exception as e:
            return f"error in reading {file_path}: {str(e)}"
        
        
def extract_text_runs(path: str):
    """
    从Word文档中提取文本run，返回列表，每个元素是字符串化JSON，包含para_id和text
    """
    doc = Document(path)
    runs_list = []
    para_id_counter = 0

    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            if run.text.strip():
                run_info = {
                    "para_id": para_id_counter,
                    "text": run.text
                }
                runs_list.append(json.dumps(run_info, ensure_ascii=False))
                para_id_counter += 1

    return runs_list, para_id_counter  # 返回列表和当前最大para_id

def insert_text_runs(doc_path: str, insert_para_id: int, new_text: str):
    """
    将新文本插入到指定 para_id 的后面
    """
    doc = Document(doc_path)

    # 先提取文本run并定位 para_id 对应的run
    runs_list, max_para_id = extract_text_runs(doc_path)

    # 找到插入位置（para_id对应的run在runs_list中的索引）
    insert_index = None
    for i, run_str in enumerate(runs_list):
        run_info = json.loads(run_str)
        if run_info["para_id"] == insert_para_id:
            insert_index = i
            break

    if insert_index is None:
        raise ValueError(f"para_id {insert_para_id} 不存在")

    # 构造新run
    new_run_info = {
        "para_id": max_para_id,
        "text": new_text
    }

    # 插入到runs_list中
    runs_list.insert(insert_index + 1, json.dumps(new_run_info, ensure_ascii=False))

    return runs_list


        
if __name__ == "__main__":
    test_path = r'E:\D2L\Agent\TinyAgent\old_docs\test.docx'
    reader = read_word_document()
    print(reader.__call__(path=test_path))
    # print(extract_text_runs(test_path))