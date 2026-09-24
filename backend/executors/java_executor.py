import subprocess
import tempfile
import shutil
import os
import re

from backend.executors.sandbox import limit_resources_no_address_space

JAVAC = shutil.which("javac") or "javac"
JAVA = shutil.which("java") or "java"

CLASS_NAME_PATTERN = re.compile(r"public\s+class\s+([A-Za-z_$][A-Za-z0-9_$]*)")


def _class_name(code, default="Main"):
    match = CLASS_NAME_PATTERN.search(code)
    return match.group(1) if match else default


def _format_javac_errors(stderr):
    error_lines = re.findall(r"(?m)^.*?\.java:\d+:\s+error:.*$", stderr)
    error_count = len(error_lines) or 1
    formatted = []
    for line in error_lines:
        match = re.search(r"\.java:(\d+):\s+error:\s+(.*)$", line)
        formatted.append(f"Line {match.group(1)}: {match.group(2)}" if match else line)
    if not formatted:
        formatted.append(stderr.strip() or "Java compilation failed.")
    return "\n".join(formatted), error_count


def run_java(code):
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix="judgy_java_")
        class_name = _class_name(code)
        source_file = os.path.join(temp_dir, f"{class_name}.java")

        with open(source_file, "w", encoding="utf-8") as file:
            file.write(code)

        compile_result = subprocess.run(
            [JAVAC, "-encoding", "UTF-8", "-d", temp_dir, source_file],
            capture_output=True, text=True, timeout=15, cwd=temp_dir,
        )

        if compile_result.returncode != 0:
            error_message, error_count = _format_javac_errors(compile_result.stderr)
            return {"success": False, "output": "", "error": error_message, "errors": error_count}

        run_result = subprocess.run(
            [JAVA, "-Xmx192m", "-XX:+UseSerialGC", "-cp", temp_dir, class_name],
            capture_output=True, text=True, timeout=5, cwd=temp_dir,
            stdin=subprocess.DEVNULL,
            preexec_fn=limit_resources_no_address_space,
            env={"PATH": os.environ.get("PATH", "")},
        )

        if run_result.returncode == 0:
            return {"success": True, "output": run_result.stdout, "error": "", "errors": 0}
        return {
            "success": False, "output": run_result.stdout,
            "error": run_result.stderr or f"Program exited with code {run_result.returncode}.",
            "errors": 1,
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": "Execution timed out.", "errors": 1}
    except Exception as error:
        return {"success": False, "output": "", "error": str(error), "errors": 1}
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)