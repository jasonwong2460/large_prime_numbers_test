import gmpy2

# 小素数底数列表
BASES = [2, 3, 5, 7, 11, 13, 17, 19]


def fermat_optimized_test(n):
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    bits = n.bit_length()

    if bits <= 32:
        # 小数字：测试前3个底数
        for a in BASES[:3]:
            if a >= n:
                break
            if gmpy2.powmod(a, n - 1, n) != 1:
                return False
        return True
    elif bits <= 256:
        # 中等数字：测试前5个底数
        for a in BASES[:5]:
            if a >= n:
                break
            if gmpy2.powmod(a, n - 1, n) != 1:
                return False
        return True
    else:
        # 大数字：测试全部底数
        for a in BASES:
            if a >= n:
                break
            if gmpy2.powmod(a, n - 1, n) != 1:
                return False
        return True