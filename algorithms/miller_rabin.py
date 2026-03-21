import gmpy2
import random


def miller_rabin_test(n, k=10):
    """米勒-拉宾素性测试"""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # 将 n-1 写成 d * 2^s 的形式
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(k):
        a = random.randint(2, n - 2)
        x = gmpy2.powmod(a, d, n)
        if x == 1 or x == n - 1:
            continue

        for _ in range(s - 1):
            x = gmpy2.powmod(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True