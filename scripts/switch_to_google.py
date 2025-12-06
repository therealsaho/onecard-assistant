import os

env_path = ".env"
new_lines = []
updated = False

if os.path.exists(env_path):
    with open(env_path, "r") as f:
        lines = f.readlines()
        
    for line in lines:
        if line.startswith("STT_PROVIDER="):
            new_lines.append("STT_PROVIDER=google\n")
            updated = True
        else:
            new_lines.append(line)
else:
    lines = []

if not updated:
    new_lines.append("STT_PROVIDER=google\n")

with open(env_path, "w") as f:
    f.writelines(new_lines)

print("Updated .env with STT_PROVIDER=google")
