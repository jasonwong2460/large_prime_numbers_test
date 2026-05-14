import math
import gmpy2


# 预生成100万以内所有质数（78498个质数）
def _generate_primes(limit=1000000):
    """埃氏筛生成质数表"""
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    return [i for i, is_p in enumerate(sieve) if is_p]


_PRIMES = _generate_primes(1000000)  # 78498个质数


def trial_division_optimized_test(n):
    """试除法 - 只检查质数"""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False

    bits = n.bit_length()

    # 大数字用gmpy2
    if bits > 48:
        return gmpy2.is_prime(n)

    limit = int(math.isqrt(n))

    # 只用质数试除
    for p in _PRIMES:
        if p > limit:
            return True
        if n % p == 0:
            return n == p

    # 超过质数表范围，继续用6k±1
    max_p = _PRIMES[-1]
    # 找到大于 max_p 的第一个 6k-1 形式的数（即模6余5）
    i = max_p + 1
    while i % 6 != 5:
        i += 1
    # 现在 i 是 6k-1, i+2 是 6k+1
    while i <= limit:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True