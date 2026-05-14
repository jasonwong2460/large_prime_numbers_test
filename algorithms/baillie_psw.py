import gmpy2


def jacobi(a, n):
    a %= n
    result = 1
    while a != 0:
        while a % 2 == 0:
            a //= 2
            n_mod_8 = n % 8
            if n_mod_8 in (3, 5):
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a %= n
    if n == 1:
        return result
    else:
        return 0


def miller_rabin(n):
    d = (n - 1) >> 1
    s = 1
    while d & 1 == 0:
        d >>= 1
        s += 1

    def sprp(a):
        a = gmpy2.powmod(a, d, n)
        if a == 1:
            return True
        for r in range(s - 1):
            if a == n - 1:
                return True
            a = (a * a) % n
        return a == n - 1

    return sprp(2)


def D_chooser(n):
    D = 5
    j = jacobi(D, n)

    while j > 0:
        D += 2 if D > 0 else -2
        D *= -1

        if D == -15:
            if gmpy2.is_square(n):
                return (0, 0)

        j = jacobi(D, n)
    return (D, j)


def div2mod(x,n):
    if x & 1:
       return ((x+n)>>1)%n
    return (x>>1)%n


def U_V_subscript(k, n, P, D):
    U = 1
    V = P
    digits = bin(k)[2:]

    for digit in digits[1:]:
        U, V = (U * V) % n, div2mod(V * V + D * U * U, n)

        if digit == '1':
            U, V = div2mod(P * U + V, n), div2mod(D * U + P * V, n)
    return U, V


def lucas_spp(n, D, P, Q):
    assert n & 1

    d = n + 1
    s = 0
    while (d & 1) == 0:
        s += 1
        d >>= 1

    U, V = U_V_subscript(d, n, P, D)
    if U == 0:
        return True

    Q = gmpy2.powmod(Q, d, n)

    for r in range(s):
        if V == 0:
            return True
        V = (V * V - 2 * Q) % n
        Q = gmpy2.powmod(Q, 2, n)

    return False


def baillie_psw_test(n):
    if n <= 1: return False
    if n & 1 == 0:
        return n == 2

    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
              53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]:
        if n % p == 0:
            return n == p

    if not miller_rabin(n):
        return False

    D, j = D_chooser(n)
    if j == 0:
        return False

    return lucas_spp(n, D, 1, (1 - D) // 4)