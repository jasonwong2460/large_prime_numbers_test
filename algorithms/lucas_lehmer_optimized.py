import gmpy2


def lucas_lehmer_optimized_test(n):
    """
    卢卡斯-莱默测试 (底层位运算加速版)
    仅适用于梅森数 n = 2^p - 1
    """
    if n < 3:
        return n == 2

    # 获取数字的二进制位长，即梅森数的指数 p
    p = n.bit_length()

    # 校验数字是否真的是 2^p - 1 形式 (二进制全为1)
    if n != (1 << p) - 1:
        return False

    # 梅森数的指数 p 必须本身是素数
    if not gmpy2.is_prime(p):
        return False

    s = 4
    for _ in range(p - 2):
        sq = s * s

        # 【核心优化】：利用位运算彻底替代耗时的大数取模 sq % n
        # 数学原理：设 sq = A * 2^p + B。因为 2^p ≡ 1 (mod 2^p - 1)
        # 所以 sq ≡ A + B (mod 2^p - 1)
        # (sq & n) 取出低 p 位 (即 B)
        # (sq >> p) 取出高位 (即 A)
        s = (sq & n) + (sq >> p)

        # 修正可能溢出的部分
        if s >= n:
            s -= n

        s -= 2

        # 修正可能出现负数的情况
        if s < 0:
            s += n

    return s == 0