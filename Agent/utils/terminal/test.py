"""Manual interactive test for execute_command tool

Demonstrates driving a persistent shell through the execute_command tool
interface (with TerminalSessionManager behind the scenes).
"""

from pathlib import Path
from Agent.tools.System_tools import execute_command


def main():
    tool = execute_command()

    print(
        "Start an interactive shell session via execute_command.\n"
        "Type commands to send; use 'exit', 'quit', or 'q' to stop.\n"
    )

    # --- Java compile & run demo (通过 execute_command 的内部会话) ---
    # run_java_demo(tool)

    try:

        while True:
            # user_cmd = input("agent input >>> ")
            # if user_cmd.strip() in {"exit", "quit", "q"}:
            #     break

            # 交互式输入：对外只需要提供一行命令字符串即可，
            # execute_command 会复用内部的终端会话。
            result = tool(command="conda env list")

            print(result.strip())
            break
    finally:
        # 如有需要可以在这里手动关闭内部 session；当前实现使用默认 session_id="default"。
        tool.session_manager.close("default")
        print("Session closed.")


def run_java_demo(tool: execute_command):
    """Create a tiny Java program, compile it, and run it through execute_command."""

    src_name = "AgentTerminalHello.java"
    src_code = (
        "import java.util.Scanner;\n"
        "public class AgentTerminalHello {\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        System.out.println(\"Hello from Java via execute_command! Please input your name:\");\n"
        "        String name = sc.nextLine();\n"
        "        System.out.println(\"Nice to meet you, \" + name + \"!\");\n"
        "        sc.close();\n"
        "    }\n"
        "}\n"
    )

    Path(src_name).write_text(src_code, encoding="utf-8")
    print(f"[java] wrote {src_name}\n")

    compile_result = tool(command=f"javac {src_name}")
    print("[java] compile output:\n" + compile_result.strip() + "\n")

    run_result = tool(command="java AgentTerminalHello")
    print("[java] run output:\n" + run_result.strip() + "\n")


if __name__ == "__main__":
    main()
    