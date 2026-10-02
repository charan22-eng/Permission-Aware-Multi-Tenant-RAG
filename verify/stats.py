import math

def wilson_score_interval(successes, n, z=1.96):
    """
    Computes the Wilson Score Interval for a proportion.
    Returns (lower_bound, upper_bound).
    """
    if n == 0:
        return (0.0, 0.0)
        
    p = successes / n
    denominator = 1 + z**2 / n
    center = p + z**2 / (2 * n)
    spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)
    
    lower = (center - spread) / denominator
    upper = (center + spread) / denominator
    
    return (lower, upper)

if __name__ == "__main__":
    # Simple unit test
    l, u = wilson_score_interval(58, 60)
    print(f"58/60: 95% CI = [{l:.3f}, {u:.3f}]")
    assert 0.88 < l < 0.90
    assert 0.98 < u < 1.00
    
    l, u = wilson_score_interval(0, 10)
    print(f"0/10: 95% CI = [{l:.3f}, {u:.3f}]")
    assert l == 0.0
    assert 0.25 < u < 0.35
    print("Tests passed.")
