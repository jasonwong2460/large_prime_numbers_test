import gmpy2


def is_perfect_square(n):
    """检查是否为完全平方数"""
    root = gmpy2.isqrt(n)
    return root * root == n


def lucas_sequence(n, P, Q, k):
    """计算卢卡斯序列"""
    U = 1
    V = P
    Qk = Q
    b = bin(k)[3:]

    for bit in b:
        U, V = (U * V) % n, (V * V - 2 * Qk) % n
        Qk = (Qk * Qk) % n
        if bit == '1':
            U, V = (P * U + V) % n, (P * V + 2 * Qk) % n
            Qk = (Qk * Q) % n

    return U, V


def lucas_test(n):
    """卢卡斯素性测试"""
    if n % 2 == 0 or n < 2:
        return False

    # 找到合适的参数 D
    D = 5
    while True:
        if gmpy2.legendre(D, n) != -1:
            break
        D = -D + 2 if D > 0 else -D - 2

    P = 1
    Q = (1 - D) // 4

    # 计算卢卡斯序列
    U, V = lucas_sequence(n, P, Q, n - gmpy2.legendre(D, n))
    return U == 0


def baillie_psw_test(n):
    """Baillie-PSW素性测试"""
    if n < 2:
        return False
    if n == 2:
        return True

    # 检查小因子
    small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29]
    for p in small_primes:
        if n % p == 0:
            return n == p

    # 检查完全平方数
    if is_perfect_square(n):
        return False

    # 米勒-拉宾测试 (基数为2)
    if not miller_rabin_base2(n):
        return False

    # 卢卡斯测试
    return lucas_test(n)


def miller_rabin_base2(n):
    """基数为2的米勒-拉宾测试"""
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    x = gmpy2.powmod(2, d, n)
    if x == 1 or x == n - 1:
        return True

    for _ in range(s - 1):
        x = gmpy2.powmod(x, 2, n)
        if x == n - 1:
            return True
    return False