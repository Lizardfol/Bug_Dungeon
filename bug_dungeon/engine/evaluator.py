
EXPECTED_PLAINTEXT_FRAGMENT = "KEY=GOBLIN"

def evaluate(level_module):
    """Return (success: bool, message: str)"""
    if not hasattr(level_module, 'ciphertext'):
        return False, 'ciphertext variable missing.'
    if not hasattr(level_module, 'decrypt'):
        return False, 'decrypt function missing.'
    try:
        result = level_module.decrypt(level_module.ciphertext)
    except Exception as e:
        return False, f'decrypt() raised: {e}'
    if not isinstance(result, str):
        return False, 'decrypt() should return a string.'
    if EXPECTED_PLAINTEXT_FRAGMENT in result.upper():
        return True, 'You found the key! Onwards to the next chamber (to be built)...'
    else:
        return False, 'decrypt() returned incorrect plaintext.'
