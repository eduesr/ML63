with open('scratch/html_diff.txt', 'r', encoding='utf-8') as f:
    diff_lines = f.readlines()

print("--- EXAMINING CHANGES AROUND gasCompareChart ---")
for idx, line in enumerate(diff_lines):
    if 'gasCompareChart' in line:
        print(f"\nMatch at line {idx+1}:")
        start = max(0, idx - 10)
        end = min(len(diff_lines), idx + 10)
        for i in range(start, end):
            prefix = " "
            if diff_lines[i].startswith('+'):
                prefix = "+"
            elif diff_lines[i].startswith('-'):
                prefix = "-"
            print(f"{i+1:4d} {prefix} {diff_lines[i][1:].strip()}")
