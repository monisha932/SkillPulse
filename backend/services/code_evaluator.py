import sys
import subprocess
import json
import tempfile
import os
import time
import sqlite3
from typing import List, Dict, Any, Optional

def evaluate_python(submitted_code: str, function_name: str, test_cases: list, timeout_sec: float = 3.0) -> dict:
    """
    Safely executes submitted Python code against a list of test cases in an isolated subprocess.
    """
    if not submitted_code or not submitted_code.strip():
        return {
            "passed_count": 0,
            "total_count": len(test_cases),
            "all_passed": False,
            "error": "No code submitted.",
            "results": []
        }

    runner_script = f"""
import sys
import json

# User code
{submitted_code}

test_cases_raw = {json.dumps(json.dumps(test_cases))}
test_cases = json.loads(test_cases_raw)
results = []

for idx, tc in enumerate(test_cases):
    inp = tc.get('input', {{}})
    expected = tc.get('expected')
    is_hidden = tc.get('is_hidden', False)
    try:
        if isinstance(inp, dict):
            actual = {function_name}(**inp)
        elif isinstance(inp, list):
            actual = {function_name}(*inp)
        else:
            actual = {function_name}(inp)
            
        passed = (actual == expected)
        results.append({{
            "test_index": idx + 1,
            "passed": passed,
            "input": "Hidden" if is_hidden else inp,
            "expected": "Hidden" if is_hidden else expected,
            "actual": "Hidden" if is_hidden and not passed else actual,
            "is_hidden": is_hidden,
            "error": None
        }})
    except Exception as e:
        results.append({{
            "test_index": idx + 1,
            "passed": False,
            "input": "Hidden" if is_hidden else inp,
            "expected": "Hidden" if is_hidden else expected,
            "actual": None,
            "is_hidden": is_hidden,
            "error": f"{{type(e).__name__}}: {{str(e)}}"
        }})

print("__RESULTS_START__")
print(json.dumps(results))
print("__RESULTS_END__")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as temp_file:
        temp_file.write(runner_script)
        temp_path = temp_file.name

    try:
        start_time = time.time()
        proc = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout_sec
        )
        duration_ms = round((time.time() - start_time) * 1000, 1)
        stdout = proc.stdout
        stderr = proc.stderr

        if "__RESULTS_START__" in stdout and "__RESULTS_END__" in stdout:
            json_str = stdout.split("__RESULTS_START__")[1].split("__RESULTS_END__")[0].strip()
            results = json.loads(json_str)
            passed = sum(1 for r in results if r["passed"])
            return {
                "passed_count": passed,
                "total_count": len(test_cases),
                "all_passed": (passed == len(test_cases)),
                "results": results,
                "execution_time_ms": duration_ms,
                "error": None
            }
        else:
            err_msg = stderr.strip() or stdout.strip() or "Runtime execution failed."
            return {
                "passed_count": 0,
                "total_count": len(test_cases),
                "all_passed": False,
                "results": [],
                "execution_time_ms": duration_ms,
                "error": err_msg
            }
    except subprocess.TimeoutExpired:
        return {
            "passed_count": 0,
            "total_count": len(test_cases),
            "all_passed": False,
            "results": [],
            "error": f"Execution Timed Out (Exceeded {timeout_sec}s limit). Check for infinite loops."
        }
    except Exception as e:
        return {
            "passed_count": 0,
            "total_count": len(test_cases),
            "all_passed": False,
            "results": [],
            "error": f"Internal execution error: {str(e)}"
        }
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


def evaluate_sql(submitted_query: str, test_cases: list, schema_seed: str = "", timeout_sec: float = 3.0) -> dict:
    """
    Executes a submitted SQL query against an in-memory SQLite sandbox database and compares output with expected records.
    """
    if not submitted_query or not submitted_query.strip():
        return {
            "passed_count": 0,
            "total_count": len(test_cases),
            "all_passed": False,
            "error": "No SQL query submitted.",
            "results": []
        }

    results = []
    start_time = time.time()

    for idx, tc in enumerate(test_cases):
        is_hidden = tc.get("is_hidden", False)
        expected = tc.get("expected", [])
        extra_seed = tc.get("input", {}).get("extra_seed", "")

        conn = None
        try:
            conn = sqlite3.connect(":memory:")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Execute schema seed
            if schema_seed:
                cursor.executescript(schema_seed)
            if extra_seed:
                cursor.executescript(extra_seed)

            # Execute candidate query
            cursor.execute(submitted_query)
            raw_rows = cursor.fetchall()

            # Convert rows to list of lists/tuples for comparison
            actual = []
            for r in raw_rows:
                row_vals = []
                for val in r:
                    # Round floats to 2 decimals for clean comparisons
                    if isinstance(val, float):
                        row_vals.append(round(val, 2))
                    else:
                        row_vals.append(val)
                actual.append(row_vals)

            # Compare normalized values
            passed = (actual == expected)

            results.append({
                "test_index": idx + 1,
                "passed": passed,
                "input": "Hidden Test Case" if is_hidden else (extra_seed or "Default Seed Dataset"),
                "expected": "Hidden" if is_hidden else expected,
                "actual": "Hidden" if is_hidden and not passed else actual,
                "is_hidden": is_hidden,
                "error": None
            })
        except Exception as e:
            results.append({
                "test_index": idx + 1,
                "passed": False,
                "input": "Hidden Test Case" if is_hidden else (extra_seed or "Default Seed Dataset"),
                "expected": "Hidden" if is_hidden else expected,
                "actual": None,
                "is_hidden": is_hidden,
                "error": f"SQL Error: {str(e)}"
            })
        finally:
            if conn:
                conn.close()

    duration_ms = round((time.time() - start_time) * 1000, 1)
    passed_cnt = sum(1 for r in results if r["passed"])
    return {
        "passed_count": passed_cnt,
        "total_count": len(test_cases),
        "all_passed": (passed_cnt == len(test_cases) and len(test_cases) > 0),
        "results": results,
        "execution_time_ms": duration_ms,
        "error": None
    }


def evaluate_java(submitted_code: str, class_name: str, test_cases: list, timeout_sec: float = 5.0) -> dict:
    """
    Compiles and executes submitted Java code in an isolated directory using javac & java.
    """
    if not submitted_code or not submitted_code.strip():
        return {
            "passed_count": 0,
            "total_count": len(test_cases),
            "all_passed": False,
            "error": "No Java code submitted.",
            "results": []
        }

    temp_dir = tempfile.mkdtemp()
    results = []
    
    try:
        # 1. Write Solution.java
        solution_file = os.path.join(temp_dir, f"{class_name}.java")
        with open(solution_file, "w", encoding="utf-8") as f:
            f.write(submitted_code)

        # 2. Write TestRunner.java
        runner_code = f"""
