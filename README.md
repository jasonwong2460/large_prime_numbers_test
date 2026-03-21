Large Prime Numbers Test
Overview
A comprehensive implementation and benchmarking suite for 8 primality testing algorithms, with systematic evaluation across different datasets and performance metrics.

Algorithms Implemented
Category	Algorithm	Description
Basic	Trial Division	Optimized with 6k±1 pattern
Basic	Fermat Test	Probabilistic test based on Fermat's little theorem
Probabilistic	Miller-Rabin	Configurable error probability (4⁻ᵏ)
Probabilistic	Baillie-PSW	Combined Fermat and Lucas test
Specialized	Lucas-Lehmer	Deterministic test for Mersenne numbers
Deterministic	AKS	Polynomial-time deterministic algorithm
Advanced	APR-CL	Fast deterministic test using cyclotomy
Advanced	Bernstein	Optimized implementation

Features

✅ 8 Algorithms: Complete implementations of major primality tests

📊 Comprehensive Benchmarking: Performance comparison across algorithms

🔢 Multiple Dataset Types: Random primes/composites, Carmichael numbers, strong pseudoprimes, Mersenne numbers

⚡ Performance Metrics: Time complexity and memory usage analysis

📈 Visualization: Tables and curves for result analysis

Test Datasets
Dataset	Size	Description
Random Primes	256/512/1024 bits × 100	Random prime numbers
Random Composites	256/512/1024 bits × 100	Random composite numbers
Carmichael Numbers	20	Numbers that pass Fermat test but are composite
Strong Pseudoprimes	20	Numbers that fool Miller-Rabin
Mersenne Numbers	20	Numbers of form 2ⁿ - 1

Evaluation Metrics
Correctness: Accuracy in prime/composite identification

Time Performance: Execution time across different bit lengths

Memory Usage: Runtime memory consumption
