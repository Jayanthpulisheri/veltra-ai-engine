from guardrails import is_command_safe

test_cases = [
    ("python3 -m unittest discover", True),        # Safe: Test execution
    ("git status", True),                         # Safe: Version control
    ("rm -rf /", False),                           # Unsafe: Destructive deletion
    ("ls -la && rm -rf /var/log", False),          # Unsafe: Chained attack
    ("echo 'hello' | base64 -d", False)           # Unsafe: Output piping
]

print("--- RUNNING VELTRA SECURITY GUARDRAIL TESTS ---")
passed = 0
for cmd, expected in test_cases:
    is_safe, reason = is_command_safe(cmd)
    result = (is_safe == expected)
    if result:
        passed += 1
        print(f"[PASS] Command: '{cmd}' -> Safe: {is_safe}")
    else:
        print(f"[FAIL] Command: '{cmd}' -> Expected {expected}, got {is_safe}")

print(f"\nTest Summary: {passed}/{len(test_cases)} Passed")
