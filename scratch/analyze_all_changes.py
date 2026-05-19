with open('scratch/html_diff.txt', 'r', encoding='utf-8') as f:
    diff_lines = f.readlines()

print("--- SUMMARIZING ALL CHANGED BLOCKS ---")
hunks = []
current_hunk = []
in_hunk = False

for line in diff_lines:
    if line.startswith('@@'):
        if current_hunk:
            hunks.append(current_hunk)
            current_hunk = []
        in_hunk = True
        current_hunk.append(line)
    elif in_hunk:
        current_hunk.append(line)

if current_hunk:
    hunks.append(current_hunk)

print(f"Total change hunks: {len(hunks)}")

for idx, hunk in enumerate(hunks):
    header = hunk[0].strip()
    deletions = sum(1 for l in hunk if l.startswith('-'))
    additions = sum(1 for l in hunk if l.startswith('+'))
    print(f"\nHunk {idx+1}: {header} (-{deletions}, +{additions})")
    
    # Print first few lines of deletions and additions to see what it is about
    del_lines = [l[1:].strip() for l in hunk if l.startswith('-')][:5]
    add_lines = [l[1:].strip() for l in hunk if l.startswith('+')][:5]
    
    if del_lines:
        print("  DELETED:")
        for l in del_lines:
            print(f"    - {l[:100]}")
    if add_lines:
        print("  ADDED:")
        for l in add_lines:
            print(f"    + {l[:100]}")
