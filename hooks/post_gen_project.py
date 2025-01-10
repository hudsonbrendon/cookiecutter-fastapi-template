import sys
import subprocess


def is_created_env() -> bool:
    try:
        subprocess.run(
            ["cp", "dot-env-template", ".env"],
            capture_output=True,
            check=True
        )
        return True
    except Exception:
        return False


if __name__ == "__main__":
    if not is_created_env():
        print("ERROR: .env not created.")
        sys.exit(1)