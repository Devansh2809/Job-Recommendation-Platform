import re

def normalize_whitespace(text: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def fix_broken_lines(text: str) -> str:
    """
    Fix lines broken mid-sentence.
    """
    lines = text.split('\n')
    fixed = []

    for line in lines:
        if fixed and not fixed[-1].endswith(('.', ':')) and line and line[0].islower():
            fixed[-1] += ' ' + line
        else:
            fixed.append(line)

    return '\n'.join(fixed)

def clean_text(text: str) -> str:
    text = normalize_whitespace(text)
    text = fix_broken_lines(text)
    return text
