def match_pattern(pattern, namespace):
    """
    Supports:
        * → single token wildcard
        # → multi token wildcard
    """
    p_parts = pattern.strip("/").split("/")
    n_parts = namespace.strip("/").split("/")

    def recurse(pi, ni):
        while pi < len(p_parts):
            if p_parts[pi] == "#":
                return True
            if ni >= len(n_parts):
                return False
            if p_parts[pi] != "*" and p_parts[pi] != n_parts[ni]:
                return False
            pi += 1
            ni += 1
        return ni == len(n_parts)

    return recurse(0, 0)
