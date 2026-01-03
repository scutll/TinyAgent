import base64
from io import BytesIO
import io
from pptx import Presentation
from PIL import Image
import json
from Agent.utils.img_filter import is_useful_image 
import os
from typing import Dict, List
from docx import Document
import pdfplumber
from Agent.utils.logging_ import log



#  上传图片给llm
def parse_image_file(path: str) -> Dict:
    """
    image: 图片文件路径，例如 'data/test.png'
    return: base64 编码后的字符串
    """
    if not os.path.exists(path):
        return {
                "success": False,
                "message": f"File not found: {path}",
                "output_path": None
            } 

    # 以二进制方式读取图片
    with open(path, "rb") as f:
        image_bytes = f.read()

    # 转成 base64
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    result = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
    return {
        "success": True,
        "message": f"File not found: {path}",
        "content": [result]
    }


def img_to_base64(page, img):
    """
    Convert a pdfplumber img object to a base64-encoded string
    """
    x0, top, x1, bottom = img["x0"], img["top"], img["x1"], img["bottom"]
    # Crop the image region from the PDF page
    im = page.crop((x0, top, x1, bottom)).to_image(resolution=150).original

    # Convert to in-memory binary stream
    buffer = BytesIO()
    im.save(buffer, format="PNG")
    buffer.seek(0)

    # Encode to base64 string
    img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    return img_base64


# 上传pdf文件给llm
def parse_pdf_file(pdf_path: str) -> Dict:
    """
    Extract PDF content (text + images) and return an ordered content list.
    Images are base64-encoded.
    
    Specifically, to prevent PDFs from failing to process due to a large number of tiny images, we filter out images with an area smaller than 5000 pixels and do not upload them.
    """

    content_list = []

    try:
        if not os.path.exists(pdf_path):
            return {
                "success": False,
                "message": f"File not found: {pdf_path}",
                "output_path": None
            }
        
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text_output = []
                try:
                    # Add page header
                    text_output.append(f"\n\n--- Page {i} ---\n\n")

                    # Extract main body text
                    page_text = page.extract_text()
                    if page_text:
                        text_output.append(page_text)

                    # Extract tables (if any)
                    tables = page.extract_tables()
                    for t_idx, table in enumerate(tables, start=1):
                        if not table:
                            continue
                        text_output.append(f"\n[Table {t_idx}]\n")
                        for row in table:
                            if row:  # avoid empty rows
                                row_text = "\t".join([cell if cell else "" for cell in row])
                                text_output.append(row_text)
                except Exception as e_page:
                    # One-page failure does not affect overall processing
                    text_output.append(f"\nFailed to parse page {i}: {e_page}\n")
                    continue
                text_content = "\n".join(text_output) if text_output else "no text extracted"
                
                content_list.append({
                    "type": "text",
                    "text": str(text_content)
                })
                
                # Images
                MIN_IMAGE_AREA = 5000
                for img_idx, img in enumerate(page.images[:10], start=1):
                    x0, top, x1, bottom = (
                        max(0, img["x0"]),
                        max(0, img["top"]),
                        min(img["x1"], page.width),
                        min(img["bottom"], page.height)
                    )
                    
                    width = x1 - x0
                    height = bottom - top
                    area = width * height

                    if area < MIN_IMAGE_AREA:
                        continue

                    # 更新 bbox
                    img["x0"], img["top"], img["x1"], img["bottom"] = x0, top, x1, bottom
                    
                    img_b64 = img_to_base64(page, img)
                    log(f"size of image: {len(img_b64)/1024} kb")
                    # Append directly to the content list
                    content_list.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}})
                    

        return {
            "success": True,
            "content": content_list
        }

    except Exception as e:
        return {
            "success": False,
            "content": f"❌Error in extraction: {e}"
        }
    

# 上传word给llm
def parse_word_file(path: str, openai_schema=False) -> Dict:
        """
        读取包含图片的Word文档,返回文本和图片的Base64编码内容,按顺序排列。

        Args:
            path (str): Word文档的路径。

        Returns:
            List[Dict]: 包含文本和图片Base64编码的列表,每个元素是{"type": "text", "text": ...}或{"type": "image_url", "image_url": {"url": ...}}。
        """
        if not os.path.exists(path):
            return {
            "success": False,
            "content": f"File not found: {path}"
        }
            
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
                            
                            from Agent.Core.agent_core import set_doc_with_imgs
                            set_doc_with_imgs()
        
        return {
            "success": True,
            "content": contents
        }
    
    
# 上传其他(txt、代码)文本文件
def parse_text_file(path) -> Dict:
    content = ""
    if not os.path.exists(path):
        return {
            "success": False,
            "content": f"File not found: {path}"
        }
        
    with open(path, 'r', encoding='utf-8') as F:
        content = F.read()
    
    result = {
        "type": "text",
        "text": content
    }
    return {
        "success": True,
        "content": [result]
    }


def parse_ppt_file(path) ->Dict:
    """
    读取PPT文件，按顺序提取文本与图片，返回结构化内容。
    图片将以 base64 形式返回，适合直接送入多模态模型。
    """
    
    if not os.path.exists(path):
        return {
            "success": False,
            "content": f"File not found: {path}"
        }
        
        
    
    prs = Presentation(path)
    contents = []
    text_id = 0

    for slide in prs.slides:
        for shape in slide.shapes:

            # ---------- 文本 ----------
            if hasattr(shape, "text") and shape.text.strip():
                text_obj = {
                    "para_id": text_id,
                    "content": shape.text.strip()
                }
                text_id += 1

                contents.append({
                    "type": "text",
                    "text": json.dumps(text_obj, ensure_ascii=False)
                })

            # ---------- 图片 ----------
            if shape.shape_type == 13:  # PICTURE
                try:
                    image = shape.image
                    image_bytes = image.blob
                    pil_img = Image.open(io.BytesIO(image_bytes))

                    is_bg = "background" in shape.name.lower()

                    if not is_useful_image(
                        pil_img,
                        image_bytes,
                        is_background=is_bg
                    ):
                        continue

                    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                    image_url = f"data:image/{image.ext};base64,{image_base64}"

                    contents.append({
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    })

                except Exception:
                    continue
    
    return {
        "success": True,
        "content": contents
    }


if __name__ == "__main__": 
    import Agent.Memory.container as ct
    memory = ct.MemoryContainer()
    
    # item = parse_text_file("docs/test.py")
    # print("item parsed!")
    # if item["success"]:
    #     item = item['content']
    # else:
    #     print("boom")
    #     exit()
    # memory._add_user_message(item)
    # from openai import OpenAI
    # client = OpenAI(
    #     api_key="",
    # )
    # completion = client.chat.completions.create(
    #     model='gpt-4.1',
    #     messages=memory(),
    #     stream=False,
    # )
    
    # # with(open("docs/test.txt", 'w')) as F:
    # #     F.write(str(item))
    # result = str(completion.choices[0].message.content)
    # print(result)
    result = parse_ppt_file("E:\D2L\Agent\TinyAgent\old_docs\议题1初稿.pptx")['content']
    # print(result)    