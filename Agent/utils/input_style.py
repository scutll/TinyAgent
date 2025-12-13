RESET = "\033[0m"
DARK_GRAY = "\033[90m"
VISIBLE_PROMPT = "Simply state your need for codeM:"
import msvcrt


def _read_user_input() -> str:
    display_prompt = f"{DARK_GRAY}{VISIBLE_PROMPT}{RESET} "
    print(display_prompt, end="", flush=True)
    buffer = []
    prompt_cleared = False
    clear_length = len(VISIBLE_PROMPT) + 1  # +1 for the trailing space

    while True:
        ch = msvcrt.getwch()

        if ch in ("\r", "\n"):
            print()
            break
        if ch == "\003":  # Ctrl+C
            raise KeyboardInterrupt
        if ch == "\x1a" or ch == "\x1b":  # Ctrl+Z or ESC
            raise EOFError
        if ch in ("\b", "\x7f"):
            if buffer:
                buffer.pop()
                print("\b \b", end="", flush=True)
                if not buffer:
                    print("\r\033[2K", end="", flush=True)
                    print(display_prompt, end="", flush=True)
                    prompt_cleared = False
            continue

        if not prompt_cleared:
            print("\r" + " " * clear_length + "\r", end="", flush=True)
            prompt_cleared = True
            if buffer:
                print("".join(buffer), end="", flush=True)

        buffer.append(ch)
        print(ch, end="", flush=True)

    return "".join(buffer)
