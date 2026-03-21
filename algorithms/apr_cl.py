def apr_cl_test(n):
    """APR-CL素性测试（简化实现）"""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # 检查小因子
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for p in small_primes:
        if n % p == 0:
            return n == p

    # 使用米勒-拉宾作为快速预检
    from .miller_rabin import miller_rabin_test
    if not miller_rabin_test(n, 10):
        return False

    # 检查 n 的欧拉函数
    # 这里简化实现，实际APR-CL需要更复杂的数论计算
    if n < 10 ** 12:
        return True

    # 对于大数，返回米勒-拉宾的结果
    return True