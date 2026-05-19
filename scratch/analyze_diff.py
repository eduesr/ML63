with open('scratch/html_diff.txt', 'r', encoding='utf-8') as f:
    diff_lines = f.readlines()

print("--- ANALYZING DELETIONS AND ADDITIONS IN ML63.html ---")
context = []
matching_hunks = []

for idx, line in enumerate(diff_lines):
    if line.startswith('@@'):
        context.append((idx, line))
    # Look for keywords related to the features
    if any(keyword in line for keyword in ['facturaSearchInput', 'buscarMovimientosFactura', 'guardarFacturaRef', 'vincular', 'limpiezaChart']):
        # Find the hunk header
        hunk_header = None
        for c_idx, c_line in reversed(context):
            if c_idx < idx:
                hunk_header = c_line
                break
        
        matching_hunks.append((idx, hunk_header, line))

# Print the matching hunks
seen_hunks = set()
for idx, hunk, line in matching_hunks:
    if hunk not in seen_hunks:
        seen_hunks.add(hunk)
        print(f"\nHunk: {hunk.strip()}")
        # Print 10 lines before and after the matching line in the diff
        start = max(0, idx - 15)
        end = min(len(diff_lines), idx + 15)
        for i in range(start, end):
            prefix = " "
            if diff_lines[i].startswith('+'):
                prefix = "+"
            elif diff_lines[i].startswith('-'):
                prefix = "-"
            print(f"{i+1:4d} {prefix} {diff_lines[i][1:].strip()}")
