import copy
from math import gcd
import gmpy2


# 简单的素数检测函数（试除法）
def isprime_slow(n):
    """判断 n 是否为素数，使用简单的试除法"""
    if n < 2:
        return False
    elif n == 2 or n == 3:
        return True
    elif n % 2 == 0:
        return False
    else:
        i = 3
        while i * i <= n:
            if n % i == 0:
                return False
            i += 2
    return True


# 计算 q 整除 t 的次数（即 t 中因子 q 的指数）
def v(q, t):
    """返回 t 能被 q 整除的次数（即 t 中质因子 q 的指数）"""
    ans = 0
    while (t % q == 0):
        ans += 1
        t //= q
    return ans


# 质因数分解
def prime_factorize(n):
    """对 n 进行质因数分解，返回列表 [(p1, k1), (p2, k2), ...]"""
    ret = []
    p = 2
    while p * p <= n:
        if n % p == 0:
            num = 0
            while n % p == 0:
                num += 1
                n //= p
            ret.append((p, num))
        p += 1

    if n != 1:
        ret.append((n, 1))

    return ret


# 计算 e(t) 函数，返回 e(t) 和对应的 q 列表
def e(t):
    """
    计算 APR 算法中的 e(t) 值
    e(t) = 2 * ∏_{q: q-1|t, q为素数} q^(1 + v(q, t))
    返回 (e(t), q_list)
    """
    s = 1
    q_list = []
    for q in range(2, t + 2):
        if t % (q - 1) == 0 and isprime_slow(q):
            s *= q ** (1 + v(q, t))
            q_list.append(q)
    return 2 * s, q_list


# JacobiSum 类（用于表示分圆域中的 Jacobi和）
class JacobiSum(object):
    """JacobiSum 类，用于表示和计算 JacobiSum"""

    def __init__(self, p, k, q):
        """初始化，p^k 是模数，q 是另一个素数"""
        self.p = p
        self.k = k
        self.q = q
        self.m = (p - 1) * p ** (k - 1)  # 阶的长度
        self.pk = p ** k  # p^k
        self.coef = [0] * self.m  # 系数数组

    # 返回单位元
    def one(self):
        """返回 JacobiSum 的单位元（即值为 1 的 JacobiSum）"""
        self.coef[0] = 1
        for i in range(1, self.m):
            self.coef[i] = 0
        return self

    # JacobiSum 的乘法
    def mul(self, jac):
        """两个 JacobiSum 相乘"""
        m = self.m
        pk = self.pk
        j_ret = JacobiSum(self.p, self.k, self.q)
        for i in range(m):
            for j in range(m):
                if (i + j) % pk < m:
                    j_ret.coef[(i + j) % pk] += self.coef[i] * jac.coef[j]
                else:
                    r = (i + j) % pk - self.p ** (self.k - 1)
                    while r >= 0:
                        j_ret.coef[r] -= self.coef[i] * jac.coef[j]
                        r -= self.p ** (self.k - 1)

        return j_ret

    # 重载乘法运算符 *
    def __mul__(self, right):
        """支持 JacobiSum * JacobiSum 和 JacobiSum * 整数"""
        if type(right) is int:
            # 与整数相乘
            j_ret = JacobiSum(self.p, self.k, self.q)
            for i in range(self.m):
                j_ret.coef[i] = self.coef[i] * right
            return j_ret
        else:
            # 与 JacobiSum 相乘
            return self.mul(right)

    # 模幂运算（x 次幂，模 n）
    def modpow(self, x, n):
        """计算 self 的 x 次幂，并对系数模 n"""
        j_ret = JacobiSum(self.p, self.k, self.q)
        j_ret.coef[0] = 1
        j_a = copy.deepcopy(self)
        while x > 0:
            if x % 2 == 1:
                j_ret = (j_ret * j_a).mod(n)
            j_a = j_a * j_a
            j_a.mod(n)
            x //= 2
        return j_ret

    # 对所有系数取模 n
    def mod(self, n):
        """对 JacobiSum 的所有系数模 n"""
        for i in range(self.m):
            self.coef[i] %= n
        return self

    # 作用 sigma_x 算子
    def sigma(self, x):
        """应用 sigma_x 算子（乘法作用）"""
        m = self.m
        pk = self.pk
        j_ret = JacobiSum(self.p, self.k, self.q)
        for i in range(m):
            if (i * x) % pk < m:
                j_ret.coef[(i * x) % pk] += self.coef[i]
            else:
                r = (i * x) % pk - self.p ** (self.k - 1)
                while r >= 0:
                    j_ret.coef[r] -= self.coef[i]
                    r -= self.p ** (self.k - 1)
        return j_ret

    # 作用 sigma_x 的逆算子
    def sigma_inv(self, x):
        """应用 sigma_x 的逆算子 = sigma_{x^{-1}}"""
        # 计算 x 模 pk 的逆元
        x_inv = pow(x, -1, self.pk)
        return self.sigma(x_inv)

    # 判断 self 是否为 N 次单位根，若是则返回指数 h
    def is_root_of_unity(self, N):
        """
        判断当前 JacobiSum 是否为模 N 的单位根
        返回 (是否为单位根, 指数 h)
        """
        m = self.m
        p = self.p
        k = self.k

        # h < m
        one = 0
        for i in range(m):
            if self.coef[i] == 1:
                one += 1
                h = i
            elif self.coef[i] == 0:
                continue
            elif (self.coef[i] - (-1)) % N != 0:
                return False, None
        if one == 1:
            return True, h

        # h >= m
        for i in range(m):
            if self.coef[i] != 0:
                break
        r = i % (p ** (k - 1))
        for i in range(m):
            if i % (p ** (k - 1)) == r:
                if (self.coef[i] - (-1)) % N != 0:
                    return False, None
            else:
                if self.coef[i] != 0:
                    return False, None

        return True, (p - 1) * p ** (k - 1) + r


