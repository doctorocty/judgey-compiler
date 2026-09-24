import subprocess
import tempfile
import shutil
import os
import re

from backend.executors.sandbox import limit_resources

GPP = shutil.which("g++") or "g++"


def run_cpp(code):
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix="judgy_cpp_")
        source_file = os.path.join(temp_dir, "program.cpp")
        executable_file = os.path.join(temp_dir, "program")

        with open(source_file, "w", encoding="utf-8") as file:
            file.write(code)

        compile_result = subprocess.run(
            [GPP, "-std=c++17", "-fdiagnostics-color=never", source_file, "-o", executable_file],
            capture_output=True, text=True, timeout=15, cwd=temp_dir,
        )

        if compile_result.returncode != 0:
            error_output = (compile_result.stderr or compile_result.stdout).strip()
            error_lines = re.findall(r"(?m)^.*?:\d+:\d+:\s+error:.*$", error_output)
            error_count = len(error_lines) or 1
            formatted_errors = []
            for line in error_lines:
                match = re.search(r":(\d+):(\d+):\s+error:\s+(.*)$", line)
                if match:
                    formatted_errors.append(f"Line {match.group(1)}, Column {match.group(2)}: {match.group(3)}")
                else:
                    formatted_errors.append(line)
            if not formatted_errors:
                formatted_errors.append(error_output or "C++ compilation failed.")
            return {"success": False, "output": "", "error": "\n".join(formatted_errors), "errors": error_count}

        run_result = subprocess.run(
            [executable_file], capture_output=True, text=True, timeout=5,
            cwd=temp_dir, stdin=subprocess.DEVNULL, preexec_fn=limit_resources,
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