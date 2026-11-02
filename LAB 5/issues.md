# Lab 5 – Static Code Analysis
## Issue Identification and Resolution

### 1. Objective

The objective of this lab is to improve the quality, security, readability, and maintainability of the Employee Payroll System using three static code analysis tools: Pylint, Bandit, and Flake8.

### 2. Issues Identified and Fixed

| Sl. No. | Issue | Type | Description | Fix Approach |
|---|---|---|---|---|
| 1 | Mutable Default Argument | Bug | A mutable list was used as a default argument in the `process_salary()` function. This could cause data to be shared between function calls. | Changed the default argument to `None` and initialized an empty list inside the function. |
| 2 | Broad Exception Handling | Code Quality | Broad exception handling could hide unexpected errors and make debugging difficult. | Replaced broad exception handling with specific `OSError` handling. |
| 3 | Unsafe eval() Usage | Security | The use of `eval()` can execute arbitrary Python expressions and create security risks. | Removed `eval()` and used the JSON module for safe data serialization. |
| 4 | Weak MD5 Hashing | Security | MD5 is considered unsuitable for secure hashing applications. | Replaced MD5 with the SHA-256 hashing algorithm. |
| 5 | Insecure Random Token Generation | Security | The standard random module is not suitable for generating security-sensitive tokens. | Used the `secrets` module to generate random payroll tokens. |
| 6 | Unsafe Shell Execution | Security | Executing shell commands can introduce command injection vulnerabilities. | Removed shell command execution. |
| 7 | Hardcoded Secret | Security | Storing sensitive information directly in source code can expose confidential information. | Removed the hardcoded secret. |
| 8 | Formatting and Naming Issues | Code Style | Inconsistent formatting and naming conventions reduced readability. | Improved formatting, naming conventions, and code organization. |

### 3. Static Analysis Results

The following results were obtained after modifying the Python program.

| Tool | Before | After |
|---|---|---|
| Pylint | 5.32/10 | 10.00/10 |
| Bandit | Issues identified in original code | No issues identified |
| Flake8 | Formatting issues | No errors reported |

### 4. Conclusion

The static code analysis tools helped identify and resolve programming, security, and formatting issues in the Employee Payroll System. The updated program achieved a Pylint score of 10.00/10, Bandit reported no security issues, and Flake8 reported no formatting errors.

These improvements make the program more secure, readable, maintainable, and reliable.