# 找到模 q 的最小原根
def smallest_primitive_root(q):
    """返回模素数 q 的最小原根"""
    for r in range(2, q):
        s = set({})
        m = 1
        for i in range(1, q):
            m = (m * r) % q
            s.add(m)
        if len(s) == q - 1:
            return r
    return None


# 计算函数 f_q(x)
def calc_f(q):
    """
    计算离散对数函数 f_q(x)，满足 g^f(x) ≡ 1 - g^x (mod q)
    其中 g 是模 q 的原根
    """
    g = smallest_primitive_root(q)
    m = {}
    for x in range(1, q - 1):
        m[pow(g, x, q)] = x
    f = {}
    for x in range(1, q - 1):
        f[x] = m[(1 - pow(g, x, q)) % q]

    return f


# 计算 Σ ζ^(a*x + b*f(x))
def calc_J_ab(p, k, q, a, b):
    """计算J_{a,b} = Σ ζ^(a*x + b*f(x))"""
    j_ret = JacobiSum(p, k, q)
    f = calc_f(q)
    for x in range(1, q - 1):
        pk = p ** k
        if (a * x + b * f[x]) % pk < j_ret.m:
            j_ret.coef[(a * x + b * f[x]) % pk] += 1
        else:
            r = (a * x + b * f[x]) % pk - p ** (k - 1)
            while r >= 0:
                j_ret.coef[r] -= 1
                r -= p ** (k - 1)
    return j_ret


# 计算 J(p, q)（适用于 p>=3 或 p=q=2）
def calc_J(p, k, q):
    """计算标准 JacobiSum J(p,q) = J_{1,1}"""
    return calc_J_ab(p, k, q, 1, 1)


# 计算 J_3(q)（用于 p=2 且 k>=3 的情况）
def calc_J3(p, k, q):
    """计算 J3(q) = J(2,q) * J_{2,1}"""
    j2q = calc_J(p, k, q)
    j21 = calc_J_ab(p, k, q, 2, 1)
    j_ret = j2q * j21
    return j_ret


