import os

dir_path = "/Users/eduardosr/Documents/GitHub/ML63/scratch/extracted_hallazgos"
targets = [
    '25-119 MODESTO LAFUENTE 63 (LIMPIEZA MANTENIMIENTO DIARIO) - 2002_selectable.txt',
    '25-120 MODESTO LAFUENTE 63 (GESTION DE CUBOS) - 2002_selectable.txt'
]

for fname in targets:
    fpath = os.path.join(dir_path, fname)
    print(f"\n=========================================")
    print(f"FILE: {fname}")
    print(f"=========================================")
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content[:2500])
    else:
        print("File not found.")
