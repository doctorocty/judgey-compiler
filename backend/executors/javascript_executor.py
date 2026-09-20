import subprocess
import os
import json

PROJECT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

NODE_PATH = r"C:\Program Files\nodejs\node.exe"

if not os.path.exists(NODE_PATH):
    NODE_PATH = "node"

ESLINT_PATH = os.path.join(
    PROJECT_DIR,
    "node_modules",
    "eslint",
    "bin",
    "eslint.js"
)

def analyze_javascript(code):
    temp_file = None

    try:
        temp_file = os.path.join(
            PROJECT_DIR,
            ".judgy_temp.js"
        )

        with open(
            temp_file,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(code)

        result = subprocess.run(
            [
                NODE_PATH,
                ESLINT_PATH,
                temp_file,
                "--no-config-lookup",
                "--format",
                "json",
                "--global",
                "console",
                "--rule",
                "no-undef:error"
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=PROJECT_DIR
        )

        output = result.stdout.strip()

        if not output:
            if result.stderr.strip():
                return [{
                    "line": 1,
                    "column": 1,
                    "message": result.stderr.strip()
                }]
            return []

        data = json.loads(output)

        if not data:
            return []

        return data[0].get("messages", [])

    except subprocess.TimeoutExpired:
        return [{
            "line": 1,
            "column": 1,
            "message": "JavaScript analysis timed out."
        }]

    except Exception as error:
        return [{
            "line": 1,
            "column": 1,
            "message": str(error)
        }]

    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)


def run_javascript(code):
    temp_file = None

    try:
        issues = analyze_javascript(code)

        if issues:
            error_messages = []

            for issue in issues:
                line = issue.get("line", "?")
                column = issue.get("column", "?")
                message = issue.get(
                    "message",
                    "Unknown error"
                )

                error_messages.append(
                    f"Line {line}, Column {column}: {message}"
                )

            return {
                "success": False,
                "output": "",
                "error": "\n".join(error_messages),
                "errors": len(issues)
            }

        temp_file = os.path.join(
            PROJECT_DIR,
            ".judgy_run.js"
        )

        with open(
            temp_file,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(code)

        result = subprocess.run(
            [
                NODE_PATH,
                temp_file
            ],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=PROJECT_DIR
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