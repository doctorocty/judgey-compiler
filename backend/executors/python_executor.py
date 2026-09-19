import subprocess
import sys
import tempfile
import os
import json


def analyze_python(temp_file):
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                temp_file,
                "--output-format",
                "json",
                "--select",
                "F821"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.stdout.strip():
            try:
                return json.loads(result.stdout), ""
            except json.JSONDecodeError:
                return [], result.stdout.strip()

        if result.returncode != 0 and result.stderr.strip():
            return [], result.stderr.strip()

        return [], ""

    except subprocess.TimeoutExpired:
        return [], "Ruff analysis timed out."

    except Exception as error:
        return [], str(error)


def run_python(code):
    temp_file = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as file:
            file.write(code)
            temp_file = file.name

        issues, analyzer_error = analyze_python(temp_file)

        if analyzer_error:
            return {
                "success": False,
                "output": "",
                "error": analyzer_error,
                "errors": 1
            }

        if issues:
            error_messages = []

            for issue in issues:
                location = issue.get("location", {})
                row = location.get("row", "?")
                column = location.get("column", "?")
                message = issue.get(
                    "message",
                    "Unknown error"
                )

                error_messages.append(
                    f"Line {row}, Column {column}: {message}"
                )

            return {
                "success": False,
                "output": "",
                "error": "\n".join(error_messages),
                "errors": len(issues)
            }

        result = subprocess.run(
            [
                sys.executable,
                temp_file
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout,
                "error": "",
                "errors": 0
            }

        return {
            "success": False,
            "output": result.stdout,
            "error": result.stderr,
            "errors": 1
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "Execution timed out after 5 seconds.",
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
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)