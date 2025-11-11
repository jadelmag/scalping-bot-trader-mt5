class Logger:
    def __init__(self):
        self.name = "Logger"

    @staticmethod
    def color_text(text, color="red"):
        colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "reset": "\033[0m"
        }
        colored_text = f"{colors.get(color, '')}{text}{colors['reset']}"
        print(colored_text)
        return colored_text
