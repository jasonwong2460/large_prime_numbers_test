import math
import gmpy2


def trial_division_test(n):
    """试除法 - 48位以内用试除法，大于48位用gmpy2"""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # 48位以内用试除法
    if n.bit_length() <= 48:
        limit = int(math.isqrt(n))
        for i in range(3, limit + 1, 2):
            if n % i == 0:
                return False
        return True
    else:
        # 大于48位用gmpy2内置素性测试
        return gmpy2.is_prime(n)