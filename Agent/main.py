from datetime import datetime
import msvcrt
import os
import time
from pathlib import Path
from Agent.Core.agent_core import AgentCore
from typing import Any, List, Optional, Set
from Agent.utils.conv_name.conv_naming import auto_name_conv_if_needed

from Agent.utils.input_style import _read_user_input
from Agent.utils.config import (
    _load_config,
    config_,
    delete_config,
    ensure_model,
    list_models,
    set_model_config,
    set_configured_model,
)
import argparse

RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
RESET = "\033[0m"


def _safe_input(prompt: str) -> Optional[str]:
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\n操作已取消!\n")
        return None


def _print_config_tree(node: Any, indent: int = 0) -> None:
    prefix = "  " * indent
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                print(f"{prefix}{key}:")
                _print_config_tree(value, indent + 1)
            else:
                print(f"{prefix}{key}: {value}")
    elif isinstance(node, list):
        for index, item in enumerate(node):
            print(f"{prefix}[{index}]:")
            _print_config_tree(item, indent + 1)
    else:
        print(f"{prefix}{node}")


def _handle_settings_menu() -> None:
    while True:
        config_snapshot = _load_config()
        print("-" * 48)
        print("当前配置:")
        _print_config_tree(config_snapshot)
        print("-" * 48)
        print("1. 设置全局配置")
        print("2. 管理模型配置")
        print("3. 设置配置模型")
        print("4. 返回主菜单")
        choice = _safe_input("选择操作 [1-4]: ")
        if choice is None:
            return
        choice = choice.strip()
        if choice == "1":
            _handle_global_config()
        elif choice == "2":
            _handle_model_management()
        elif choice == "3":
            _handle_configured_model()
        elif choice in {"4", "", "q", "Q"}:
            break
        else:
            print("无效选择!\n")


def _handle_global_config() -> None:
    while True:
        action = _safe_input("选择操作: [a] 添加/更新 / [d] 删除 / [回车返回]: ")
        if action is None:
            print("已退出全局配置。\n")
            return
        action = action.strip().lower()
        if action == "" or action == "b":
            break
        if action not in {"a", "d"}:
            print("无效操作!\n")
            continue

        key = _safe_input("配置键: ")
        if key is None:
            print("该项操作已取消。\n")
            continue
        key = key.strip()
        if not key:
            print("键名不能为空!\n")
            continue

        if action == "d":
            try:
                delete_config(key)
                print("配置删除成功!\n")
            except KeyError:
                print("删除失败: 指定配置不存在。\n")
        else:
            value = _safe_input("配置值: ")
            if value is None:
                print("该项配置已取消。\n")
                continue
            config_(key, value)
            print("配置修改成功!\n")


def _handle_model_management() -> None:
    while True:
        config_snapshot = _load_config()
        models = list_models()
        if models:
            print("已配置模型:")
            for name in models:
                marker = "(配置中)" if config_snapshot.get("configured_model") == name else ""
                print(f" - {name} {marker}")
        else:
            print("当前没有配置任何模型，输入名称即可创建。")
        model_name = _safe_input("输入模型名称（回车返回）: ")
        if model_name is None:
            print("已退出模型管理。\n")
            return
        model_name = model_name.strip()
        if not model_name:
            break
        ensure_model(model_name)
        _edit_model_config(model_name)


def _edit_model_config(model_name: str) -> None:
    while True:
        config_snapshot = _load_config()
        model_config = (
            config_snapshot.get("models", {}).get(model_name, {})
        )
        print(f"[{model_name}] 当前配置:")
        if model_config:
            _print_config_tree(model_config, indent=1)
        else:
            print("  (暂无配置)")
        key = _safe_input(f"[{model_name}] 配置键（回车完成）: ")
        if key is None:
            print(f"已取消 {model_name} 的配置编辑。\n")
            return
        key = key.strip()
        if not key:
            break
        value = _safe_input(f"[{model_name}] 配置值: ")
        if value is None:
            print("该项配置已取消。\n")
            continue
        set_model_config(model_name, key, value)
        print(f"[{model_name}] 配置更新成功!\n")
control_panel = """Welcome for using CodeM!
1. start codem
2. view chats
3. settings
4. contact us"""


