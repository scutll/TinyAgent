# the core agent part 
# it does not contains the model directly, but the pipeline does for it 
# the agent_core is deployed in user's system, and the Model deployed in the server. agent_core uploads input and gets reply streamly from server

from pathlib import Path
import shutil
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RESET = "\033[0m"

from Agent.request.api import api,structured_response, agentOutputFields
from Agent.prompts.prompt_react import prompt_react
from Agent.prompts.tools_prompt import *

from Agent.Memory.container import MemoryContainer
from Agent.Memory.compression import memory_compress__
from Agent.request.api import *
from Agent.utils.parser import parse_response
from Agent.utils.logging_ import log
from Agent.utils.config import get_configured_model
from Agent.utils.multimodal import (
    parse_image_file,
    parse_pdf_file,
    parse_text_file,
    parse_word_file,
    parse_ppt_file
)

def _select_parser(suffix: str):
        if suffix in IMAGE_EXTS:
            return parse_image_file
        if suffix in PDF_EXTS:
            return parse_pdf_file
        if suffix in WORD_EXTS:
            return parse_word_file
        if suffix in PPT_EXTS:
            return parse_ppt_file
        return parse_text_file


# 导入工具
from Agent.tools.Tools import ToolsContainer
import Agent.tools.File_tools as ft
import Agent.tools.System_tools as st
import Agent.tools.Web_tools as wt
import Agent.tools.docs_tools as dt
import Agent.tools.inquery_tool as it
from Agent.prompts.tools_prompt import Finish_prompt 
tools = ToolsContainer()
Tools = [it.talk_with_user(),
         ft.create_file(), ft.read_file(), ft.search_replace(),
         st.delete_dir(), st.delete_file(), st.get_absolute_cur_path(), st.tree_file(), st.execute_command(),
         dt.read_word_document(), dt.extract_info_from_docx_table(),
         wt.fetch_webpage_with_selector(), wt.fetch_webpage()]
tools.load_tool(Tools)
docs_with_imgs = False  # 当read_word_document读取的内容有image时设为true，这时禁止使用structured output

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
WORD_EXTS = {".docx"}
PDF_EXTS = {".pdf"}
PPT_EXTS = {".ppt", ".pptx"}

def set_doc_with_imgs():
    global docs_with_imgs
    docs_with_imgs = True
    log("[Warning] Docs extracted with images! Structured LLM Output prohibited!")

# 初始化conversation(Memory)

system_prompt = prompt_react 
all_tools_prompt = tools.prompt_all_tools + Finish_prompt


