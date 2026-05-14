import gmpy2
import random
import streamlit as st

def generate_test_numbers():
    """生成测试数据集"""
    st.sidebar.header("📊 测试数据集生成")

    # 随机数生成参数
    bits_options = st.sidebar.multiselect(
        "选择位数",
        [4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 256, 384, 512, 640, 768, 896, 1024],
        default=[256, 512]
    )

    count_per_bit = st.sidebar.number_input(
        "每个位数的数量",
        min_value=10,
        max_value=200,
        value=50,
        step=10
    )

    generate_btn = st.sidebar.button("生成测试数据")

    test_numbers = {
        'primes': [],
        'composites': [],
        'special': []
    }

    if generate_btn:
        with st.spinner("生成测试数据中..."):
            # 生成素数和合数
            for bits in bits_options:
                # 生成素数 (记录位数信息)
                for _ in range(count_per_bit):
                    prime = gmpy2.next_prime(gmpy2.mpz(random.getrandbits(bits)))
                    test_numbers['primes'].append((int(prime), bits))

                # 生成合数 (记录位数信息)
                for _ in range(count_per_bit):
                    p1 = gmpy2.next_prime(gmpy2.mpz(random.getrandbits(bits // 2)))
                    p2 = gmpy2.next_prime(gmpy2.mpz(random.getrandbits(bits // 2)))
                    composite = p1 * p2
                    test_numbers['composites'].append((int(composite), bits))

            # 特殊测试用例
            special_cases = generate_special_cases()
            test_numbers['special'] = special_cases

            st.session_state.test_numbers = test_numbers
            st.sidebar.success(f"已生成 {len(test_numbers['primes'])} 个素数, "
                               f"{len(test_numbers['composites'])} 个合数, "
                               f"{len(test_numbers['special'])} 个特殊数")

    return test_numbers


def generate_special_cases():
    """生成特殊测试用例 - 支持256/512位大数"""
    special = []

    # ========== 1. 卡迈克尔数 ==========
    carmichael_pool = []
    small_carmichael = [
        561, 1105, 1729, 2465, 2821, 6601, 8911, 10585, 15841, 29341,
        41041, 46657, 52633, 62745, 63973, 75361, 101101, 115921, 126217, 162401,
        172081, 188461, 252601, 278545, 294409, 314821, 334153, 340561, 399001, 410041,
        449065, 488881, 512461, 530881, 552721, 656601, 658801, 670033, 748657, 825265,
        838201, 852841, 997633, 1033669, 1082809, 1152271, 1193221, 1461241, 1569457, 1615681
    ]
    carmichael_pool.extend(small_carmichael)
    carmichael_pool.extend(generate_carmichael_by_bits(256, count=10))
    carmichael_pool.extend(generate_carmichael_by_bits(512, count=10))

    carmichael_sample = random.sample(carmichael_pool, min(20, len(carmichael_pool)))
    for n in carmichael_sample:
        special.append((n, "卡迈克尔数"))

    # ========== 2. 强伪素数 ==========
    pseudoprime_pool = []
    small_pseudoprime = [
        2047, 3277, 4033, 4681, 8321, 15841, 29341, 42799, 49141, 52633,
        65281, 74665, 80581, 85489, 88357, 90751, 104653, 130561, 196093, 220729,
        233017, 252601, 253241, 256999, 258511, 271361, 288961, 294409, 306613, 316201,
        318361, 342271, 348161, 355441, 357761, 361801, 390937, 403201, 406681, 413641
    ]
    pseudoprime_pool.extend(small_pseudoprime)
    pseudoprime_pool.extend(generate_pseudoprime_by_bits(256, count=10))
    pseudoprime_pool.extend(generate_pseudoprime_by_bits(512, count=10))

    pseudoprime_sample = random.sample(pseudoprime_pool, min(20, len(pseudoprime_pool)))
    for n in pseudoprime_sample:
        special.append((n, "强伪素数"))

    # ========== 3. 梅森数 ==========
    mersenne_exponents = [
        2, 3, 5, 7, 13, 17, 19, 31, 61, 89,
        107, 127, 521, 607, 1279, 2203, 2281, 3217, 4253, 4423
    ]
    for exp in mersenne_exponents[:20]:
        mersenne = (1 << exp) - 1
        special.append((mersenne, "梅森数"))

    return special


def generate_carmichael_by_bits(target_bits, count=10):
    carmichael_list = []
    target_value = 2 ** target_bits
    k_estimate = int((target_value / 1296) ** (1 / 3))
    search_range = max(100000, int(k_estimate * 0.1))
    start_k = max(1, k_estimate - search_range)
    end_k = k_estimate + search_range

    for k in range(start_k, end_k, max(1, search_range // 100)):
        p = 6 * k + 1
        q = 12 * k + 1
        r = 18 * k + 1
        if gmpy2.is_prime(p) and gmpy2.is_prime(q) and gmpy2.is_prime(r):
            carmichael = p * q * r
            bits = carmichael.bit_length()
            if abs(bits - target_bits) <= 20:
                carmichael_list.append(carmichael)
                if len(carmichael_list) >= count:
                    break
    return carmichael_list


def generate_pseudoprime_by_bits(target_bits, count=10):
    pseudoprime_list = []
    attempts = 0
    max_attempts = 5000

    while len(pseudoprime_list) < count and attempts < max_attempts:
        attempts += 1
        bits_half = target_bits // 2
        bits_p = bits_half + random.randint(-10, 10)
        bits_q = target_bits - bits_p

        p = gmpy2.next_prime(random.getrandbits(max(2, bits_p)))
        q = gmpy2.next_prime(random.getrandbits(max(2, bits_q)))
        n = p * q
        bits = n.bit_length()

        if abs(bits - target_bits) <= 20 and is_strong_pseudoprime(n, 2):
            if n not in pseudoprime_list:
                pseudoprime_list.append(n)
    return pseudoprime_list


def is_strong_pseudoprime(n, a=2):
    if gmpy2.is_prime(n):
        return False
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return True
    for _ in range(s - 1):
        x = pow(x, 2, n)
        if x == n - 1:
            return True
    return False