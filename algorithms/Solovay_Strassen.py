import random
import gmpy2


def solovay_strassen_test(N: int, tests: int = 40) -> bool:
    """
    Solovay-Strassen 概率素性测试

    参数：
        N      : 要测试的整数
        tests  : 测试次数（建议 40~100，次数越多越可靠）

    返回：
        True  → 可能是素数
        False → 一定是合数
    """
    if N < 2:
        return False
    if N == 2 or N == 3:
        return True
    if N % 2 == 0:  # 排除偶数
        return False

    # 快速试除几个小素数（加速）
    for p in [3, 5, 7, 11]:
        if N % p == 0:
            return N == p

    # Solovay-Strassen 概率测试
    for _ in range(tests):
        a = random.randint(2, N - 1)

        if gmpy2.gcd(a, N) > 1:
            return False

        left = gmpy2.powmod(a, N // 2, N)
        right = int(gmpy2.jacobi(a, N)) % N

        if left != right:
            return False

    return True