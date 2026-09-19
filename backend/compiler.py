from executors.python_executor import run_python
from executors.javascript_executor import run_javascript
from executors.c_executor import run_c

def compile_code(language, code):
    if language == "python":
        return run_python(code)

    if language == "javascript":
        return run_javascript(code)

    if language == "c":
        return run_c(code)

    return {
        "success": False,
        "output": "",
        "error": f"{language} compiler is not connected yet.",
        "errors": 1
    }