import streamlit as st
import gmpy2
import pandas as pd
import numpy as np
import time
import psutil
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime
import random
import sys
import os

# 添加算法模块路径
sys.path.append(os.path.dirname(__file__))
from algorithms import *

# 页面配置
st.set_page_config(
    page_title="素性测试算法对比评测",
    page_icon="🔢",
    layout="wide"
)

matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']

# 初始化会话状态
if 'test_results' not in st.session_state:
    st.session_state.test_results = []
if 'algorithm_times' not in st.session_state:
    st.session_state.algorithm_times = {}
if 'algorithm_memory' not in st.session_state:
    st.session_state.algorithm_memory = {}
if 'test_numbers' not in st.session_state:
    st.session_state.test_numbers = None


class PerformanceMonitor:
    """性能监控类"""

    @staticmethod
    def measure_memory(func):
        """装饰器：测量内存使用"""
        def wrapper(*args, **kwargs):
            process = psutil.Process()
            mem_before = process.memory_info().rss / 1024 / 1024  # MB
            result = func(*args, **kwargs)
            mem_after = process.memory_info().rss / 1024 / 1024
            mem_used = mem_after - mem_before
            return result, mem_used
        return wrapper

    @staticmethod
    def measure_time(func):
        """装饰器：测量执行时间"""
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            return result, elapsed
        return wrapper


