from main import execute_agent_command

print("--- RUNNING VELTRA AI INTEGRATION DEMO ---")

# 1. Test Valid JSON Output
execute_agent_command('echo "{\\"status\\": \\"OK\\", \\"msg\\": \\"Veltra Active\\"}"')

# 2. Test Safe Shell Command
execute_agent_command("git status")

# 3. Test Blocked Chained Execution
execute_agent_command("echo 'hello' && rm -rf /tmp/test_dir")
