import os

def replace_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    if 'from collections.abc import Iterable' in content:
        print(f'Replacing in {file_path}')
        content = content.replace('from collections.abc import Iterable', 'from collections.abc import Iterable')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                replace_in_file(os.path.join(root, file))

if __name__ == '__main__':
    main() 