# 计算 J_2(q)（用于 p=2 且 k>=3 的情况）
def calc_J2(p, k, q):
    """计算 J2(q) 用于修正项"""
    j31 = calc_J_ab(2, 3, q, 3, 1)
    j_conv = JacobiSum(p, k, q)
    for i in range(j31.m):
        j_conv.coef[i * (p ** k) // 8] = j31.coef[i]
    j_ret = j_conv * j_conv
    return j_ret


# 步骤 4a：p >= 3 的情况
def APRtest_step4a(p, k, q, N):
    """APR 算法第4步，适用于 p >= 3"""
    J = calc_J(p, k, q)

    # 初始化 s1 = 1
    s1 = JacobiSum(p, k, q).one()

    # 计算 J^Θ
    for x in range(p ** k):
        if x % p == 0:
            continue
        t = J.sigma_inv(x)
        t = t.modpow(x, N)
        s1 = s1 * t
        s1.mod(N)

    # r = N mod p^k
    r = N % (p ** k)

    # s2 = s1 ^ (N / p^k)
    s2 = s1.modpow(N // (p ** k), N)

    # 计算 J^α
    J_alpha = JacobiSum(p, k, q).one()
    for x in range(p ** k):
        if x % p == 0:
            continue
        t = J.sigma_inv(x)
        t = t.modpow((r * x) // (p ** k), N)
        J_alpha = J_alpha * t
        J_alpha.mod(N)

    # S = s2 * J_alpha
    S = (s2 * J_alpha).mod(N)

    # 判断 S 是否为单位根
    exist, h = S.is_root_of_unity(N)

    if not exist:
        # 合数
        return False, None
    else:
        # 可能是素数
        if h % p != 0:
            l_p = 1
        else:
            l_p = 0
        return True, l_p


# 步骤 4b：p=2 且 k>=3 的情况
def APRtest_step4b(p, k, q, N):
    """APR 算法第4步，适用于 p=2 且 k>=3"""
    J = calc_J3(p, k, q)

    # 初始化 s1 = 1
    s1 = JacobiSum(p, k, q).one()

    # 计算 J3^Θ
    for x in range(p ** k):
        if x % 8 not in [1, 3]:
            continue
        t = J.sigma_inv(x)
        t = t.modpow(x, N)
        s1 = s1 * t
        s1.mod(N)

    # r = N mod p^k
    r = N % (p ** k)

    # s2 = s1 ^ (N / p^k)
    s2 = s1.modpow(N // (p ** k), N)

    # 计算 J3^α
    J_alpha = JacobiSum(p, k, q).one()
    for x in range(p ** k):
        if x % 8 not in [1, 3]:
            continue
        t = J.sigma_inv(x)
        t = t.modpow((r * x) // (p ** k), N)
        J_alpha = J_alpha * t
        J_alpha.mod(N)

    # S = s2 * J_alpha * J2^δ
    if N % 8 in [1, 3]:
        S = (s2 * J_alpha).mod(N)
    else:
        J2_delta = calc_J2(p, k, q)
        S = (s2 * J_alpha * J2_delta).mod(N)

    # 判断 S 是否为单位根
    exist, h = S.is_root_of_unity(N)

    if not exist:
        # 合数
        return False, None
    else:
        # 可能是素数
        if h % p != 0 and (pow(q, (N - 1) // 2, N) + 1) % N == 0:
            l_p = 1
        else:
            l_p = 0
        return True, l_p


# 步骤 4c：p=2 且 k=2 的情况
def APRtest_step4c(p, k, q, N):
    """APR 算法第4步，适用于 p=2 且 k=2"""
    J2q = calc_J(p, k, q)

    # s1 = J(2,q)^2 * q (模 N)
    s1 = (J2q * J2q * q).mod(N)

    # s2 = s1 ^ (N/4)
    s2 = s1.modpow(N // 4, N)

    if N % 4 == 1:
        S = s2
    elif N % 4 == 3:
        S = (s2 * J2q * J2q).mod(N)
    else:
        print("错误")

    # 判断 S 是否为单位根
    exist, h = S.is_root_of_unity(N)

    if not exist:
        # 合数
        return False, None
    else:
        # 可能是素数
        if h % p != 0 and (pow(q, (N - 1) // 2, N) + 1) % N == 0:
            l_p = 1
        else:
            l_p = 0
        return True, l_p


# 步骤 4d：p=2 且 k=1 的情况
def APRtest_step4d(p, k, q, N):
    """APR 算法第4步，适用于 p=2 且 k=1"""
    S2q = pow(-q, (N - 1) // 2, N)
    if (S2q - 1) % N != 0 and (S2q + 1) % N != 0:
        # 合数
        return False, None
    else:
        # 可能是素数
        if (S2q + 1) % N == 0 and (N - 1) % 4 == 0:
            l_p = 1
        else:
            l_p = 0
        return True, l_p


# 第4步的总入口
def APRtest_step4(p, k, q, N):
    """根据 p 和 k 的值选择对应的第4步子步骤"""
    if p >= 3:
        result, l_p = APRtest_step4a(p, k, q, N)
    elif p == 2 and k >= 3:
        result, l_p = APRtest_step4b(p, k, q, N)
    elif p == 2 and k == 2:
        result, l_p = APRtest_step4c(p, k, q, N)
    elif p == 2 and k == 1:
        result, l_p = APRtest_step4d(p, k, q, N)
    else:
        print("错误")

    return result, l_p


# APR 素数测试主函数
def APRtest(N):
    """
    APR（Adleman-Pomerance-Rumely）素数测试主函数
    输入：整数 N
    输出：True 表示 N 是素数，False 表示 N 是合数
    """
    # 预定义的 t 值列表
    t_list = [2, 12, 60, 180, 840, 1260, 1680, 2520, 5040, 15120, 55440, 110880, 720720, 1441440, 4324320,
              24504480, 73513440]

    if N == 2 or N == 3:
        return True

    if N.bit_length() > 1024:
        return gmpy2.is_prime(N)

    # 选择合适的 t
    for t in t_list:
        et, q_list = e(t)
        if N < et * et:
            break
    else:
        return False

    # 第1步：检查 gcd(t * e(t), N)
    g = gcd(t * et, N)
    if g > 1:
        return False

    # 第2步：初始化 l_p
    l = {}
    fac_t = prime_factorize(t)
    for p, k in fac_t:
        if p >= 3 and pow(N, p - 1, p * p) != 1:
            l[p] = 1
        else:
            l[p] = 0

    # 第3步和第4步：对每个 q 进行测试
    for q in q_list:
        if q == 2:
            continue
        fac = prime_factorize(q - 1)
        for p, k in fac:
            # 第4步
            result, l_p = APRtest_step4(p, k, q, N)
            if not result:
                # 合数
                return False
            elif l_p == 1:
                l[p] = 1

    # 第5步：处理尚未满足条件的 p
    for p, value in l.items():
        if value == 0:
            # 尝试其他 (p, q) 对
            count = 0
            i = 1
            found = False
            # 最多尝试30次
            while count < 30:
                q = p * i + 1
                if N % q != 0 and isprime_slow(q) and (q not in q_list):
                    count += 1
                    k = v(p, q - 1)
                    # 第4步
                    result, l_p = APRtest_step4(p, k, q, N)
                    if not result:
                        # 合数
                        return False
                    elif l_p == 1:
                        found = True
                        break
                i += 1
            if not found:
                return False

    # 第6步：最终验证
    r = 1
    for t in range(t - 1):
        r = (r * N) % et
        if r != 1 and r != N and N % r == 0:
            return False
    # 通过所有测试，是素数！
    return True