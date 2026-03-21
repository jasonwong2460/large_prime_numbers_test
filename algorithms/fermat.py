import gmpy2
import random


def fermat_test(n, k=10):
    """费马素性测试"""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    for _ in range(k):
        a = random.randint(2, n - 2)
        if gmpy2.powmod(a, n - 1, n) != 1:
            return False
    return True