import java.util.*;

public class TestRunner {{
    public static void main(String[] args) {{
        Solution sol = new Solution();
        List<Map<String, Object>> results = new ArrayList<>();
"""
        # Inject test case invocations based on class_name
        for idx, tc in enumerate(test_cases):
            inp = tc.get("input", {})
            expected = tc.get("expected")
            is_hidden = tc.get("is_hidden", False)

            if "nums" in inp and "target" in inp:
                # Two Sum problem
                nums_arr = "new int[] {" + ", ".join(map(str, inp["nums"])) + "}"
                target_val = inp["target"]
                exp_arr = "new int[] {" + ", ".join(map(str, expected)) + "}"
                runner_code += f"""
        try {{
            int[] actual = sol.twoSum({nums_arr}, {target_val});
            int[] expected = {exp_arr};
            boolean passed = (actual != null && actual.length == 2 && 
                              ((actual[0] == expected[0] && actual[1] == expected[1]) ||
                               (actual[0] == expected[1] && actual[1] == expected[0])));
            System.out.println("CASE_{idx+1}_RESULT::" + (passed ? "PASS" : "FAIL") + "::" + Arrays.toString(actual));
        }} catch (Exception e) {{
            System.out.println("CASE_{idx+1}_RESULT::ERROR::" + e.toString());
        }}
"""
            elif "s" in inp:
                # Palindrome problem
                escaped_s = json.dumps(inp["s"])
                exp_bool = "true" if expected else "false"
                runner_code += f"""
        try {{
            boolean actual = sol.isPalindrome({escaped_s});
            boolean expected = {exp_bool};
            boolean passed = (actual == expected);
            System.out.println("CASE_{idx+1}_RESULT::" + (passed ? "PASS" : "FAIL") + "::" + actual);
        }} catch (Exception e) {{
            System.out.println("CASE_{idx+1}_RESULT::ERROR::" + e.toString());
        }}
"""

        runner_code += """
    }
}
"""
        runner_file = os.path.join(temp_dir, "TestRunner.java")
        with open(runner_file, "w", encoding="utf-8") as f:
            f.write(runner_code)

        # 3. Compile with javac
        compile_proc = subprocess.run(
            ["javac", solution_file, runner_file],
            capture_output=True,
            text=True,
            cwd=temp_dir,
            timeout=8.0
        )

        if compile_proc.returncode != 0:
            return {
                "passed_count": 0,
                "total_count": len(test_cases),
                "all_passed": False,
                "results": [],
                "error": f"Java Compilation Error:\n{compile_proc.stderr.strip() or compile_proc.stdout.strip()}"
            }

        # 4. Run with java
        start_time = time.time()
        run_proc = subprocess.run(
            ["java", "-cp", temp_dir, "TestRunner"],
            capture_output=True,
            text=True,
            cwd=temp_dir,
            timeout=timeout_sec
        )
        duration_ms = round((time.time() - start_time) * 1000, 1)

        output_lines = run_proc.stdout.splitlines()
        for idx, tc in enumerate(test_cases):
            prefix = f"CASE_{idx+1}_RESULT::"
            matching = [l for l in output_lines if l.startswith(prefix)]
            is_hidden = tc.get("is_hidden", False)

            if matching:
                rest = matching[0][len(prefix):]
                parts = rest.split("::", 1)
                status = parts[0]
                actual_val = parts[1] if len(parts) > 1 else ""
                passed = (status == "PASS")
                error_msg = actual_val if status == "ERROR" else None

                results.append({
                    "test_index": idx + 1,
                    "passed": passed,
                    "input": "Hidden" if is_hidden else tc.get("input"),
                    "expected": "Hidden" if is_hidden else tc.get("expected"),
                    "actual": "Hidden" if is_hidden and not passed else actual_val,
                    "is_hidden": is_hidden,
                    "error": error_msg
                })
            else:
                results.append({
                    "test_index": idx + 1,
                    "passed": False,
                    "input": "Hidden" if is_hidden else tc.get("input"),
                    "expected": "Hidden" if is_hidden else tc.get("expected"),
                    "actual": None,
                    "is_hidden": is_hidden,
                    "error": "No output for test case"
                })

        passed_cnt = sum(1 for r in results if r["passed"])
        return {
            "passed_count": passed_cnt,
            "total_count": len(test_cases),
            "all_passed": (passed_cnt == len(test_cases)),
            "results": results,
            "execution_time_ms": duration_ms,
            "error": None
        }
    except subprocess.TimeoutExpired:
        return {
            "passed_count": 0,
            "total_count": len(test_cases),
            "all_passed": False,
            "results": [],
            "error": f"Execution Timed Out (Exceeded {timeout_sec}s limit)."
        }
    except Exception as e:
        return {
            "passed_count": 0,
            "total_count": len(test_cases),
            "all_passed": False,
            "results": [],
            "error": f"Java execution error: {str(e)}"
        }
    finally:
        # Cleanup temporary directory
        if os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass


def evaluate_code(submitted_code: str, function_name: str, test_cases: list, language: str = "python",
                  class_name: str = "Solution", schema_seed: str = "", timeout_sec: float = 3.0) -> dict:
    """
    Unified entry point for sandboxed code and query evaluation.
    Routes to Python, SQL, or Java evaluator according to language.
    """
    lang = (language or "python").lower().strip()
    if lang == "sql":
        return evaluate_sql(submitted_query=submitted_code, test_cases=test_cases, schema_seed=schema_seed, timeout_sec=timeout_sec)
    elif lang == "java":
        return evaluate_java(submitted_code=submitted_code, class_name=class_name or "Solution", test_cases=test_cases, timeout_sec=timeout_sec)
    else:
        return evaluate_python(submitted_code=submitted_code, function_name=function_name, test_cases=test_cases, timeout_sec=timeout_sec)
