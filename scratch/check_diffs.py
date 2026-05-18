import re
import subprocess

def run_git_command(args):
    result = subprocess.run(['git'] + args, capture_output=True, text=True, cwd='/Users/eduardosr/Documents/GitHub/ML63')
    return result.stdout

remote_html = run_git_command(['show', 'origin/main:ML63.html'])

def extract_function(html_content, name):
    # Find position of 'async function name' or 'function name'
    match = re.search(r'(?:async\s+)?function\s+' + re.escape(name) + r'\b', html_content)
    if not match:
        return None
    
    start_pos = match.start()
    # Now find the first opening brace '{' after start_pos
    brace_start = html_content.find('{', start_pos)
    if brace_start == -1:
        return None
    
    # Trace braces to find matching closing brace
    brace_count = 1
    current_pos = brace_start + 1
    while brace_count > 0 and current_pos < len(html_content):
        char = html_content[current_pos]
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        current_pos += 1
    
    return html_content[start_pos:current_pos]

for target in ['buscarMovimientosFactura', 'guardarFacturaRef']:
    func_code = extract_function(remote_html, target)
    if func_code:
        print(f"\n--- EXTRACTED {target} ---")
        print(func_code)
        with open(f'/Users/eduardosr/Documents/GitHub/ML63/scratch/remote_{target}.js', 'w', encoding='utf-8') as f:
            f.write(func_code)
    else:
        print(f"Could not find function {target}")
