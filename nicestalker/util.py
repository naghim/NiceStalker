def is_partial_match(haystacks, needles):
    for haystack in haystacks:
        if not haystack:
            continue
        
        haystack = str(haystack).lower()

        for needle in needles:
            if str(needle).lower() in haystack:
                return True
    
    return False