class AgentCore:
    def __init__(self, model: Optional[str] = None):
        self.input = None
        self._sticky_model = model is not None
        if model is None:
            try:
                model = get_configured_model()
            except ValueError:
                model = "doubao-seed-1-6-thinking-250715"
        self.model = model
        self.UseModel = model
        # 保存解析成功的文件内容: {abs_path: [content_blocks]}
        self.files: Dict[str, List[Dict[str, Any]]] = {}
        
        self.Memory = MemoryContainer()
        self.Memory._add_system_prompt(system_prompt)
        self.Memory._add_tool_prompt(tool_prompt=all_tools_prompt)

    def refresh_model(self, force: bool = False) -> None:
        if self._sticky_model and not force:
            return
        try:
            configured = get_configured_model()
        except ValueError:
            return
        if configured and configured != self.model:
            self.model = configured
            self.UseModel = configured
        
    def _invoke_model(self, message: Union[str, list]) -> Any:
        self.refresh_model()
        alias = (self.model or "").lower()

        if "gpt" in alias or alias in {"openai"}:
            handler = api.get("gpt")
        elif "doubao" in alias:
            handler = api.get("Doubao") if docs_with_imgs else api.get("structured")
        else:
            handler = api.get("structured") if not docs_with_imgs else api.get("Doubao")

        if handler is None:
            raise RuntimeError("No available API handler for current configuration")
        return handler(message, self.Memory)


    def set_input(self, input: str):
        self.input = input
        
        
    def reset_conversation__(self):
        self.Memory.reset__()
        self.Memory._add_system_prompt(system_prompt)
        # print("conversation reset!")
        
    def load_conv(self, filename):
        self.Memory._load_conversation(filename)
        
        
    def compress_context__(self):
        print(len(self.Memory.tool_prompt["content"]), len(self.Memory.system_prompt["content"]), len(self.Memory.conversation))
        compressed_context = memory_compress__(self.Memory)
        self.Memory.reset__()
        self.Memory._add_tool_prompt(all_tools_prompt)
        self.Memory._add_system_prompt(system_prompt)
        self.Memory._add_assistant_message(compressed_context)
        
        


    def _relativize(self, file_path: Path, rel_base: Optional[Path]) -> str:
        if rel_base is None:
            return file_path.name
        try:
            return str(file_path.relative_to(rel_base))
        except ValueError:
            return file_path.name

    def _process_file_paths(
        self,
        file_paths: Iterable[Path],
        rel_base: Optional[Path] = None,
    ) -> List[Path]:
        """解析文件并按绝对路径记录内容。

        self.files 的 key 为文件的绝对路径字符串，
        这样 main 中上传/删除都可以直接用同一地址表示同一个文件。
        """
        aggregated: Dict[str, List[Dict[str, Any]]] = {}
        processed: List[Path] = []

        for file_path in file_paths:
            if not file_path.exists() or not file_path.is_file():
                log(f"[upload_files] skip missing entry: {file_path}")
                continue

            parser = _select_parser(file_path.suffix.lower())
            if parser is None:
                log(f"[upload_files] unsupported file type skipped: {file_path.name}")
                continue

            try:
                result = parser(str(file_path))
            except Exception as exc:
                log(f"[upload_files] failed to parse file {file_path}\nERROR:{exc}")
                continue


            if not result.get("success"):
                err_msg = result.get("message") or result.get("content")
                log(f"[upload_files] parser reported failure for {file_path}: {err_msg}")
                continue

            content = result.get("content") or []
            if not content:
                log(f"[upload_files] no content extracted from {file_path}")
                continue

            # 这里统一使用绝对路径做 key，保证与 main 侧看到的路径一致
            abs_path = str(file_path.resolve())
            aggregated[abs_path] = content
            processed.append(file_path)

        self.files = aggregated
        return processed

    def upload_local_files(
        self,
        selected_paths: Sequence[Union[str, Path]],
        base_dir: Optional[Union[str, Path]] = None,
    ) -> None:
        if not selected_paths:
            self.files = {}
            return

        normalized: List[Path] = []
        for raw in selected_paths:
            path_obj = Path(raw).expanduser()
            try:
                normalized.append(path_obj.resolve())
            except FileNotFoundError:
                log(f"[upload_files] unable to resolve path: {raw}")

        rel_base = None
        if base_dir is not None:
            rel_base = Path(base_dir).expanduser()
            try:
                rel_base = rel_base.resolve()
            except FileNotFoundError:
                rel_base = rel_base

        processed = self._process_file_paths(normalized, rel_base)
        if processed:
            log(f"[upload_files] prepared {len(processed)} files from manual selection")
        else:
            log("[upload_files] no files prepared from manual selection")

    def upload_files(self) -> None:
        project_root = Path(__file__).resolve().parents[2]
        tmp_dir = project_root / "tmp"

        if not tmp_dir.exists():
            log(f"[upload_files] tmp dir not found: {tmp_dir}")
            self.files = {}
            return

        file_paths = sorted(p for p in tmp_dir.rglob("*") if p.is_file())
        if not file_paths:
            self.files = {}
            return

        processed_files = self._process_file_paths(file_paths, tmp_dir)

        log("successfully processed file: " + " ".join(str(file) for file in file_paths))
        old_docs = project_root / "old_docs"
        for src in processed_files:
            try:
                rel = src.relative_to(tmp_dir)
                dst = old_docs / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                log(f"[upload_files] moved {src} -> {dst}")
            except Exception as e:
                log(f"[upload_files] failed to move {src} to old_docs: {e}")

    def uploaded_files(self) -> list:
        if len(self.files):
            return [key for key in self.files.keys()]
        else:
            return []
    
    def delete_uploaded_file(self, path: Union[str, Path]) -> list:
        """从已上传文件列表中删除指定路径，并返回剩余文件列表。

        这里的 path 可以是任意可解析为绝对路径的字符串/Path；
        内部会 resolve 后与 self.files 的绝对路径 key 匹配。
        """
        if not self.files:
            return []

        try:
            target = str(Path(path).expanduser().resolve())
        except Exception:
            target = str(path)

        if target in self.files:
            del self.files[target]
            log(f"[upload_files] deleted uploaded file: {target}")
        else:
            log(f"[upload_files] file not found in uploaded list: {target}")

        return self.uploaded_files()

    def _compose_input_payload(self) -> Union[str, List[Dict]]:
        if len(self.files):
            combined: List[Dict[str, Any]] = []
            # 将每个文件的内容展开成模型可消费的列表
            for rel_name, content_blocks in self.files.items():
                combined.append({"type": "text", "text": f"[File]: `{rel_name}`"})
                combined.extend(content_blocks)
            combined.append({"type": "text", "text": self.input})
            return combined
        else: 
            return str(self.input)


    def run(self, dialog: str):
        if self.input is None:
            raise Exception("None task!")


        from Agent.request.api import set_dialog
        set_dialog(dialog)
        
        payload = self._compose_input_payload()
        log(f"[task_start] model={self.model}\t with len of {int(len(str(payload))/1024)} KB")
        
        response = self._invoke_model(payload)
        self.files = {}



        think, text, func_call, func_args = parse_response(response)
        log(str(response))
        print('-' * 38, f"\n{BLUE}Assistant{RESET}: ", text)
        if func_call == "Finish":
            log(f"[task_finish]\n{text}")
            log("==================Finish Task====================")
            return
        
        
        while True:
            # print(f"calling {func_call} with {func_args}:\n y to confirm")
            # while input() != 'y':
            #     continue

            if func_call == "ParseFailure":
                observation = """
                你上次生成的回答格式有问题导致Agent无法成功解释，请查阅system_prompt，严格按照要求的输出格式重新输出:
                \nTracestack:\n
                """ + think
            elif func_call == "FalsedGeneration":
                error = func_args["error"]
                print('*' * 38, f"\n{RED}ERROR{RESET}: ", error, '*' * 38)
                break
            else:
                print(f"{GREEN}calling tool{RESET}: {func_call}")
                observation =  tools.call_func(func_call, func_args)
            if isinstance(observation, str) and func_call != dt.read_word_document.__name__:
                log(f"[tool_result] {func_call}\n{observation}")
                
            # 这里可以进行记忆压缩的操作，但难点是什么时候进行压缩，如果Agent正在进行任务没理由压缩记忆，所以需要Agent自行判断是否要进行压缩，或者在任务完成后可以进行压缩
            
            if isinstance(observation, str):
                observation = f"observation after calling {func_call}:\n" + observation       
                     
            response = self._invoke_model(observation)

            think, text, func_call, func_args = parse_response(response)
            log(str(response))
            
            # print("my think: ", think)
            print('-' * 38, f"\n{BLUE}Assistant{RESET}: ", text)
            
            if func_call == "Finish":
                log(f"[task_finish]\n{text}")
                break
        log("==================Finish Task====================")
        # self.compress_context__()