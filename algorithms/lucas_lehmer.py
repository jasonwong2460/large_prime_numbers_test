import gmpy2


def lucas_lehmer_test(n):
    """卢卡斯-莱默测试（专门用于梅森数）"""
    # 检查 n+1 是否为2的幂
    m = n + 1
    if m & (m - 1) != 0:
        return False

    # 获取指数 p
    p = int(gmpy2.log2(m))
    if p == 2:
        return True

    # 卢卡斯-莱默测试
    s = 4
    M = (1 << p) - 1

    for _ in range(p - 2):
        s = (s * s - 2) % M

    return s == 0