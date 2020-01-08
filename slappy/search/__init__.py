import re


def create_pattern(pattern, rna=False):
    ut = 'U' if rna else 'T'
    alphabet = {
        'A': 'A',
        'C': 'C',
        'G': 'G',
        'T': ut,
        'U': ut,
        'R': '[AG]',
        'Y': f'[C{ut}]',
        'S': f'[CG]',
        'W': f'[A{ut}]',
        'K': f'[G{ut}]',
        'M': f'[AC]',
        'B': f'[CG{ut}]',
        'D': f'[AG{ut}]',
        'H': f'[AC{ut}]',
        'V': f'[ACG]',
        'N': f'[ACG{ut}]',
        '-': '',
        '.': '',
    }
    
    new_pattern = []
    for c in pattern:
        new_pattern.append(alphabet[c.upper()])
    
    return f'(?=({"".join(new_pattern)}))'
    
    
def search(search_string, sequence, rna):
    pattern = create_pattern(search_string, rna)
    for match in re.finditer(pattern, sequence, flags=re.IGNORECASE):
        yield {'from': match.span()[0]+1, 'to': match.span()[0]+1 + len(match.group(1)), 'seq': match.group(1)}


