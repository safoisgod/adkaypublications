import os

EXCLUDE = {'.git', 'venv', '__pycache__', 'static'}

def tree(dir_path, prefix=""):
    contents = [c for c in os.listdir(dir_path) if c not in EXCLUDE]
    pointers = ['├── '] * (len(contents) - 1) + ['└── ']

    for pointer, name in zip(pointers, contents):
        path = os.path.join(dir_path, name)
        print(prefix + pointer + name)

        if os.path.isdir(path):
            extension = '│   ' if pointer == '├── ' else '    '
            tree(path, prefix + extension)

tree(".")