import subprocess
import sys
import tempfile
import os
import ast
import io

from pyflakes.reporter import Reporter
from backend.executors.sandbox import limit_resources

_BLOCKING_MESSAGE_TYPES = ("UndefinedName", "UndefinedLocal", "UndefinedExport")


def analyze_python(code):
    try:
        compile(code, "<submission>", "exec", dont_inherit=True)
    except SyntaxError as error:
        return [f"Line {error.lineno or '?'}, Column {error.offset or 0}: {error.msg or 'invalid syntax'}"]
    except (ValueError, OverflowError) as error:
        return [str(error)]

    from pyflakes.checker import Checker
    tree = ast.parse(code)
    checker = Checker(tree, filename="<submission>")

    return [
        f"Line {m.lineno}, Column {m.col + 1}: {m.message % m.message_args}"
        for m in checker.messages
        if type(m).__name__ in _BLOCKING_MESSAGE_TYPES
    ]


def run_python(code):
    temp_file = None
    try:
        issues = analyze_python(code)
        if issues:
            return {"success": False, "output": "", "error": "\n".join(issues), "errors": len(issues)}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as file:
            file.write(code)
            temp_file = file.name

        result = subprocess.run(
            [sys.executable, temp_file], capture_output=True, text=True, timeout=5,
            stdin=subprocess.DEVNULL, preexec_fn=limit_resources
        )

        if result.returncode == 0:
            return {"success": True, "output": result.stdout, "error": "", "errors": 0}
        return {"success": False, "output": result.stdout, "error": result.stderr, "errors": 1}

    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": "Execution timed out after 5 seconds.", "errors": 1}
    except Exception as error:
        return {"success": False, "output": "", "error": str(error), "errors": 1}
    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)