import os

dir_path = "/Users/eduardosr/Documents/GitHub/ML63/scratch/extracted_hallazgos"
prefix_files = [f for f in os.listdir(dir_path) if f.startswith('25-')]

for fname in sorted(prefix_files):
    fpath = os.path.join(dir_path, fname)
    print(f"\n=========================================")
    print(f"FILE: {fname}")
    print(f"=========================================")
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content[:2500]) # print first 2500 characters
