import subprocess
import tempfile
import os
import re

PROJECT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

BASH_PATH = r"C:\msys64\usr\bin\bash.exe"

def windows_to_msys(path):
    path = os.path.abspath(path)
    drive = path[0].lower()
    rest = path[2:].replace("\\", "/")
    return f"/{drive}{rest}"

def run_c(code):
    temp_dir = None

    try:
        temp_dir = tempfile.mkdtemp(
            dir=PROJECT_DIR,
            prefix=".judgy_c_"
        )

        source_file = os.path.join(
            temp_dir,
            "program.c"
        )

        executable_file = os.path.join(
            temp_dir,
            "program.exe"
        )

        with open(
            source_file,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(code)

        source_msys = windows_to_msys(source_file)
        executable_msys = windows_to_msys(executable_file)

        compile_command = (
            f'gcc -fdiagnostics-color=never '
            f'"{source_msys}" '
            f'-o "{executable_msys}"'
        )

        environment = os.environ.copy()
        environment["MSYSTEM"] = "UCRT64"
        environment["CHERE_INVOKING"] = "1"

        environment["PATH"] = (
            r"C:\msys64\ucrt64\bin"
            + ";"
            + r"C:\msys64\usr\bin"
            + ";"
            + environment.get("PATH", "")
        )

        compile_result = subprocess.run(
            [
                BASH_PATH,
                "--login",
                "-c",
                compile_command
            ],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=PROJECT_DIR,
            env=environment
        )

        if compile_result.returncode != 0:
            error_output = (
                compile_result.stderr
                or compile_result.stdout
            ).strip()

            error_lines = re.findall(
                r"(?m)^.*?:\d+:\d+:\s+error:.*$",
                error_output
            )

            error_count = len(error_lines)

            if error_count == 0:
                error_count = 1

            formatted_errors = []

            for line in error_lines:
                match = re.search(
                    r":(\d+):(\d+):\s+error:\s+(.*)$",
                    line
                )

                if match:
                    formatted_errors.append(
                        f"Line {match.group(1)}, Column {match.group(2)}: {match.group(3)}"
                    )
                else:
                    formatted_errors.append(line)

            if not formatted_errors:
                formatted_errors.append(
                    error_output or "C compilation failed."
                )

            return {
                "success": False,
                "output": "",
                "error": "\n".join(formatted_errors),
                "errors": error_count
            }

        run_command = f'"{executable_msys}"'

        run_result = subprocess.run(
            [
                BASH_PATH,
                "--login",
                "-c",
                run_command
            ],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=PROJECT_DIR,
            env=environment
        )

        if run_result.returncode == 0:
            return {
                "success": True,
                "output": run_result.stdout,
                "error": "",
                "errors": 0
            }

        return {
            "success": False,
            "output": run_result.stdout,
            "error": run_result.stderr,
            "errors": 1
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "Execution timed out.",
            "errors": 1
        }

    except Exception as error:
        return {
            "success": False,
            "output": "",
            "error": str(error),
            "errors": 1
        }

    finally:
        if temp_dir and os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                filepath = os.path.join(
                    temp_dir,
                    filename
                )

                try:
                    os.remove(filepath)
                except Exception:
                    pass

            try:
                os.rmdir(temp_dir)
            except Exception:
                pass