def generate_test_numbers():
    """生成测试数据集"""
    st.sidebar.header("📊 测试数据集生成")

    # 随机数生成参数
    bits_options = st.sidebar.multiselect(
        "选择位数",
        [256, 512, 1024],
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
        with st.spinner("生成测试数据中..."): # type: ignore
            # 生成素数和合数
            for bits in bits_options:
                # 生成素数
                for _ in range(count_per_bit):
                    prime = gmpy2.next_prime(gmpy2.mpz(random.getrandbits(bits)))
                    test_numbers['primes'].append(int(prime))

                # 生成合数
                for _ in range(count_per_bit):
                    p1 = gmpy2.next_prime(gmpy2.mpz(random.getrandbits(bits // 2)))
                    p2 = gmpy2.next_prime(gmpy2.mpz(random.getrandbits(bits // 2)))
                    composite = p1 * p2
                    test_numbers['composites'].append(int(composite))

            # 特殊测试用例
            special_cases = generate_special_cases()
            test_numbers['special'] = special_cases

            st.session_state.test_numbers = test_numbers
            st.sidebar.success(f"已生成 {len(test_numbers['primes'])} 个素数, "
                               f"{len(test_numbers['composites'])} 个合数, "
                               f"{len(test_numbers['special'])} 个特殊数")

    return test_numbers


def generate_special_cases():
    """生成特殊测试用例"""
    special = []

    # 卡迈克尔数
    carmichael = [
        561, 1105, 1729, 2465, 2821, 6601, 8911, 10585, 15841, 29341,
        41041, 46657, 52633, 62745, 63973, 75361, 101101, 115921, 126217, 162401
    ]
    for n in carmichael[:20]:
        special.append((n, "卡迈克尔数"))

    # 强伪素数
    strong_pseudoprime = [
        2047, 3277, 4033, 4681, 8321, 15841, 29341, 42799, 49141, 52633,
        65281, 74665, 80581, 85489, 88357, 90751, 104653, 130561, 196093, 220729
    ]
    for n in strong_pseudoprime[:20]:
        special.append((n, "强伪素数"))

    # 梅森数
    mersenne_exponents = [
        2, 3, 5, 7, 13, 17, 19, 31, 61, 89,
        107, 127, 521, 607, 1279, 2203, 2281, 3217, 4253, 4423
    ]
    for exp in mersenne_exponents[:20]:
        mersenne = (1 << exp) - 1
        special.append((mersenne, "梅森数"))

    return special


def run_algorithm_test(algorithm_name, algorithm_func, numbers, test_type):
    """运行单个算法的测试"""
    results = []
    times = []
    memories = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, num in enumerate(numbers):
        # 关键修改：判断是否为元组，如果是则提取具体类型
        if isinstance(num, tuple):
            num_val, special_type = num
            actual_test_type = special_type  # 使用具体的特殊数类型
        else:
            num_val = num
            actual_test_type = test_type  # 使用传入的普通类型

        status_text.text(f"测试 {algorithm_name} - {i + 1}/{len(numbers)}: {str(num_val)[:50]}...")

        # 直接测量时间和内存
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024
        start_time = time.time()

        result = algorithm_func(num_val)

        elapsed = time.time() - start_time
        mem_after = process.memory_info().rss / 1024 / 1024
        mem_used = max(0, mem_after - mem_before)

        results.append({
            'number': num_val,
            'is_prime': result,
            'time': elapsed,
            'memory': mem_used,
            'test_type': actual_test_type  # 使用具体类型
        })

        times.append(elapsed)
        memories.append(mem_used)

        progress_bar.progress((i + 1) / len(numbers))

    status_text.text(f"{algorithm_name} 测试完成")
    return results, times, memories


def compare_algorithms():
    """对比所有算法"""
    st.header("🔬 算法性能对比")

    if st.session_state.test_numbers is None:
        st.warning("请先在侧边栏生成测试数据")
        return

    test_numbers = st.session_state.test_numbers

    # 算法列表
    algorithms = {
        "试除法": trial_division_test,
        "费马测试": fermat_test,
        "米勒-拉宾": miller_rabin_test,
        "Baillie-PSW": baillie_psw_test,
        "卢卡斯-莱默": lucas_lehmer_test,
        "AKS": aks_test,
        "APR-CL": apr_cl_test,
        "Bernstein": bernstein_test
    }

    # 选择要测试的算法
    selected_algorithms = st.multiselect(
        "选择要对比的算法",
        list(algorithms.keys()),
        default=list(algorithms.keys())[:3]
    )

    if st.button("开始性能对比测试"):
        all_results = {}
        comparison_data = []
        special_details = {}

        for algo_name in selected_algorithms:
            st.subheader(f"测试 {algo_name}")

            tab1, tab2, tab3, tab4 = st.tabs(["素数测试", "合数测试", "特殊数测试", "特殊数详细统计"])

            with tab1:
                st.write("测试素数")
                results, times, memories = run_algorithm_test(
                    algo_name,
                    algorithms[algo_name],
                    test_numbers['primes'],
                    "素数"
                )
                all_results[f"{algo_name}_primes"] = results
                comparison_data.append({
                    '算法': algo_name,
                    '类型': '素数',
                    '平均时间(秒)': np.mean(times) if times else 0,
                    '最大时间(秒)': np.max(times) if times else 0,
                    '平均内存(MB)': np.mean(memories) if memories else 0,
                    '准确率(%)': 100
                })

            with tab2:
                st.write("测试合数")
                results, times, memories = run_algorithm_test(
                    algo_name,
                    algorithms[algo_name],
                    test_numbers['composites'],
                    "合数"
                )
                all_results[f"{algo_name}_composites"] = results
                comparison_data.append({
                    '算法': algo_name,
                    '类型': '合数',
                    '平均时间(秒)': np.mean(times) if times else 0,
                    '最大时间(秒)': np.max(times) if times else 0,
                    '平均内存(MB)': np.mean(memories) if memories else 0,
                    '准确率(%)': 100
                })

            with tab3:
                st.write("测试特殊数")
                results, times, memories = run_algorithm_test(
                    algo_name,
                    algorithms[algo_name],
                    test_numbers['special'],
                    "特殊数"
                )
                all_results[f"{algo_name}_special"] = results

                # 计算总体准确率（用于图表）
                correct = sum(1 for r in results if
                              (r['test_type'] == "梅森数" and r['is_prime'] == is_mersenne_prime(r['number'])) or
                              (r['test_type'] != "梅森数" and r['is_prime'] == False))
                accuracy = (correct / len(results)) * 100 if results else 0
                comparison_data.append({
                    '算法': algo_name,
                    '类型': '特殊数',
                    '平均时间(秒)': np.mean(times) if times else 0,
                    '最大时间(秒)': np.max(times) if times else 0,
                    '平均内存(MB)': np.mean(memories) if memories else 0,
                    '准确率(%)': accuracy
                })

                # 统计各类特殊数的详细数据
                carmichael_correct = 0
                carmichael_total = 0
                pseudoprime_correct = 0
                pseudoprime_total = 0
                mersenne_correct = 0
                mersenne_total = 0
                carmichael_times = []
                pseudoprime_times = []
                mersenne_times = []

                for r in results:
                    if r['test_type'] == "卡迈克尔数":
                        carmichael_total += 1
                        carmichael_times.append(r['time'])
                        if not r['is_prime']:
                            carmichael_correct += 1
                    elif r['test_type'] == "强伪素数":
                        pseudoprime_total += 1
                        pseudoprime_times.append(r['time'])
                        if not r['is_prime']:
                            pseudoprime_correct += 1
                    elif r['test_type'] == "梅森数":
                        mersenne_total += 1
                        mersenne_times.append(r['time'])
                        if r['is_prime'] == is_mersenne_prime(r['number']):
                            mersenne_correct += 1

                # 保存到 special_details 字典
                special_details[algo_name] = {
                    '卡迈克尔数': {
                        '正确数': carmichael_correct,
                        '总数': carmichael_total,
                        '准确率(%)': (carmichael_correct / carmichael_total * 100) if carmichael_total > 0 else 0,
                        '平均时间(秒)': np.mean(carmichael_times) if carmichael_times else 0
                    },
                    '强伪素数': {
                        '正确数': pseudoprime_correct,
                        '总数': pseudoprime_total,
                        '准确率(%)': (pseudoprime_correct / pseudoprime_total * 100) if pseudoprime_total > 0 else 0,
                        '平均时间(秒)': np.mean(pseudoprime_times) if pseudoprime_times else 0
                    },
                    '梅森数': {
                        '正确数': mersenne_correct,
                        '总数': mersenne_total,
                        '准确率(%)': (mersenne_correct / mersenne_total * 100) if mersenne_total > 0 else 0,
                        '平均时间(秒)': np.mean(mersenne_times) if mersenne_times else 0
                    }
                }

            with tab4:
                st.write("特殊数详细统计")
                if algo_name in special_details:
                    details = special_details[algo_name]
                    detail_data = []
                    for special_type, stats in details.items():
                        detail_data.append({
                            '特殊数类型': special_type,
                            '测试总数': stats['总数'],
                            '正确判断数': stats['正确数'],
                            '准确率(%)': f"{stats['准确率(%)']:.2f}",
                            '平均时间(秒)': f"{stats['平均时间(秒)']:.6f}"
                        })
                    if detail_data:
                        st.dataframe(pd.DataFrame(detail_data), hide_index=True, use_container_width=True)
                    else:
                        st.info("暂无详细数据")
                else:
                    st.info("暂无详细数据")

        # 显示对比结果
        display_comparison_results(comparison_data)

        # 显示所有算法的特殊数详细对比表格
        st.header("📊 特殊数详细对比")
        if special_details:
            summary_data = []
            for algo_name, details in special_details.items():
                for special_type, stats in details.items():
                    if stats['总数'] > 0:
                        summary_data.append({
                            '算法': algo_name,
                            '特殊数类型': special_type,
                            '正确数/总数': f"{stats['正确数']}/{stats['总数']}",
                            '准确率(%)': f"{stats['准确率(%)']:.2f}",
                            '平均时间(秒)': f"{stats['平均时间(秒)']:.6f}"
                        })
            if summary_data:
                st.dataframe(pd.DataFrame(summary_data), hide_index=True, use_container_width=True)
            else:
                st.info("没有特殊数测试数据")
        else:
            st.info("请先运行算法测试")


def display_comparison_results(comparison_data):
    """显示对比结果"""
    st.header("📈 性能对比图表")

    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    df = pd.DataFrame(comparison_data)

    # 创建三个列
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("平均执行时间对比")
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        pivot_time = df.pivot(index='算法', columns='类型', values='平均时间(秒)')
        pivot_time.plot(kind='bar', ax=ax1)
        ax1.set_ylabel('时间 (秒)')
        ax1.set_title('算法平均执行时间对比')
        ax1.legend(title='测试类型')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig1)

    with col2:
        st.subheader("内存占用对比")
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        pivot_memory = df.pivot(index='算法', columns='类型', values='平均内存(MB)')
        pivot_memory.plot(kind='bar', ax=ax2)
        ax2.set_ylabel('内存 (MB)')
        ax2.set_title('算法内存占用对比')
        ax2.legend(title='测试类型')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig2)

    with col3:
        st.subheader("准确率对比")
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        pivot_accuracy = df.pivot(index='算法', columns='类型', values='准确率(%)')
        pivot_accuracy.plot(kind='bar', ax=ax3)
        ax3.set_ylabel('准确率 (%)')
        ax3.set_title('算法准确率对比')
        ax3.legend(title='测试类型')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig3)

    # 显示详细数据表格
    st.subheader("详细测试数据")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # 导出结果
    csv = df.to_csv(index=False)
    st.download_button(
        label="下载测试结果 (CSV)",
        data=csv,
        file_name=f"primality_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def is_mersenne_prime(n):
    """判断是否为梅森素数"""
    if n <= 1:
        return False
    # 检查 n+1 是否为2的幂
    m = n + 1
    return (m & (m - 1) == 0) and (n != 0)


def single_number_test():
    """单个数测试"""
    st.header("🔢 单个数字测试")

    col1, col2 = st.columns([2, 1])

    with col1:
        test_number = st.text_input(
            "输入要测试的数字",
            placeholder="例如: 123456789"
        )

    with col2:
        algorithms_selected = st.multiselect(
            "选择要使用的算法",
            ["试除法", "费马测试", "米勒-拉宾", "Baillie-PSW",
             "卢卡斯-莱默", "AKS", "APR-CL", "Bernstein"],
            default=["米勒-拉宾", "Baillie-PSW"]
        )

    if st.button("开始测试") and test_number:
        try:
            num = int(test_number)

            st.write(f"### 测试数字: {num}")

            algorithms_map = {
                "试除法": trial_division_test,
                "费马测试": fermat_test,
                "米勒-拉宾": miller_rabin_test,
                "Baillie-PSW": baillie_psw_test,
                "卢卡斯-莱默": lucas_lehmer_test,
                "AKS": aks_test,
                "APR-CL": apr_cl_test,
                "Bernstein": bernstein_test
            }

            results_data = []

            for algo_name in algorithms_selected:
                with st.spinner(f"运行 {algo_name}..."): # type: ignore
                    start_time = time.time()
                    result = algorithms_map[algo_name](num)
                    elapsed = time.time() - start_time

                    results_data.append({
                        "算法": algo_name,
                        "结果": "素数" if result else "合数",
                        "执行时间(秒)": f"{elapsed:.6f}"
                    })

            df = pd.DataFrame(results_data)
            st.dataframe(df,
                         hide_index=True,
                         use_container_width=True,
                         column_config={
                             "算法": st.column_config.TextColumn(width="small"),
                             "结果": st.column_config.TextColumn(width="small"),
                             "执行时间(秒)": st.column_config.TextColumn(width="medium")
                         })

        except ValueError:
            st.error("请输入有效的整数")


def main():
    """主函数"""
    st.title("🔢 素性测试算法对比评测系统")
    st.markdown("---")

    # 侧边栏
    st.sidebar.title("⚙️ 配置面板")

    # 生成测试数据
    generate_test_numbers()

    # 主界面选项卡
    tab1, tab2 = st.tabs(["📊 算法对比测试", "🔬 单个数测试"])

    with tab1:
        compare_algorithms()

    with tab2:
        single_number_test()


if __name__ == "__main__":
    main()