import gmpy2
import math


def aks_test(n):
    """AKS素性测试（简化实现）"""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # 检查是否为完全幂
    for b in range(2, int(math.log2(n)) + 1):
        a = gmpy2.iroot(n, b)
        if a[1]:
            return False

    # 找到最小的 r
    max_r = int(math.log2(n) ** 2)
    r = 2
    while r < max_r:
        if gmpy2.gcd(n, r) != 1:
            if r < n and n % r == 0:
                return False
            r += 1
            continue

        found = True
        for k in range(1, int(math.log2(n) ** 2) + 1):
            if gmpy2.powmod(r, k, n) == 1 % n:
                found = False
                break
        if found:
            break
        r += 1

    # 检查 a 从 1 到 sqrt(phi(r)) * log2(n)
    phi_r = r - 1
    limit = int(math.sqrt(phi_r) * math.log2(n))

    for a in range(1, limit + 1):
        if gmpy2.gcd(a, n) != 1:
            return False

    return True