def _handle_configured_model() -> None:
    config_snapshot = _load_config()
    models = list_models()
    if not models:
        print("当前没有可用模型，请先创建模型再设置配置项。\n")
        return

    current = config_snapshot.get("configured_model")
    if current:
        print(f"当前配置模型: {current}")
    else:
        print("当前尚未设置配置模型。")

    print("可选模型:")
    for idx, name in enumerate(models, start=1):
        marker = "(当前)" if current == name else ""
        print(f" {idx}. {name} {marker}")

    choice = _safe_input("输入编号或名称（回车取消）: ")
    if choice is None or not choice.strip():
        print("已取消配置模型设置。\n")
        return
    choice = choice.strip()

    if choice.isdigit():
        index = int(choice)
        if 1 <= index <= len(models):
            name = models[index - 1]
        else:
            print("编号超出范围!\n")
            return
    else:
        name = choice

    try:
        set_configured_model(name)
        print(f"配置模型已更新为: {name}\n")
    except ValueError as exc:
        print(f"设置失败: {exc}\n")
def _format_relative_path(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def _collect_all_files(directory: Path) -> List[Path]:
    files: List[Path] = []
    for path in directory.rglob("*"):
        if path.is_file():
            files.append(path)
    return files


def _interactive_file_selection(base_dir: Path) -> List[Path]:
    current_dir = base_dir
    selected: List[Path] = []
    selected_set: Set[Path] = set()
    print_files_list = True
    while True:
        if print_files_list:
            print("-" * 48)
            print(f"当前目录: {current_dir}")
            try:
                entries = sorted(current_dir.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
            except PermissionError:
                print("没有权限访问该目录，已返回上级。\n")
                if current_dir == base_dir:
                    continue
                current_dir = current_dir.parent
                continue

            if not entries:
                print("(目录为空)")

            for idx, entry in enumerate(entries, start=1):
                marker = f"{RED}[DIR]{RESET}" if entry.is_dir() else f"{GREEN}[FILE]{RESET}"
                print(f"{idx}. {marker} {entry.name}")

            select_all_idx = len(entries) + 1
            print(f"{select_all_idx}. 添加当前目录")
            print("b. 返回上一级    d. 完成    q. 取消")

        print_files_list = True
        choice_raw = _safe_input("选择序号: ")
        if choice_raw is None:
            print("已取消文件选择。\n")
            return []
        choice = choice_raw.strip()
        if choice.lower() == "b":
            if current_dir == base_dir:
                print("已经位于根目录。\n")
            else:
                current_dir = current_dir.parent
            continue
        
        if choice.lower() == "d":
            return selected
        if choice.lower() == "q":
            return []

        # 支持用空格或逗号分隔多个序号
        tokens = choice.replace(",", " ").split()
        if not tokens:
            print("无效输入，请重新选择。\n")
            continue

        if not all(tok.isdigit() for tok in tokens):
            print("无效输入，请输入数字序号或命令。\n")
            continue

        indexes = [int(tok) for tok in tokens]

        # 单个序号维持原有行为（可进入目录、选择目录全部等）
        if len(indexes) == 1:
            idx = indexes[0]

            if 1 <= idx <= len(entries):
                entry = entries[idx - 1]
                if entry.is_dir():
                    current_dir = entry
                    continue
                resolved = entry.resolve()
                if resolved in selected_set:
                    print("该文件已在上传列表中。")
                    print_files_list = False
                    continue
                selected.append(resolved)
                selected_set.add(resolved)
                print(f"已添加文件: {GREEN}{_format_relative_path(resolved, base_dir)}{RESET}")
                print_files_list = False
                continue

            if idx == select_all_idx:
                all_files = _collect_all_files(current_dir)
                added = 0
                for file_path in all_files:
                    resolved = file_path.resolve()
                    if resolved in selected_set:
                        continue
                    selected.append(resolved)
                    selected_set.add(resolved)
                    added += 1
                print(f"已添加 {added} 个文件.")
                print_files_list = False
                continue

            print("编号超出范围。\n")
            continue

        # 多个序号：一次性添加多个文件，仅允许文件，不支持目录和“添加当前目录”选项
        added_multi = 0
        for idx in indexes:
            if idx == select_all_idx:
                print(f"序号 {idx} 为'添加当前目录'选项，不能与其他序号一起使用，已忽略。")
                continue
            if not (1 <= idx <= len(entries)):
                print(f"序号 {idx} 超出范围，已忽略。")
                continue
            entry = entries[idx - 1]
            if entry.is_dir():
                print(f"序号 {idx} 对应的是目录，暂不支持一次选择多个目录，已忽略。")
                continue
            resolved = entry.resolve()
            if resolved in selected_set:
                continue
            selected.append(resolved)
            selected_set.add(resolved)
            added_multi += 1

        if added_multi > 0:
            print(f"已添加 {added_multi} 个文件。")
            print_files_list = False
        else:
            print("没有添加任何新文件。\n")


def _handle_file_upload(agent: AgentCore) -> None:
    base_dir = Path.cwd().resolve()
    print("\n== 文件上传模式 ==")
    print("提示：输入 'b' 返回上级，'d' 完成，'q' 取消。\n")
    selected_files = _interactive_file_selection(base_dir)
    if not selected_files:
        print("未选择任何文件，已退出上传模式。\n")
        return

    agent.upload_local_files(selected_files, base_dir)
    # 统计真正解析成功并存入 AgentCore 的文件数量
    uploaded = agent.uploaded_files()
    if not uploaded:
        print("所选文件均未成功解析，未准备任何可用文件。\n")
    else:
        print(f"已准备 {len(uploaded)} 个文件：")
        for file_path in uploaded:
            try:
                rel_view = _format_relative_path(Path(file_path), base_dir)
            except Exception:
                rel_view = file_path
            print(f"- {GREEN}{rel_view}{RESET}")
        print("将在下一次对话时发送。\n")


def _handle_uploaded_files(agent: AgentCore) -> None:
    """查看并删除已解析成功、当前准备发送的文件。"""
    base_dir = Path.cwd().resolve()
    while True:
        uploaded = agent.uploaded_files()
        if not uploaded:
            print("当前没有已上传成功的文件。")
            return

        print("\n== 已上传文件列表 ==")
        for idx, file_path in enumerate(uploaded, start=1):
            try:
                rel_view = _format_relative_path(Path(file_path), base_dir)
            except Exception:
                rel_view = file_path
            print(f" {idx}. {BLUE}{rel_view}{RESET}")

        choice_raw = _safe_input("输入要删除的序号，可用空格或逗号分隔（回车返回）: ")
        if choice_raw is None:
            print("已取消删除操作，当前上传文件保持不变。\n")
            return
        choice = choice_raw.strip()
        if not choice:
            # 直接回车表示不再修改
            print("已退出已上传文件管理。\n")
            return

        tokens = choice.replace(",", " ").split()
        to_remove: Set[int] = set()
        for token in tokens:
            if token.isdigit():
                idx_val = int(token)
                if 1 <= idx_val <= len(uploaded):
                    to_remove.add(idx_val)
                else:
                    print(f"序号 {token} 超出范围，已忽略。")
            else:
                print(f"'{token}' 不是有效序号，已忽略。")

        if not to_remove:
            continue

        # 按序号从大到小删除，避免索引错位
        for idx_val in sorted(to_remove, reverse=True):
            path_to_delete = uploaded[idx_val - 1]
            agent.delete_uploaded_file(path_to_delete)

        print("所选文件已删除。")


def chats_manage(agent: AgentCore, current_dialog: str) -> str:
    """浏览、加载或删除历史聊天记录。返回可能更新的 dialog id。"""
    history_dir = os.path.join(os.path.dirname(__file__), "history")
    os.makedirs(history_dir, exist_ok=True)

    files = [f for f in os.listdir(history_dir) if f.endswith(".json") and os.path.isfile(os.path.join(history_dir, f))]
    if not files:
        print("no chat saved!")
        return current_dialog

    files.sort()
    cache = {idx: os.path.splitext(name)[0] for idx, name in enumerate(files, start=1)}

    print("-" * 32)
    print("chats:")
    for idx, stem in cache.items():
        display = f"{BLUE}{stem}{RESET}" if stem == current_dialog else stem
        print(f"{idx}. {display}")
    print("-" * 32)

    action = _safe_input("选择操作: [l] 加载 / [d] 删除 / [回车返回]: ")
    if action is None or action.strip() == "":
        return current_dialog
    action = action.strip().lower()

    if action not in {"l", "d"}:
        print("无效操作!\n")
        return current_dialog

    choice_raw = _safe_input("输入序号: ")
    if choice_raw is None or not choice_raw.strip().isdigit():
        print("invalid choice!")
        return current_dialog

    idx = int(choice_raw.strip())
    if idx not in cache:
        print("invalid choice!")
        return current_dialog

    stem = cache[idx]
    filename = stem + ".json"
    file_path = os.path.join(history_dir, filename)

    if action == "l":
        agent.load_conv(filename)
        print(f"chat switched to {stem}!")
        return stem

    # delete
    confirm = _safe_input(f"确认删除 {stem}? [y/N]: ")
    if confirm and confirm.strip().lower() == "y":
        try:
            os.remove(file_path)
            print(f"{stem} deleted.")
            # 如果删掉当前会话，则生成新 id
            if stem == current_dialog:
                return datetime.now().strftime("%m%d-%H%M")
        except Exception as exc:
            print(f"删除失败: {exc}")
    return current_dialog


def _run_chat_session(agent: AgentCore, dialog_id: str) -> str:
    print("输入 ':menu' 返回上一级。按 Ctrl+C 重置会话，Ctrl+Z 退出聊天。")
    first_round_named = False  # 标记当前会话是否已经尝试自动命名
    while True:
        try:
            user_input = input(">")
            if not user_input.strip():
                continue
            if user_input.strip().lower() in {":menu", ":back"}:
                print("已返回聊天菜单。\n")
                break
            agent.set_input(user_input)
            agent.run(dialog_id)

            # 第一轮完整对话结束后尝试自动命名一次
            if not first_round_named:
                dialog_id = auto_name_conv_if_needed(dialog_id)
                first_round_named = True
        except KeyboardInterrupt:
            agent.reset_conversation__()
            print("A new chat started!")
            dialog_id = datetime.now().strftime("%m%d-%H%M")
            first_round_named = False
        except EOFError:
            print("\nThanks for using CodeM!")
            break
    return dialog_id


        
        
def main():
    CURRENT_DIALOG_ = datetime.now().strftime("%m%d-%H%M")
    
    print(control_panel)
    agent = AgentCore()
    while True:
        ch = msvcrt.getwch()
        if ch == "1":
            while True:
                print("-" * 32)
                print("1. 进行对话")
                print("2. 上传文件")
                print("3. 查看/删除已上传文件")
                print("4. 返回主菜单")
                sub_choice = _safe_input("选择操作 [1-4]: ")
                if sub_choice is None:
                    break
                sub_choice = sub_choice.strip()
                if sub_choice == "1":
                    CURRENT_DIALOG_ = _run_chat_session(agent, CURRENT_DIALOG_)
                elif sub_choice == "2":
                    _handle_file_upload(agent)
                elif sub_choice == "3":
                    _handle_uploaded_files(agent)
                elif sub_choice in {"4", "", "b", "B"}:
                    break
                else:
                    print("无效选择!\n")
        
        elif ch == "2":
            CURRENT_DIALOG_ = chats_manage(agent, CURRENT_DIALOG_)
            
        
        elif ch == "3":
            time.sleep(0.3)
            _handle_settings_menu()
        
        elif ch == "4":
            print("-" * 32)
            print("Github: https://github.com/scutll/TinyAgent")
            print("-" * 32)
        
        else:
            if ch == "\003" or ch == "\x1b" or ch == "\x1a":  # Ctrl+C\Ctrl+Z\ESC
                return
            
            handle_invalid_choice()
            
    
        

if __name__ == "__main__":
    main()
    
def handle_invalid_choice():
    print("not a valid choice!", end="", flush=True)
            
    start = time.time()
    while time.time() - start < 1:

        if msvcrt.kbhit():
            msvcrt.getwch() 
        
        time.sleep(0.01) 
    
    print("\r\033[2K", end="", flush=True)