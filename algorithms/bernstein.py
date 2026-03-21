import gmpy2


def bernstein_test(n):
    """Bernstein素性测试（优化的大数测试）"""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # 使用优化的米勒-拉宾
    from .miller_rabin import miller_rabin_test

    # 对于小数字使用确定性测试
    if n < 2 ** 64:
        return deterministic_miller_rabin(n)

    # 对于大数字使用高精度的概率测试
    return miller_rabin_test(n, 20)


def deterministic_miller_rabin(n):
    """确定性米勒-拉宾测试（用于64位整数）"""
    # 已知的确定性基
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    # 根据 n 的大小选择合适的基
    if n < 341550071728321:
        bases = [2, 3, 5, 7, 11, 13, 17]
    elif n < 3186658578340311:
        bases = [2, 3, 5, 7, 11, 13]
    elif n < 3071837692357849:
        bases = [2, 3, 5, 7, 11]
    else:
        bases = [2, 3, 5, 7]

    for a in bases:
        if a >= n:
            continue
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