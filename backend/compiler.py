from backend.executors.python_executor import run_python
from backend.executors.javascript_executor import run_javascript
from backend.executors.c_executor import run_c
from backend.executors.java_executor import run_java
from backend.executors.cpp_executor import run_cpp

def compile_code(language, code):
    if language == "python":
        return run_python(code)
    if language == "javascript":
        return run_javascript(code)
    if language == "c":
        return run_c(code)
    if language == "java":
        return run_java(code)
    if language == "cpp":
        return run_cpp(code)
    return {"success": False, "output": "", "error": f"{language} compiler is not connected yet.", "errors": 1}