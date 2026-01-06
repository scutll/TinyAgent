from typing import List
from pathlib import Path
import json

from Agent.Memory.container import MemoryContainer
from Agent.request.api import get_response_from_gpt
from Agent.utils.conv_name.naming_prompt import name_a_conv_prompt
from Agent.utils.logging_ import log


def name_a_conv(conv: List) -> str:
    """给定一轮对话内容，向模型请求一个会话标题。"""
    tmp_container = MemoryContainer()
    tmp_container._add_system_prompt(name_a_conv_prompt)
    build_conv(conv, tmp_container)
    title = get_response_from_gpt(
        "以上是一轮人机对话的内容,请你进行总结并只输出标题结果",
        tmp_container,
    )
    return title


def build_conv(convs: List, container: MemoryContainer) -> None:
    """将 JSON 中的一轮人机对话写入临时 MemoryContainer。

    目前约定 convs 为长度为 2 的列表：第 0 项为 user，第 1 项为 assistant。
    """
    if len(convs) != 2:
        raise Exception(f"Number of talks supposed to be 2! {len(convs)} now!")

    user_talk = convs[0]["content"]["content"]
    assistant_talk = convs[1]["content"]["content"]
    container._add_user_message(user_talk)
    container._add_assistant_message(assistant_talk)


def auto_name_conv_if_needed(dialog_id: str) -> str:
    """如果指定会话还没命名，则自动生成标题并写回 history JSON。

    同时在成功命名后，将 history 文件从
    `{dialog_id}.json` 重命名为 `{dialog_id}-{title}.json`，
    并返回最新的 dialog_id（用于后续保存和切换会话）。
    """
    agent_dir = Path(__file__).resolve().parents[2]
    history_path = agent_dir / "history" / f"{dialog_id}.json"

    # 默认返回原始 dialog_id，任何失败场景都保持不变
    new_dialog_id = dialog_id

    log(f"[conv_title] try auto naming for dialog_id='{dialog_id}', file='{history_path.name}'")

    if not history_path.exists():
        log("[conv_title] history file not found, skip auto naming")
        return new_dialog_id

    try:
        with history_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        log(f"[conv_title] failed to load history json: {exc}")
        return new_dialog_id

    conv_name = data.get("conv_name")
    # 只在未命名或占位名的情况下生成
    if conv_name and conv_name != "Not named":
        log(f"[conv_title] already named as '{conv_name}', skip")
        return new_dialog_id

    convs = data.get("conversation") or []
    if len(convs) < 2:
        # 还没形成完整一轮人机对话
        log(f"[conv_title] only {len(convs)} messages, need at least 2, skip")
        return new_dialog_id

    first_round = convs[:2]

    try:
        title = name_a_conv(first_round).strip()
    except Exception as exc:
        log(f"[conv_title] LLM title generation failed: {exc}")
        return new_dialog_id

    if not title:
        log("[conv_title] empty title returned, skip")
        return new_dialog_id

    data["conv_name"] = title
    try:
        with history_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        log(f"[conv_title] conv_name set to '{title}' in json")
    except Exception as exc:
        log(f"[conv_title] failed to write conv_name to json: {exc}")
        return new_dialog_id

    # 基于标题生成新的文件名
    safe_title = "".join(ch for ch in title if ch not in "\\/:*?\"<>|")
    if not safe_title:
        log("[conv_title] title becomes empty after sanitizing, skip rename")
        return new_dialog_id

    new_path = history_path.with_name(safe_title + ".json")

    # 如已是目标文件名，直接返回
    if new_path == history_path:
        log("[conv_title] history file name already matches safe_title, no rename")
        return new_dialog_id

    try:
        history_path.rename(new_path)
        new_dialog_id = safe_title
        log(f"[conv_title] history file renamed to '{new_path.name}', new_dialog_id='{new_dialog_id}'")
    except Exception as exc:
        # 重命名失败不影响后续使用原文件名
        log(f"[conv_title] failed to rename history file: {exc}")
        return dialog_id

    return new_dialog_id
    
