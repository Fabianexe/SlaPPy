import re


def create_pattern(pattern, dna=False):
    ut = 'T' if dna else 'U'
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
    
    
def search(search_string, sequence):
    pattern = create_pattern(search_string)
    for match in re.finditer(pattern, sequence, flags=re.IGNORECASE):
        yield {'from': match.span()[0], 'to': match.span()[0] + len(match.group(1)), 'seq': match.group(1)}


