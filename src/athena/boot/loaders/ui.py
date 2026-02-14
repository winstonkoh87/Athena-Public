from athena.boot.constants import BOLD, CYAN, RESET

class UILoader:
    @staticmethod
    def divider(title: str):
        """Print a section divider."""
        print(f"\n{BOLD}{CYAN}{'─' * 60}{RESET}")
        print(f"{BOLD}{CYAN}{title}{RESET}")
        print(f"{BOLD}{CYAN}{'─' * 60}{RESET}\n")

    @staticmethod
    def header(title: str, color: str = CYAN):
        print(f"\n{BOLD}{color}{title}{RESET}")
