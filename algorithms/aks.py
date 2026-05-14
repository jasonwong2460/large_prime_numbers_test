import gmpy2
import math


def aks_test(n):
    """
    AKS素性测试算法
    参数n: 待测试的正整数
    返回: True表示素数，False表示合数
    """
    if n <= 1:
        return False
    if n <= 3:
        return True

    # 大于12位用gmpy2内置素性测试
    if n.bit_length() > 12:
        return gmpy2.is_prime(n)

    # 第1步：检查n是否为完全幂
    if is_perfect_power(n):
        return False

    # 第2步：寻找合适的r
    r = find_r(n)

    # 第3步：检查小因子
    for a in range(2, min(r, n)):
        if math.gcd(a, n) > 1:
            return False

    # 第4步：多项式测试
    if n <= r:
        return True

    phi_r = euler_phi(r)
    max_a = int(2 * math.sqrt(phi_r) * math.log2(n))

    for a in range(1, max_a + 1):
        if not polynomial_test(n, a, r):
            return False

    return True


def is_perfect_power(n):
    """检查n是否为a^b形式（b≥2）"""
    for b in range(2, int(math.log2(n)) + 1):
        a = int(round(n ** (1.0 / b)))
        if a ** b == n:
            return True
    return False


def find_r(n):
    """
    找到最小的r，使得ord_r(n) > log2(n)^2
    且r与n互质
    """
    max_k = int(math.log2(n) ** 2)

    r = 2
    while True:
        if math.gcd(r, n) == 1:
            # 计算n模r的阶
            order = multiplicative_order(n, r)
            if order > max_k:
                return r
        r += 1


def multiplicative_order(a, m):
    """
    计算a模m的乘法阶
    前提：gcd(a,m)=1
    """
    if math.gcd(a, m) != 1:
        return -1

    # 欧拉函数的上界
    phi = euler_phi(m)

    # 寻找最小的d使得a^d ≡ 1 (mod m)
    for d in range(1, phi + 1):
        if gmpy2.powmod(a, d, m) == 1:
            return d
    return phi


def euler_phi(n):
    """计算欧拉函数φ(n)"""
    result = n
    p = 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            result -= result // p
        p += 1
    if n > 1:
        result -= result // n
    return result


def polynomial_test(n, a, r):
    """
    核心多项式测试：
    检查 (x + a)^n ≡ x^n + a (mod x^r - 1, n)
    """
    # 计算 (x + a)^n mod (x^r - 1) 的系数（模n）
    poly = [0] * r
    poly[0] = 1  # 初始多项式为1

    # 使用快速幂计算 (x + a)^n
    exponent = n
    base = [0] * r
    base[0] = a  # x + a 的表示：[a, 1, 0, 0, ...]
    base[1] = 1

    while exponent > 0:
        if exponent & 1:
            poly = poly_multiply(poly, base, r, n)
        base = poly_multiply(base, base, r, n)
        exponent >>= 1

    # 检查是否等于 x^n + a
    # x^n mod (x^r - 1) 相当于 x^(n mod r)
    poly_expected = [0] * r
    poly_expected[0] = a % n
    poly_expected[n % r] = (poly_expected[n % r] + 1) % n

    # 比较系数
    return poly == poly_expected


def poly_multiply(p, q, r, mod):
    """
    多项式乘法模 (x^r - 1) 和模 mod
    返回：p * q mod (x^r - 1) 的系数列表（长度为r）
    """
    result = [0] * r

    for i in range(r):
        if p[i] == 0:
            continue
        for j in range(r):
            if q[j] == 0:
                continue
            # 注意指数取模r
            idx = (i + j) % r
            result[idx] = (result[idx] + p[i] * q[j]) % mod

    return result