from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Arrays, Bits & Recursion"


@topic(G, "bit_magic", "Bit Magic", "binary")
def _():
    yield lead("Bit manipulation treats an integer as a row of 0/1 switches. A handful of operators (`& | ^ ~ << >>`) and a dozen tricks turn O(n) counting problems into O(1) formulas, cancel paired elements with XOR, and enumerate every subset of a set with a counter.")
    yield define("Bit magic", "solving problems by operating directly on the binary representation of integers — testing, setting, clearing and counting bits, and using XOR's cancelling property — instead of on their decimal value.")

    yield section("Binary representation and two's complement", "binary")
    yield p("An `n`-bit integer has `n` positions; bit 0 is the **least significant bit** (LSB, rightmost, worth `1`) and bit `n-1` the **most significant bit** (MSB, leftmost). Unsigned numbers use all bits for magnitude; signed numbers use **two's complement**, where the MSB acts as the sign and the representable range is `-2^(n-1)` … `2^(n-1) - 1`.")
    yield steps(
        ("Write the positive number", "`3` in 4 bits is `0011`."),
        ("Invert every bit", "`0011` → `1100` (this is the one's complement)."),
        ("Add 1", "`1100 + 1` → `1101`. That is `-3` in 4-bit two's complement."),
    )
    yield formula("two's complement of x in n bits = 2^n − x        (4 bits: 16 − 3 = 13 = 1101)")
    yield diagram('''
        4-bit two's complement (range -8 … 7)

         bits   value         bits   value
         0000     0           1000    -8   ← MSB set ⇒ negative
         0001     1           1001    -7
         0010     2           1010    -6
         0011     3           1011    -5
         0100     4           1100    -4
         0101     5           1101    -3
         0110     6           1110    -2
         0111     7           1111    -1
    ''', "Every 4-bit pattern is used exactly once; there is only one zero")
    yield p("Why two's complement rather than a separate sign bit? Three reasons that make hardware simpler:")
    yield ul(
        "**One zero.** A sign-magnitude scheme has `+0` and `-0`; two's complement has a single `0000`.",
        "**Addition just works.** The same adder handles positive and negative operands: `3 + (-3)` = `0011 + 1101` = `1 0000`, and dropping the carry gives `0000`. Subtraction is addition of the complement, which is where the name `0 − x` comes from.",
        "**The leading bit is the sign.** MSB `1` ⇒ negative, so a sign test is a single bit check.",
    )
    yield multi('''
        3 in 4 bits: 0011
        7 in 4 bits: 0111
        -1 in 4 bits: 1111
        -3 in 4 bits: 1101
        -8 in 4 bits: 1000
        2^4 - 3 = 13 -> 1101
    ''', py=r'''
        def bits(x, n):
            # the low n bits of x, most significant first ((x >> i) & 1 picks bit i)
            return "".join("1" if (x >> i) & 1 else "0" for i in range(n - 1, -1, -1))

        for x in (3, 7, -1, -3, -8):
            print(x, "in 4 bits:", bits(x, 4))
        print("2^4 - 3 =", (1 << 4) - 3, "->", bits((1 << 4) - 3, 4))
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        using namespace std;

        string bits(int x, int n) {
            string s;
            for (int i = n - 1; i >= 0; i--)        // (x >> i) & 1 picks bit i
                s += ((x >> i) & 1) ? '1' : '0';
            return s;
        }

        int main() {
            for (int x : {3, 7, -1, -3, -8})
                cout << x << " in 4 bits: " << bits(x, 4) << "\n";
            cout << "2^4 - 3 = " << ((1 << 4) - 3) << " -> " << bits((1 << 4) - 3, 4) << "\n";
        }
    ''', java=r'''
        public class Main {
            static String bits(int x, int n) {
                StringBuilder sb = new StringBuilder();
                for (int i = n - 1; i >= 0; i--)    // (x >> i) & 1 picks bit i
                    sb.append((x >> i) & 1);
                return sb.toString();
            }

            public static void main(String[] args) {
                for (int x : new int[]{3, 7, -1, -3, -8})
                    System.out.println(x + " in 4 bits: " + bits(x, 4));
                System.out.println("2^4 - 3 = " + ((1 << 4) - 3) + " -> " + bits((1 << 4) - 3, 4));
            }
        }
    ''', js=r'''
        function bits(x, n) {
            let s = "";
            for (let i = n - 1; i >= 0; i--)        // (x >> i) & 1 picks bit i
                s += (x >> i) & 1;
            return s;
        }

        for (const x of [3, 7, -1, -3, -8])
            console.log(x, "in 4 bits:", bits(x, 4));
        console.log("2^4 - 3 =", (1 << 4) - 3, "->", bits((1 << 4) - 3, 4));
    ''')
    yield note("Masking with `(x >> i) & 1` works for negative numbers too, because every language above shifts a negative `int` arithmetically (the sign bit is copied in). Python has no fixed width, so `-3` is conceptually `…11111101` with infinitely many leading ones — taking the low 4 bits still gives `1101`.")

    yield section("Bitwise operators", "math-function")
    yield table(
        ["Operator", "Name", "Rule per bit", "`12 (1100)` with `10 (1010)`"],
        ["`a & b`", "AND", "1 only if **both** bits are 1", "`1000` = 8"],
        ["`a | b`", "OR", "1 if **either** bit is 1", "`1110` = 14"],
        ["`a ^ b`", "XOR", "1 if the bits **differ**", "`0110` = 6"],
        ["`~a`", "NOT", "flips every bit; equals `-a - 1` in two's complement", "`~12` = -13"],
        ["`a << k`", "left shift", "shift left, zeros enter on the right; multiplies by `2^k`", "`12 << 2` = 48"],
        ["`a >> k`", "right shift", "shift right, drops the low bits; divides by `2^k` (floor)", "`12 >> 2` = 3"],
    )
    yield multi('''
        a = 12 -> 00001100
        b = 10 -> 00001010
        a & b = 8 -> 00001000
        a | b = 14 -> 00001110
        a ^ b = 6 -> 00000110
        ~a = -13 -> 11110011
        a << 2 = 48 -> 00110000
        a >> 2 = 3 -> 00000011
    ''', py=r'''
        def bits(x, n):
            return "".join("1" if (x >> i) & 1 else "0" for i in range(n - 1, -1, -1))

        def show(label, v):
            print(f"{label} = {v} -> {bits(v, 8)}")

        a, b = 12, 10
        show("a", a)
        show("b", b)
        show("a & b", a & b)
        show("a | b", a | b)
        show("a ^ b", a ^ b)
        show("~a", ~a)            # -13: Python prints the signed value, low 8 bits are 11110011
        show("a << 2", a << 2)
        show("a >> 2", a >> 2)
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        using namespace std;

        string bits(int x, int n) {
            string s;
            for (int i = n - 1; i >= 0; i--) s += ((x >> i) & 1) ? '1' : '0';
            return s;
        }

        void show(const string& label, int v) {
            cout << label << " = " << v << " -> " << bits(v, 8) << "\n";
        }

        int main() {
            int a = 12, b = 10;
            show("a", a);
            show("b", b);
            show("a & b", a & b);
            show("a | b", a | b);
            show("a ^ b", a ^ b);
            show("~a", ~a);           // -13 in a 32-bit int: low 8 bits are 11110011
            show("a << 2", a << 2);
            show("a >> 2", a >> 2);
        }
    ''', java=r'''
        public class Main {
            static String bits(int x, int n) {
                StringBuilder sb = new StringBuilder();
                for (int i = n - 1; i >= 0; i--) sb.append((x >> i) & 1);
                return sb.toString();
            }

            static void show(String label, int v) {
                System.out.println(label + " = " + v + " -> " + bits(v, 8));
            }

            public static void main(String[] args) {
                int a = 12, b = 10;
                show("a", a);
                show("b", b);
                show("a & b", a & b);
                show("a | b", a | b);
                show("a ^ b", a ^ b);
                show("~a", ~a);       // -13 in a 32-bit int: low 8 bits are 11110011
                show("a << 2", a << 2);
                show("a >> 2", a >> 2);
            }
        }
    ''', js=r'''
        function bits(x, n) {
            let s = "";
            for (let i = n - 1; i >= 0; i--) s += (x >> i) & 1;
            return s;
        }

        function show(label, v) {
            console.log(`${label} = ${v} -> ${bits(v, 8)}`);
        }

        const a = 12, b = 10;
        show("a", a);
        show("b", b);
        show("a & b", a & b);
        show("a | b", a | b);
        show("a ^ b", a ^ b);
        show("~a", ~a);               // JS converts to a 32-bit int first: -13
        show("a << 2", a << 2);
        show("a >> 2", a >> 2);
    ''')

    yield section("Language differences you must know", "alert-triangle")
    yield table(
        ["", "Python", "C++ / Java", "JavaScript"],
        ["Width of an `int`", "unbounded — `1 << 100` is fine, `~x` is always `-x-1`", "32-bit `int`, 64-bit `long`/`long long`; overflow wraps (Java) or is undefined for signed (C++)", "numbers are doubles, but **every bitwise operator converts to a 32-bit signed int first** — `1 << 31` is `-2147483648`"],
        ["`>>` on negatives", "arithmetic (floor division by `2^k`)", "arithmetic; C++ guarantees it since C++20", "arithmetic"],
        ["Logical (zero-fill) shift", "not needed — mask first: `(x & 0xFFFFFFFF) >> k`", "Java: `x >>> k`. C++: cast to `unsigned` first", "`x >>> k`"],
        ["Shift by ≥ width", "fine (just a bigger number)", "**undefined** in C++, taken mod 32/64 in Java", "taken mod 32"],
        ["Popcount built-in", "`n.bit_count()` (3.10+) or `bin(n).count('1')`", "`std::popcount` (`<bit>`, unsigned) / `__builtin_popcount`; `Integer.bitCount(n)`", "none — `n.toString(2).split('1').length - 1`"],
    )
    yield multi('''
        -16 >> 2 = -4
        -16 >>> 2 = 1073741820
        1 << 10 = 1024
    ''', py=r'''
        x = -16
        print("-16 >> 2 =", x >> 2)                       # arithmetic: sign bit copied in
        print("-16 >>> 2 =", (x & 0xFFFFFFFF) >> 2)       # emulate a 32-bit logical shift
        print("1 << 10 =", 1 << 10)
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        int main() {
            int x = -16;
            cout << "-16 >> 2 = " << (x >> 2) << "\n";                        // arithmetic shift
            cout << "-16 >>> 2 = " << (static_cast<unsigned>(x) >> 2) << "\n"; // logical: shift as unsigned
            cout << "1 << 10 = " << (1 << 10) << "\n";
        }
    ''', java=r'''
        public class Main {
            public static void main(String[] args) {
                int x = -16;
                System.out.println("-16 >> 2 = " + (x >> 2));     // arithmetic shift
                System.out.println("-16 >>> 2 = " + (x >>> 2));   // logical shift fills with zeros
                System.out.println("1 << 10 = " + (1 << 10));
            }
        }
    ''', js=r'''
        const x = -16;
        console.log("-16 >> 2 =", x >> 2);        // arithmetic shift
        console.log("-16 >>> 2 =", x >>> 2);      // logical shift; result is an unsigned 32-bit value
        console.log("1 << 10 =", 1 << 10);
    ''')
    yield pitfall("In JavaScript `2 ** 40 | 0` silently truncates to 32 bits, and in C++ `1 << 31` on an `int` and any shift by 32 or more are undefined behaviour. When you need 64 bits use `1n << 40n` (BigInt) in JS and `1LL << 40` / `1L << 40` in C++/Java.")

    yield section("The classic tricks", "bulb")
    yield table(
        ["Expression", "What it does", "Why"],
        ["`n & 1`", "`1` if `n` is odd", "the LSB is the only odd place value"],
        ["`n << 1`, `n >> 1`", "`n * 2`, `n / 2` (floor)", "shifting moves every bit to the next place value"],
        ["`1 << k`", "`2^k`, a mask with only bit `k` set", "`1` moved `k` places left"],
        ["`n & (1 << k)`", "non-zero iff bit `k` is set", "AND keeps only that bit"],
        ["`n | (1 << k)`", "set bit `k`", "OR with the mask forces a `1`"],
        ["`n & ~(1 << k)`", "clear bit `k`", "AND with every bit except `k` set"],
        ["`n ^ (1 << k)`", "toggle bit `k`", "XOR with `1` flips, with `0` keeps"],
        ["`n & (n - 1)`", "clear the **rightmost set bit**", "subtracting 1 flips that bit and the zeros after it"],
        ["`n & -n`  (= `n & ~(n - 1)`)", "isolate the rightmost set bit", "`-n` agrees with `n` only at that bit"],
        ["`n & (n - 1) == 0`", "`n` is a power of two (for `n > 0`)", "a power of two has exactly one set bit"],
        ["`x ^ x = 0`, `x ^ 0 = x`", "XOR cancels pairs", "the basis of the odd-occurrence problems below"],
        ["`a ^= b; b ^= a; a ^= b`", "swap without a temporary", "`a ^ b ^ b = a`"],
    )
    yield section("Decimal to binary and back", "arrows-shuffle")
    yield p("Repeated division by 2 produces the bits from the right: the remainder is the next bit, the quotient is what is left. Reading a binary string left to right is the reverse: `value = value * 2 + bit`. Both loops are `O(number of bits)` = `O(log n)`.")
    yield multi('''
        37 -> 100101
        100101 -> 37
    ''', py=r'''
        def to_binary(n):
            if n == 0:
                return "0"
            s = ""
            while n > 0:
                s = str(n % 2) + s      # remainder = next bit from the right
                n //= 2
            return s

        def to_decimal(b):
            v = 0
            for ch in b:
                v = v * 2 + (1 if ch == '1' else 0)   # shift what we have, add the new bit
            return v

        print(37, "->", to_binary(37))
        print("100101", "->", to_decimal("100101"))
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        using namespace std;

        string toBinary(int n) {
            if (n == 0) return "0";
            string s;
            while (n > 0) {
                s = char('0' + n % 2) + s;     // remainder = next bit from the right
                n /= 2;
            }
            return s;
        }

        int toDecimal(const string& b) {
            int v = 0;
            for (char ch : b) v = v * 2 + (ch == '1' ? 1 : 0);   // shift what we have, add the new bit
            return v;
        }

        int main() {
            cout << 37 << " -> " << toBinary(37) << "\n";
            cout << "100101" << " -> " << toDecimal("100101") << "\n";
        }
    ''', java=r'''
        public class Main {
            static String toBinary(int n) {
                if (n == 0) return "0";
                StringBuilder s = new StringBuilder();
                while (n > 0) {
                    s.insert(0, n % 2);        // remainder = next bit from the right
                    n /= 2;
                }
                return s.toString();
            }

            static int toDecimal(String b) {
                int v = 0;
                for (char ch : b.toCharArray()) v = v * 2 + (ch == '1' ? 1 : 0);   // shift, add the new bit
                return v;
            }

            public static void main(String[] args) {
                System.out.println(37 + " -> " + toBinary(37));
                System.out.println("100101" + " -> " + toDecimal("100101"));
            }
        }
    ''', js=r'''
        function toBinary(n) {
            if (n === 0) return "0";
            let s = "";
            while (n > 0) {
                s = (n % 2) + s;              // remainder = next bit from the right
                n = Math.floor(n / 2);
            }
            return s;
        }

        function toDecimal(b) {
            let v = 0;
            for (const ch of b) v = v * 2 + (ch === '1' ? 1 : 0);   // shift what we have, add the new bit
            return v;
        }

        console.log(37, "->", toBinary(37));
        console.log("100101", "->", toDecimal("100101"));
    ''')
    yield note("The built-ins do the same: Python `bin(37)` / `int('100101', 2)`, C++ `bitset<8>(37)` / `stoi(s, nullptr, 2)`, Java `Integer.toBinaryString(37)` / `Integer.parseInt(s, 2)`, JavaScript `(37).toString(2)` / `parseInt(s, 2)`.")

    yield section("Check whether the kth bit is set", "search")
    yield io("n = 5, k = 1", "Yes", "n = 5, k = 2", "No", "n = 5, k = 3", "Yes")
    yield p("Bits are counted from the right, so the **kth bit** (1-based) is the mask `1 << (k - 1)`; `k` must not exceed the width of `n`. Two equivalent ways:")
    yield idea("**Move the mask to the bit:** `n & (1 << (k-1))` keeps only bit `k`; the result is non-zero exactly when that bit is `1`. **Or move the bit to the mask:** `(n >> (k-1)) & 1` drags bit `k` down to position 0 and reads it as `0` or `1`.")
    yield diagram('''
        n = 5 = 0 1 0 1          k = 3 → mask 1 << 2 = 0 1 0 0
                k=4 3 2 1
        n & mask = 0 1 0 0  ≠ 0  → bit 3 is set
        n >> 2   = 0 0 0 1  & 1 = 1 → the same answer, read at position 0
    ''', "Both methods look at the same bit")
    yield multi('''
        n = 5 -> 0101
        k = 1: Yes Yes
        k = 2: No No
        k = 3: Yes Yes
        k = 4: No No
    ''', py=r'''
        def is_kth_set_mask(n, k):
            return (n & (1 << (k - 1))) != 0     # way 1: move the mask to the bit

        def is_kth_set_shift(n, k):
            return ((n >> (k - 1)) & 1) == 1     # way 2: move the bit to position 0

        n = 5
        print("n =", n, "->", format(n, "04b"))
        for k in range(1, 5):
            print(f"k = {k}:", "Yes" if is_kth_set_mask(n, k) else "No",
                  "Yes" if is_kth_set_shift(n, k) else "No")
    ''', cpp=r'''
        #include <iostream>
        #include <bitset>
        using namespace std;

        bool isKthSetMask(int n, int k) {
            return (n & (1 << (k - 1))) != 0;    // way 1: move the mask to the bit
        }

        bool isKthSetShift(int n, int k) {
            return ((n >> (k - 1)) & 1) == 1;    // way 2: move the bit to position 0
        }

        int main() {
            int n = 5;
            cout << "n = " << n << " -> " << bitset<4>(n) << "\n";
            for (int k = 1; k <= 4; k++)
                cout << "k = " << k << ": " << (isKthSetMask(n, k) ? "Yes" : "No")
                     << " " << (isKthSetShift(n, k) ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        public class Main {
            static boolean isKthSetMask(int n, int k) {
                return (n & (1 << (k - 1))) != 0;    // way 1: move the mask to the bit
            }

            static boolean isKthSetShift(int n, int k) {
                return ((n >> (k - 1)) & 1) == 1;    // way 2: move the bit to position 0
            }

            public static void main(String[] args) {
                int n = 5;
                String b = String.format("%4s", Integer.toBinaryString(n)).replace(' ', '0');
                System.out.println("n = " + n + " -> " + b);
                for (int k = 1; k <= 4; k++)
                    System.out.println("k = " + k + ": " + (isKthSetMask(n, k) ? "Yes" : "No")
                                       + " " + (isKthSetShift(n, k) ? "Yes" : "No"));
            }
        }
    ''', js=r'''
        function isKthSetMask(n, k) {
            return (n & (1 << (k - 1))) !== 0;   // way 1: move the mask to the bit
        }

        function isKthSetShift(n, k) {
            return ((n >> (k - 1)) & 1) === 1;   // way 2: move the bit to position 0
        }

        const n = 5;
        console.log("n =", n, "->", n.toString(2).padStart(4, "0"));
        for (let k = 1; k <= 4; k++)
            console.log(`k = ${k}:`, isKthSetMask(n, k) ? "Yes" : "No", isKthSetShift(n, k) ? "Yes" : "No");
    ''')
    yield complexity("O(1)", "O(1)")
    yield note("Way 2 is the one to use when you want the bit's **value** (`0`/`1`) rather than a yes/no — e.g. when reading a number bit by bit. Both are a single AND plus a shift.")
    yield pitfall("`if n & (1 << (k-1)) == 1` is wrong for `k > 1`: the AND leaves the bit **in place**, so the result is `4` for `k = 3`, not `1`. Compare with `!= 0` (or use the shift form). Also, in C++ `1 << 31` overflows a signed `int` — use `1u << k` or `1LL << k` for high bits.")

    yield section("Count set bits", "hash")
    yield io("n = 5", "2", "n = 13", "3", "n = 255", "8")
    yield p("The number of `1` bits is also called the **population count** or **Hamming weight**. There are four standard ways, from obvious to fastest.")
    yield p("**Naive:** walk the bits from LSB to MSB — `n % 2` (or `n & 1`) reads the lowest bit, `n // 2` (or `n >> 1`) drops it. Runs once per bit, set or not.")
    yield multi('''
        9 -> 2
        13 -> 3
        255 -> 8
        1023 -> 10
    ''', py=r'''
        def count_bits(n):
            res = 0
            while n:
                res += n & 1          # 1 if the lowest bit is set
                n >>= 1               # drop it
            return res

        for n in (9, 13, 255, 1023):
            print(n, "->", count_bits(n))
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        int countBits(int n) {
            int res = 0;
            while (n) {
                res += n & 1;         // 1 if the lowest bit is set
                n >>= 1;              // drop it
            }
            return res;
        }

        int main() {
            for (int n : {9, 13, 255, 1023}) cout << n << " -> " << countBits(n) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int countBits(int n) {
                int res = 0;
                while (n != 0) {
                    res += n & 1;     // 1 if the lowest bit is set
                    n >>>= 1;         // logical shift so a negative n also terminates
                }
                return res;
            }

            public static void main(String[] args) {
                for (int n : new int[]{9, 13, 255, 1023}) System.out.println(n + " -> " + countBits(n));
            }
        }
    ''', js=r'''
        function countBits(n) {
            let res = 0;
            while (n !== 0) {
                res += n & 1;         // 1 if the lowest bit is set
                n >>>= 1;             // logical shift so a negative n also terminates
            }
            return res;
        }

        for (const n of [9, 13, 255, 1023]) console.log(n, "->", countBits(n));
    ''')
    yield complexity("O(number of bits) = O(log n)", "O(1)")
    yield pitfall("With an **arithmetic** shift (`>>`) a negative `n` never reaches zero — `-1 >> 1` is still `-1` — so the loop runs forever. Use the logical shift (`>>>` in Java/JS, cast to `unsigned` in C++) or loop a fixed 32 times. Python's `n >>= 1` on a negative number has the same problem.")
    yield p("**Brian Kernighan's algorithm:** `n & (n - 1)` clears the rightmost set bit, so the loop runs once **per set bit** instead of once per bit position. For a sparse number it is much faster.")
    yield diagram('''
        n = 13:   1101
        1101 & 1100 = 1100   (12)   rightmost 1 cleared → count 1
        1100 & 1011 = 1000   ( 8)                       → count 2
        1000 & 0111 = 0000   ( 0)                       → count 3, stop
    ''', "Subtracting 1 flips the rightmost 1 and every 0 after it; AND-ing keeps everything to its left")
    yield multi('''
        9 -> 2
        13 -> 3
        255 -> 8
        1023 -> 10
    ''', py=r'''
        def count_bits(n):
            res = 0
            while n:
                n &= n - 1            # clears the rightmost set bit
                res += 1
            return res

        for n in (9, 13, 255, 1023):
            print(n, "->", count_bits(n))
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        int countBits(int n) {
            int res = 0;
            while (n) {
                n &= n - 1;           // clears the rightmost set bit
                res++;
            }
            return res;
        }

        int main() {
            for (int n : {9, 13, 255, 1023}) cout << n << " -> " << countBits(n) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int countBits(int n) {
                int res = 0;
                while (n != 0) {
                    n &= n - 1;       // clears the rightmost set bit
                    res++;
                }
                return res;
            }

            public static void main(String[] args) {
                for (int n : new int[]{9, 13, 255, 1023}) System.out.println(n + " -> " + countBits(n));
            }
        }
    ''', js=r'''
        function countBits(n) {
            let res = 0;
            while (n !== 0) {
                n &= n - 1;           // clears the rightmost set bit
                res++;
            }
            return res;
        }

        for (const n of [9, 13, 255, 1023]) console.log(n, "->", countBits(n));
    ''')
    yield complexity("O(number of set bits)", "O(1)")
    yield p("**Lookup table:** precompute the count for every byte value `0…255` once (`O(1)`, it is a constant 256 entries), then a 32-bit number is just **four table reads**. Each entry is built from a smaller one: `tbl[i] = (i & 1) + tbl[i >> 1]`.")
    yield multi('''
        9 -> 2
        13 -> 3
        255 -> 8
        1023 -> 10
    ''', py=r'''
        tbl = [0] * 256
        for i in range(1, 256):
            tbl[i] = (i & 1) + tbl[i >> 1]      # lowest bit + count of the rest

        def count_bits(n):                      # 32-bit n: four bytes
            return (tbl[n & 0xff] + tbl[(n >> 8) & 0xff]
                    + tbl[(n >> 16) & 0xff] + tbl[(n >> 24) & 0xff])

        for n in (9, 13, 255, 1023):
            print(n, "->", count_bits(n))
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        int tbl[256];

        void initialize() {
            for (int i = 1; i < 256; i++) tbl[i] = (i & 1) + tbl[i >> 1];   // lowest bit + count of the rest
        }

        int countBits(unsigned n) {             // unsigned: >> never drags a sign bit in
            return tbl[n & 0xff] + tbl[(n >> 8) & 0xff] + tbl[(n >> 16) & 0xff] + tbl[(n >> 24) & 0xff];
        }

        int main() {
            initialize();
            for (int n : {9, 13, 255, 1023}) cout << n << " -> " << countBits(n) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int[] tbl = new int[256];

            static void initialize() {
                for (int i = 1; i < 256; i++) tbl[i] = (i & 1) + tbl[i >> 1];   // lowest bit + count of the rest
            }

            static int countBits(int n) {       // >>> so a negative n gives the right 32-bit answer
                return tbl[n & 0xff] + tbl[(n >>> 8) & 0xff] + tbl[(n >>> 16) & 0xff] + tbl[(n >>> 24) & 0xff];
            }

            public static void main(String[] args) {
                initialize();
                for (int n : new int[]{9, 13, 255, 1023}) System.out.println(n + " -> " + countBits(n));
            }
        }
    ''', js=r'''
        const tbl = new Array(256).fill(0);
        for (let i = 1; i < 256; i++) tbl[i] = (i & 1) + tbl[i >> 1];   // lowest bit + count of the rest

        function countBits(n) {                 // >>> so a negative n gives the right 32-bit answer
            return tbl[n & 0xff] + tbl[(n >>> 8) & 0xff] + tbl[(n >>> 16) & 0xff] + tbl[(n >>> 24) & 0xff];
        }

        for (const n of [9, 13, 255, 1023]) console.log(n, "->", countBits(n));
    ''')
    yield complexity("O(1) — four lookups", "O(1) — a fixed 256-entry table")
    yield p("**Built-ins:** in production code use the library — it compiles to a single `popcnt` instruction where the CPU has one.")
    yield multi('''
        9 -> 2
        13 -> 3
        255 -> 8
        1023 -> 10
    ''', py=r'''
        for n in (9, 13, 255, 1023):
            print(n, "->", n.bit_count())        # Python 3.10+; older: bin(n).count("1")
    ''', cpp=r'''
        #include <iostream>
        #include <bit>
        using namespace std;

        int main() {
            for (int n : {9, 13, 255, 1023})
                cout << n << " -> " << popcount(static_cast<unsigned>(n)) << "\n";   // C++20; or __builtin_popcount(n)
        }
    ''', java=r'''
        public class Main {
            public static void main(String[] args) {
                for (int n : new int[]{9, 13, 255, 1023})
                    System.out.println(n + " -> " + Integer.bitCount(n));          // Long.bitCount for long
            }
        }
    ''', js=r'''
        for (const n of [9, 13, 255, 1023])
            console.log(n, "->", n.toString(2).split("1").length - 1);   // no popcount in JS: count '1's in the binary string
    ''')

    yield section("Is n a power of 2?", "bolt")
    yield io("n = 4", "Yes", "n = 6", "No", "n = 0", "No")
    yield p("**Naive:** keep halving while `n` is even; it is a power of two if you end at exactly `1`. `O(log n)`.")
    yield snippet("py", r'''
        def is_power_of_two(n):
            if n == 0:
                return False
            while n != 1:
                if n % 2 != 0:          # an odd number above 1 cannot be a power of two
                    return False
                n //= 2
            return True

        for n in (4, 0, 1, 6, 1024):
            print(n, "->", "Yes" if is_power_of_two(n) else "No")
    ''', out='''
        4 -> Yes
        0 -> No
        1 -> Yes
        6 -> No
        1024 -> Yes
    ''')
    yield idea("A power of two has **exactly one** set bit (`1, 10, 100, 1000…`). `n & (n - 1)` clears the rightmost set bit, so for a power of two it leaves `0`; any other positive number still has a bit left. `n = 0` has no set bit at all and must be rejected separately — `0 & (0 - 1)` is also `0`.")
    yield multi('''
        4 -> Yes
        0 -> No
        1 -> Yes
        6 -> No
        1024 -> Yes
    ''', py=r'''
        def is_power_of_two(n):
            return n != 0 and (n & (n - 1)) == 0     # exactly one set bit

        for n in (4, 0, 1, 6, 1024):
            print(n, "->", "Yes" if is_power_of_two(n) else "No")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        bool isPowerOfTwo(int n) {
            return n != 0 && (n & (n - 1)) == 0;      // exactly one set bit
        }

        int main() {
            for (int n : {4, 0, 1, 6, 1024})
                cout << n << " -> " << (isPowerOfTwo(n) ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        public class Main {
            static boolean isPowerOfTwo(int n) {
                return n != 0 && (n & (n - 1)) == 0;  // exactly one set bit
            }

            public static void main(String[] args) {
                for (int n : new int[]{4, 0, 1, 6, 1024})
                    System.out.println(n + " -> " + (isPowerOfTwo(n) ? "Yes" : "No"));
            }
        }
    ''', js=r'''
        function isPowerOfTwo(n) {
            return n !== 0 && (n & (n - 1)) === 0;    // exactly one set bit
        }

        for (const n of [4, 0, 1, 6, 1024])
            console.log(n, "->", isPowerOfTwo(n) ? "Yes" : "No");
    ''')
    yield complexity("O(1)", "O(1)")
    yield pitfall("Two edge cases: `n = 0` passes the `n & (n-1) == 0` test but is not a power of two, and a **negative** `n` such as `-2147483648` (`INT_MIN`, a single set bit in 32 bits) also passes. Write `n > 0 && (n & (n - 1)) == 0` when negatives are possible.")

    yield section("Find the one odd-occurring element", "puzzle")
    yield io("arr = [10, 30, 30, 10, 30, 30, 20]", "20", "arr = [4, 3, 4, 4, 4, 5, 5]", "3")
    yield p("Every element appears an even number of times except one. **Naive:** for each element count its occurrences with a second loop and return the first with an odd count — `O(n²)`.")
    yield snippet("py", r'''
        def find_odd(arr):
            for x in arr:
                count = 0
                for y in arr:               # O(n) count for each of the n elements
                    if x == y:
                        count += 1
                if count % 2 == 1:
                    return x
            return -1

        print(find_odd([10, 30, 30, 10, 30, 30, 20]))
        print(find_odd([4, 3, 4, 4, 4, 5, 5]))
    ''', out='''
        20
        3
    ''')
    yield idea("XOR is commutative and associative, `x ^ x = 0` and `x ^ 0 = x`. XOR-ing the whole array therefore lets every pair cancel itself regardless of order, and the only thing left standing is the element that had no partner.")
    yield diagram('''
        10 ^ 30 ^ 30 ^ 10 ^ 30 ^ 30 ^ 20
      = (10 ^ 10) ^ (30 ^ 30) ^ (30 ^ 30) ^ 20      reorder: XOR is commutative
      =    0      ^    0      ^    0      ^ 20
      = 20
    ''', "Pairs cancel to 0; 0 is the XOR identity")
    yield multi('''
        10 30 30 10 30 30 20 -> 20
        4 3 4 4 4 5 5 -> 3
    ''', py=r'''
        def find_odd(arr):
            res = 0
            for x in arr:
                res ^= x              # pairs cancel: x ^ x = 0
            return res

        for arr in ([10, 30, 30, 10, 30, 30, 20], [4, 3, 4, 4, 4, 5, 5]):
            print(" ".join(map(str, arr)), "->", find_odd(arr))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        int findOdd(const vector<int>& arr) {
            int res = 0;
            for (int x : arr) res ^= x;      // pairs cancel: x ^ x = 0
            return res;
        }

        int main() {
            vector<vector<int>> tests = {{10, 30, 30, 10, 30, 30, 20}, {4, 3, 4, 4, 4, 5, 5}};
            for (const auto& arr : tests) {
                for (int x : arr) cout << x << " ";
                cout << "-> " << findOdd(arr) << "\n";
            }
        }
    ''', java=r'''
        public class Main {
            static int findOdd(int[] arr) {
                int res = 0;
                for (int x : arr) res ^= x;  // pairs cancel: x ^ x = 0
                return res;
            }

            public static void main(String[] args) {
                int[][] tests = {{10, 30, 30, 10, 30, 30, 20}, {4, 3, 4, 4, 4, 5, 5}};
                for (int[] arr : tests) {
                    StringBuilder sb = new StringBuilder();
                    for (int x : arr) sb.append(x).append(' ');
                    System.out.println(sb + "-> " + findOdd(arr));
                }
            }
        }
    ''', js=r'''
        function findOdd(arr) {
            let res = 0;
            for (const x of arr) res ^= x;   // pairs cancel: x ^ x = 0
            return res;
        }

        for (const arr of [[10, 30, 30, 10, 30, 30, 20], [4, 3, 4, 4, 4, 5, 5]])
            console.log(arr.join(" "), "->", findOdd(arr));
    ''')
    yield complexity("O(n)", "O(1)")
    yield note("The same trick solves **missing number** (XOR `1…n` with the array — the missing value survives) and **find the element that appears once while the rest appear twice**. It fails when more than one element is odd-occurring — the result is the XOR of all of them — which is exactly the next problem.")

    yield section("Find the two odd-occurring elements", "puzzle")
    yield io("arr = [3, 4, 3, 4, 5, 4, 4, 6, 7, 7]", "5 6", "arr = [20, 15, 20, 16]", "15 16")
    yield p("Now exactly two elements, `x` and `y`, occur an odd number of times. XOR-ing everything gives `x ^ y`, which is not enough on its own — we need to separate them.")
    yield idea("`x ^ y` has a `1` exactly where `x` and `y` **differ**. Take its rightmost set bit, `sn = xors & -xors`. Partition the array into elements that have that bit set and elements that do not: `x` lands in one group and `y` in the other, and every paired element lands in the same group as its partner. XOR each group separately and the pairs cancel again, leaving `x` in one group and `y` in the other.")
    yield diagram('''
        arr = 3 4 3 4 5 4 4 6 7 7
        XOR of all      = 5 ^ 6 = 101 ^ 110 = 011          (every pair cancels)
        rightmost 1 bit = 011 & -011 = 001                 (5 and 6 differ in bit 0)

        bit 0 set   : 3 3 5 7 7   → XOR = 5
        bit 0 clear : 4 4 4 4 6   → XOR = 6
    ''', "The rightmost differing bit splits the two odd elements into different groups")
    yield multi('''
        3 4 3 4 5 4 4 6 7 7 -> 5 6
        20 15 20 16 -> 15 16
    ''', py=r'''
        def two_odd(arr):
            xors = 0
            for x in arr:
                xors ^= x                 # = x ^ y
            sn = xors & -xors             # rightmost set bit (same as xors & ~(xors - 1))
            res1 = res2 = 0
            for x in arr:
                if x & sn:
                    res1 ^= x             # group with the bit set
                else:
                    res2 ^= x             # group with the bit clear
            return min(res1, res2), max(res1, res2)

        for arr in ([3, 4, 3, 4, 5, 4, 4, 6, 7, 7], [20, 15, 20, 16]):
            a, b = two_odd(arr)
            print(" ".join(map(str, arr)), "->", a, b)
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        #include <algorithm>
        using namespace std;

        pair<int, int> twoOdd(const vector<int>& arr) {
            int xors = 0;
            for (int x : arr) xors ^= x;        // = x ^ y
            int sn = xors & -xors;              // rightmost set bit (same as xors & ~(xors - 1))
            int res1 = 0, res2 = 0;
            for (int x : arr) {
                if (x & sn) res1 ^= x;          // group with the bit set
                else        res2 ^= x;          // group with the bit clear
            }
            return {min(res1, res2), max(res1, res2)};
        }

        int main() {
            vector<vector<int>> tests = {{3, 4, 3, 4, 5, 4, 4, 6, 7, 7}, {20, 15, 20, 16}};
            for (const auto& arr : tests) {
                for (int x : arr) cout << x << " ";
                auto [a, b] = twoOdd(arr);
                cout << "-> " << a << " " << b << "\n";
            }
        }
    ''', java=r'''
        public class Main {
            static int[] twoOdd(int[] arr) {
                int xors = 0;
                for (int x : arr) xors ^= x;    // = x ^ y
                int sn = xors & -xors;          // rightmost set bit (same as xors & ~(xors - 1))
                int res1 = 0, res2 = 0;
                for (int x : arr) {
                    if ((x & sn) != 0) res1 ^= x;   // group with the bit set
                    else               res2 ^= x;   // group with the bit clear
                }
                return new int[]{Math.min(res1, res2), Math.max(res1, res2)};
            }

            public static void main(String[] args) {
                int[][] tests = {{3, 4, 3, 4, 5, 4, 4, 6, 7, 7}, {20, 15, 20, 16}};
                for (int[] arr : tests) {
                    StringBuilder sb = new StringBuilder();
                    for (int x : arr) sb.append(x).append(' ');
                    int[] r = twoOdd(arr);
                    System.out.println(sb + "-> " + r[0] + " " + r[1]);
                }
            }
        }
    ''', js=r'''
        function twoOdd(arr) {
            let xors = 0;
            for (const x of arr) xors ^= x;     // = x ^ y
            const sn = xors & -xors;            // rightmost set bit (same as xors & ~(xors - 1))
            let res1 = 0, res2 = 0;
            for (const x of arr) {
                if (x & sn) res1 ^= x;          // group with the bit set
                else        res2 ^= x;          // group with the bit clear
            }
            return [Math.min(res1, res2), Math.max(res1, res2)];
        }

        for (const arr of [[3, 4, 3, 4, 5, 4, 4, 6, 7, 7], [20, 15, 20, 16]]) {
            const [a, b] = twoOdd(arr);
            console.log(arr.join(" "), "->", a, b);
        }
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("The two results come out in **group order**, not sorted — which group holds the smaller value depends on the bit chosen. Sort the pair (as above) or the output will look random. `xors & -xors` relies on two's complement: `-xors` is `~xors + 1`, which agrees with `xors` only at the rightmost set bit.")

    yield section("Power set using bitmasks", "apps")
    yield io("s = \"abc\"", "{} {a} {b} {a,b} {c} {a,c} {b,c} {a,b,c}")
    yield idea("A set of `n` elements has `2^n` subsets, and there are exactly `2^n` integers from `0` to `2^n - 1`. Read each counter as a mask: bit `j` set means **include `s[j]`**. Looping the counter enumerates every subset exactly once, with no recursion.")
    yield diagram('''
        s = "abc", n = 3, masks 0 … 7       (bit 0 ↔ a, bit 1 ↔ b, bit 2 ↔ c)

        i    c b a    subset
        0    0 0 0    {}
        1    0 0 1    {a}
        2    0 1 0    {b}
        3    0 1 1    {a,b}
        4    1 0 0    {c}
        5    1 0 1    {a,c}
        6    1 1 0    {b,c}
        7    1 1 1    {a,b,c}
    ''', "The counter's bits choose the elements")
    yield multi('''
        000 -> {}
        001 -> {a}
        010 -> {b}
        011 -> {a,b}
        100 -> {c}
        101 -> {a,c}
        110 -> {b,c}
        111 -> {a,b,c}
    ''', py=r'''
        def power_set(s):
            n = len(s)
            for i in range(1 << n):                      # 2^n masks
                chosen = [s[j] for j in range(n) if i & (1 << j)]   # bit j set → take s[j]
                print(format(i, f"0{n}b"), "-> {" + ",".join(chosen) + "}")

        power_set("abc")
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        using namespace std;

        void powerSet(const string& s) {
            int n = s.size();
            for (int i = 0; i < (1 << n); i++) {        // 2^n masks
                string mask, chosen;
                for (int j = n - 1; j >= 0; j--) mask += ((i >> j) & 1) ? '1' : '0';
                for (int j = 0; j < n; j++)
                    if (i & (1 << j)) {                  // bit j set → take s[j]
                        if (!chosen.empty()) chosen += ',';
                        chosen += s[j];
                    }
                cout << mask << " -> {" << chosen << "}\n";
            }
        }

        int main() { powerSet("abc"); }
    ''', java=r'''
        public class Main {
            static void powerSet(String s) {
                int n = s.length();
                for (int i = 0; i < (1 << n); i++) {    // 2^n masks
                    StringBuilder mask = new StringBuilder(), chosen = new StringBuilder();
                    for (int j = n - 1; j >= 0; j--) mask.append((i >> j) & 1);
                    for (int j = 0; j < n; j++)
                        if ((i & (1 << j)) != 0) {       // bit j set → take s[j]
                            if (chosen.length() > 0) chosen.append(',');
                            chosen.append(s.charAt(j));
                        }
                    System.out.println(mask + " -> {" + chosen + "}");
                }
            }

            public static void main(String[] args) { powerSet("abc"); }
        }
    ''', js=r'''
        function powerSet(s) {
            const n = s.length;
            for (let i = 0; i < (1 << n); i++) {        // 2^n masks
                const chosen = [];
                for (let j = 0; j < n; j++)
                    if (i & (1 << j)) chosen.push(s[j]); // bit j set → take s[j]
                console.log(i.toString(2).padStart(n, "0"), "-> {" + chosen.join(",") + "}");
            }
        }

        powerSet("abc");
    ''')
    yield complexity("O(2^n · n)", "O(n) for the current subset")
    yield note("Bitmasks are the standard way to iterate over subsets in **bitmask DP** (travelling salesman, assignment problems): the mask *is* the state, `mask | (1 << j)` adds an element, `mask & ~(1 << j)` removes one, and `__builtin_popcount(mask)` tells how many are chosen. The recursive include/exclude version of this problem is in the Recursion topic.")

    yield section("Interview Q&A", "message-question")
    yield qa("Why does `n & (n - 1)` clear the rightmost set bit?",
             "Subtracting 1 borrows from the rightmost `1`: that bit becomes `0` and every `0` to its right becomes `1`; the bits to its left are untouched. AND-ing with `n` keeps the untouched left part and zeroes everything from that bit rightwards. Example: `12 = 1100`, `11 = 1011`, `12 & 11 = 1000`.")
    yield qa("How do you check if two integers have opposite signs without comparing them?",
             "`(x ^ y) < 0`. The sign bit of the XOR is `1` exactly when the sign bits differ. Related: `x` and `y` have the same parity iff `((x ^ y) & 1) == 0`.")
    yield qa("What is the difference between `>>` and `>>>`?",
             "`>>` is an arithmetic shift: the sign bit is copied into the vacated positions, so `-16 >> 2 = -4` (floor division). `>>>` (Java, JavaScript) is a logical shift that fills with zeros, so `-16 >>> 2` is `1073741820` — the number reinterpreted as unsigned. C++ gets the logical behaviour by casting to `unsigned`; Python has unbounded ints, so mask to a width first.")
    yield qa("Every element appears three times except one. Does XOR still work?",
             "Plain XOR does not, because `x ^ x ^ x = x` — triples do not cancel. Count the set bits per position: each of the 32 positions has a count that is a multiple of 3 plus the lone element's bit, so `count % 3` rebuilds the answer in `O(32·n)`. Alternatively use two accumulators (`ones`, `twos`) that act as a mod-3 counter per bit.")
    yield qa("How would you find the missing number in `1…n` with one slot missing, without extra space?",
             "XOR all numbers `1…n` and XOR all array elements; everything present cancels and the missing number remains. The sum formula `n(n+1)/2 − sum(arr)` also works but can overflow a 32-bit `int` for large `n`, which XOR never does.")
    yield qa("When is the lookup-table popcount actually better than Kernighan's loop?",
             "When numbers are dense (many set bits) and you count millions of them: the table is a constant four array reads with no data-dependent branch, whereas Kernighan does one iteration per set bit (up to 32). For a few calls, or sparse numbers, the loop is simpler and just as fast. In real code use the built-in — it maps to the hardware `popcnt` instruction.")


@topic(G, "recursion", "Recursion", "repeat")
def _():
    yield lead("Recursion solves a problem by calling itself on a **smaller instance** and trusting that call's answer. The problems here — rope cutting, subsets, Tower of Hanoi, Josephus, subset sum and permutations — are the templates for backtracking and dynamic programming later in the course.")
    yield define("Recursion", "a function that calls itself with an input strictly closer to a **base case**, which is answered directly. Each active call lives in its own stack frame, so the maximum depth of the recursion is also the auxiliary space.")

    yield section("How a recursive call runs", "stack-2")
    yield p("Every call pushes a frame (parameters, locals, return address) on the **call stack**; the frame is popped when the call returns. Work written *before* the recursive call happens on the way **down**, work *after* it happens on the way **up** — the trace below shows both.")
    yield multi('''
        enter 3
        enter 2
        enter 1
        base case reached
        exit 1
        exit 2
        exit 3
    ''', py=r'''
        def trace(n):
            if n == 0:                    # base case: answered without another call
                print("base case reached")
                return
            print("enter", n)             # on the way down
            trace(n - 1)                  # smaller instance
            print("exit", n)              # on the way up, after the sub-call finished

        trace(3)
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        void trace(int n) {
            if (n == 0) {                 // base case: answered without another call
                cout << "base case reached\n";
                return;
            }
            cout << "enter " << n << "\n";    // on the way down
            trace(n - 1);                     // smaller instance
            cout << "exit " << n << "\n";     // on the way up, after the sub-call finished
        }

        int main() { trace(3); }
    ''', java=r'''
        public class Main {
            static void trace(int n) {
                if (n == 0) {             // base case: answered without another call
                    System.out.println("base case reached");
                    return;
                }
                System.out.println("enter " + n);   // on the way down
                trace(n - 1);                       // smaller instance
                System.out.println("exit " + n);    // on the way up, after the sub-call finished
            }

            public static void main(String[] args) { trace(3); }
        }
    ''', js=r'''
        function trace(n) {
            if (n === 0) {                // base case: answered without another call
                console.log("base case reached");
                return;
            }
            console.log("enter", n);      // on the way down
            trace(n - 1);                 // smaller instance
            console.log("exit", n);       // on the way up, after the sub-call finished
        }

        trace(3);
    ''')
    yield diagram('''
        trace(3)                         call stack (top is the running call)
         └ trace(2)                      ┌──────────┐
            └ trace(1)                   │ trace(0) │ ← base case, 4 frames deep
               └ trace(0)  base case     │ trace(1) │
                                         │ trace(2) │
                                         │ trace(3) │
                                         └──────────┘
    ''', "Depth 4 = O(n) auxiliary space, even though the function declares no arrays")
    yield cards(
        ("Base case first", "Without it the recursion never stops: Python raises `RecursionError` at ~1000 frames, C++/Java crash with a stack overflow.", "flag"),
        ("Make progress", "Every call must move strictly towards the base case (`n-1`, `i+1`, a shorter string).", "arrow-down"),
        ("Trust the sub-call", "Assume `f(n-1)` is correct and only write how to build `f(n)` from it — the *recursive leap of faith*.", "brain"),
        ("Count the tree", "Time ≈ number of nodes in the recursion tree (branching^depth); space = its height.", "hierarchy"),
        cols=2,
    )

    yield section("Rope cutting problem", "scissors")
    yield io("n = 5, a = 2, b = 5, c = 1", "5", "n = 23, a = 12, b = 9, c = 11", "2", "n = 5, a = 4, b = 2, c = 6", "-1")
    yield p("Cut a rope of length `n` into the **maximum number of pieces**, each of length `a`, `b` or `c`; return `-1` if no exact division exists. For `n = 23` the best is `12 + 11` (2 pieces); for `n = 5` with `c = 1` it is five unit pieces.")
    yield idea("The first cut is `a`, `b` or `c`. Whichever it is, the rest of the rope is a smaller rope with the same question — so `maxPieces(n) = 1 + max(maxPieces(n-a), maxPieces(n-b), maxPieces(n-c))`. A rope of length `0` needs `0` more cuts (base case); a negative length means that cut overshoots and is reported as `-1`, which the `max` discards unless all three branches fail.")
    yield diagram('''
        maxPieces(5)  a=2 b=5 c=1
        ├── maxPieces(3)   (cut 2)
        │   ├── maxPieces(1)  → ├ (-1) → -1   ├ (-4) → -1   ├ (0) → 0     ⇒ 1
        │   ├── maxPieces(-2) → -1
        │   └── maxPieces(2)  → … ⇒ 2
        │                                          ⇒ 1 + max(1, -1, 2) = 3
        ├── maxPieces(0)   (cut 5)  → 0            ⇒ 0 + 1 = 1
        └── maxPieces(4)   (cut 1)  → … ⇒ 4        ⇒ 5
                                                   answer = max(3, 1, 5) = 5
    ''', "Three branches per node; a negative length is a dead branch (-1)")
    yield multi('''
        n=5 a=2 b=5 c=1 -> 5
        n=23 a=12 b=9 c=11 -> 2
        n=5 a=4 b=2 c=6 -> -1
    ''', py=r'''
        def max_pieces(n, a, b, c):
            if n == 0:
                return 0                      # nothing left to cut: 0 more pieces
            if n < 0:
                return -1                     # this cut overshot the rope: invalid
            res = max(max_pieces(n - a, a, b, c),
                      max_pieces(n - b, a, b, c),
                      max_pieces(n - c, a, b, c))
            if res == -1:
                return -1                     # none of the three cuts can finish the rope
            return res + 1                    # +1 for the piece cut here

        for n, a, b, c in ((5, 2, 5, 1), (23, 12, 9, 11), (5, 4, 2, 6)):
            print(f"n={n} a={a} b={b} c={c} ->", max_pieces(n, a, b, c))
    ''', cpp=r'''
        #include <iostream>
        #include <algorithm>
        using namespace std;

        int maxPieces(int n, int a, int b, int c) {
            if (n == 0) return 0;                 // nothing left to cut: 0 more pieces
            if (n < 0) return -1;                 // this cut overshot the rope: invalid
            int res = max({maxPieces(n - a, a, b, c),
                           maxPieces(n - b, a, b, c),
                           maxPieces(n - c, a, b, c)});
            if (res == -1) return -1;             // none of the three cuts can finish the rope
            return res + 1;                       // +1 for the piece cut here
        }

        int main() {
            int tests[3][4] = {{5, 2, 5, 1}, {23, 12, 9, 11}, {5, 4, 2, 6}};
            for (auto& t : tests)
                cout << "n=" << t[0] << " a=" << t[1] << " b=" << t[2] << " c=" << t[3]
                     << " -> " << maxPieces(t[0], t[1], t[2], t[3]) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int maxPieces(int n, int a, int b, int c) {
                if (n == 0) return 0;             // nothing left to cut: 0 more pieces
                if (n < 0) return -1;             // this cut overshot the rope: invalid
                int res = Math.max(maxPieces(n - a, a, b, c),
                          Math.max(maxPieces(n - b, a, b, c), maxPieces(n - c, a, b, c)));
                if (res == -1) return -1;         // none of the three cuts can finish the rope
                return res + 1;                   // +1 for the piece cut here
            }

            public static void main(String[] args) {
                int[][] tests = {{5, 2, 5, 1}, {23, 12, 9, 11}, {5, 4, 2, 6}};
                for (int[] t : tests)
                    System.out.println("n=" + t[0] + " a=" + t[1] + " b=" + t[2] + " c=" + t[3]
                                       + " -> " + maxPieces(t[0], t[1], t[2], t[3]));
            }
        }
    ''', js=r'''
        function maxPieces(n, a, b, c) {
            if (n === 0) return 0;                // nothing left to cut: 0 more pieces
            if (n < 0) return -1;                 // this cut overshot the rope: invalid
            const res = Math.max(maxPieces(n - a, a, b, c),
                                 maxPieces(n - b, a, b, c),
                                 maxPieces(n - c, a, b, c));
            if (res === -1) return -1;            // none of the three cuts can finish the rope
            return res + 1;                       // +1 for the piece cut here
        }

        for (const [n, a, b, c] of [[5, 2, 5, 1], [23, 12, 9, 11], [5, 4, 2, 6]])
            console.log(`n=${n} a=${a} b=${b} c=${c} ->`, maxPieces(n, a, b, c));
    ''')
    yield complexity("O(3^n)", "O(n) recursion depth")
    yield pitfall("Returning `0` for a negative length (instead of `-1`) silently counts an impossible cut as valid and over-reports the answer. Also note the massive overlap in the tree — `maxPieces(2)` is computed many times. Memoising on `n` turns this into the `O(n)` dynamic-programming solution in the DP topic.")

    yield section("Subsets of a string", "list-check")
    yield io("s = \"AB\"", "\"\" B A AB", "s = \"ABC\"", "\"\" C B BC A AC AB ABC")
    yield p("Generate all `2^n` subsets (subsequences keeping the original order) of a string of distinct characters.")
    yield idea("Walk the string one index at a time. For `s[i]` there are exactly two choices — **leave it out** or **put it in** — and the rest of the string is the same problem. When the index reaches the end, the accumulated `curr` is one finished subset. Two choices at each of `n` levels gives `2^n` leaves.")
    yield diagram('''
        sub("", 0)                                       s = "ABC"
        ├── exclude A → sub("", 1)
        │   ├── exclude B → sub("", 2)
        │   │   ├── exclude C → ""      ✔
        │   │   └── include C → "C"     ✔
        │   └── include B → sub("B", 2)
        │       ├── "B"  ✔     └── "BC" ✔
        └── include A → sub("A", 1)
            ├── sub("A", 2)  → "A" ✔, "AC" ✔
            └── sub("AB", 2) → "AB" ✔, "ABC" ✔
    ''', "Depth n, 2^n leaves — one per subset. Exclude first, so the empty string is printed first")
    yield multi('''
        AB -> "" B A AB (4 subsets)
        ABC -> "" C B BC A AC AB ABC (8 subsets)
    ''', py=r'''
        def subsets(s, curr, i, out):
            if i == len(s):
                out.append(curr if curr else '""')    # a finished subset
                return
            subsets(s, curr, i + 1, out)              # exclude s[i]
            subsets(s, curr + s[i], i + 1, out)       # include s[i]

        for s in ("AB", "ABC"):
            out = []
            subsets(s, "", 0, out)
            print(s, "->", " ".join(out), f"({len(out)} subsets)")
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        void subsets(const string& s, string curr, int i, vector<string>& out) {
            if (i == (int)s.size()) {
                out.push_back(curr.empty() ? "\"\"" : curr);   // a finished subset
                return;
            }
            subsets(s, curr, i + 1, out);             // exclude s[i]
            subsets(s, curr + s[i], i + 1, out);      // include s[i]
        }

        int main() {
            for (string s : {"AB", "ABC"}) {
                vector<string> out;
                subsets(s, "", 0, out);
                cout << s << " ->";
                for (const string& x : out) cout << " " << x;
                cout << " (" << out.size() << " subsets)\n";
            }
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static void subsets(String s, String curr, int i, List<String> out) {
                if (i == s.length()) {
                    out.add(curr.isEmpty() ? "\"\"" : curr);  // a finished subset
                    return;
                }
                subsets(s, curr, i + 1, out);                 // exclude s[i]
                subsets(s, curr + s.charAt(i), i + 1, out);   // include s[i]
            }

            public static void main(String[] args) {
                for (String s : new String[]{"AB", "ABC"}) {
                    List<String> out = new ArrayList<>();
                    subsets(s, "", 0, out);
                    System.out.println(s + " -> " + String.join(" ", out) + " (" + out.size() + " subsets)");
                }
            }
        }
    ''', js=r'''
        function subsets(s, curr, i, out) {
            if (i === s.length) {
                out.push(curr === "" ? '""' : curr);  // a finished subset
                return;
            }
            subsets(s, curr, i + 1, out);             // exclude s[i]
            subsets(s, curr + s[i], i + 1, out);      // include s[i]
        }

        for (const s of ["AB", "ABC"]) {
            const out = [];
            subsets(s, "", 0, out);
            console.log(s, "->", out.join(" "), `(${out.length} subsets)`);
        }
    ''')
    yield complexity("O(2^n · n)", "O(n) recursion depth (plus the output)")
    yield note("Swapping the two recursive calls (include first) lists `ABC AB AC A BC B C \"\"` instead — the set of subsets is the same, only the order changes. The iterative bitmask version of this problem is in Bit Magic → *Power set using bitmasks*. With repeated characters this prints duplicate subsets; sort the string and skip equal neighbours to avoid that.")

    yield section("Tower of Hanoi", "stack-3")
    yield io("n = 1", "Move disc 1 from A to C", "n = 2", "Move disc 1 from A to B / Move disc 2 from A to C / Move disc 1 from B to C")
    yield p("Move `n` discs from peg **A** (source) to peg **C** (destination) using peg **B** (auxiliary), under three rules:")
    yield ol(
        "Only **one disc** moves at a time.",
        "A **larger disc may never sit on a smaller** one.",
        "Only the **top disc** of a peg can be moved.",
    )
    yield diagram('''
            A          B          C                 A          B          C
            |          |          |                 |          |          |
           ═╪═         |          |      →          |          |         ═╪═
          ══╪══        |          |                 |          |        ══╪══
         ═══╪═══       |          |                 |          |       ═══╪═══
        ────┴──────────┴──────────┴──          ────┴──────────┴──────────┴──
    ''', "n = 3: the whole tower must end on C in the same order")
    yield idea("To move `n` discs A → C, the biggest disc `n` can only move when the other `n-1` discs are out of the way on B. So: move `n-1` discs A → B (using C as spare), move disc `n` A → C, then move the `n-1` discs B → C (using A as spare). The recursion is the same problem with the pegs **relabelled** — that is why the function takes the three pegs as parameters.")
    yield steps(
        ("`TOH(n-1, A, C, B)`", "Park the top `n-1` discs on the auxiliary peg B, using C as the spare."),
        ("Move disc `n` from A to C", "The largest disc makes its single move onto the empty destination."),
        ("`TOH(n-1, B, A, C)`", "Bring the `n-1` discs from B onto C, using A as the spare."),
    )
    yield formula("moves(n) = 2 · moves(n−1) + 1 = 2^n − 1        (3 discs → 7, 10 discs → 1023, 64 discs → 1.8 × 10^19)")
    yield multi('''
        n = 2
        Move disc 1 from A to B
        Move disc 2 from A to C
        Move disc 1 from B to C
        moves: 3
        n = 3
        Move disc 1 from A to C
        Move disc 2 from A to B
        Move disc 1 from C to B
        Move disc 3 from A to C
        Move disc 1 from B to A
        Move disc 2 from B to C
        Move disc 1 from A to C
        moves: 7
    ''', py=r'''
        def toh(n, src, aux, dst):
            if n == 0:
                return 0                              # no discs: no moves
            moves = toh(n - 1, src, dst, aux)         # park n-1 discs on the auxiliary peg
            print(f"Move disc {n} from {src} to {dst}")
            moves += 1 + toh(n - 1, aux, src, dst)    # bring them onto the destination
            return moves

        for n in (2, 3):
            print("n =", n)
            print("moves:", toh(n, "A", "B", "C"))
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        int toh(int n, char src, char aux, char dst) {
            if (n == 0) return 0;                         // no discs: no moves
            int moves = toh(n - 1, src, dst, aux);        // park n-1 discs on the auxiliary peg
            cout << "Move disc " << n << " from " << src << " to " << dst << "\n";
            moves += 1 + toh(n - 1, aux, src, dst);       // bring them onto the destination
            return moves;
        }

        int main() {
            for (int n : {2, 3}) {
                cout << "n = " << n << "\n";
                int moves = toh(n, 'A', 'B', 'C');      // run first: the moves print inside
                cout << "moves: " << moves << "\n";
            }
        }
    ''', java=r'''
        public class Main {
            static int toh(int n, char src, char aux, char dst) {
                if (n == 0) return 0;                     // no discs: no moves
                int moves = toh(n - 1, src, dst, aux);    // park n-1 discs on the auxiliary peg
                System.out.println("Move disc " + n + " from " + src + " to " + dst);
                moves += 1 + toh(n - 1, aux, src, dst);   // bring them onto the destination
                return moves;
            }

            public static void main(String[] args) {
                for (int n : new int[]{2, 3}) {
                    System.out.println("n = " + n);
                    System.out.println("moves: " + toh(n, 'A', 'B', 'C'));
                }
            }
        }
    ''', js=r'''
        function toh(n, src, aux, dst) {
            if (n === 0) return 0;                        // no discs: no moves
            let moves = toh(n - 1, src, dst, aux);        // park n-1 discs on the auxiliary peg
            console.log(`Move disc ${n} from ${src} to ${dst}`);
            moves += 1 + toh(n - 1, aux, src, dst);       // bring them onto the destination
            return moves;
        }

        for (const n of [2, 3]) {
            console.log("n =", n);
            console.log("moves:", toh(n, "A", "B", "C"));
        }
    ''')
    yield complexity("O(2^n) moves", "O(n) recursion depth")
    yield pitfall("The classic slip is the **peg order** in the two recursive calls. With the signature `TOH(n, source, auxiliary, destination)` the first call is `TOH(n-1, A, C, B)` (destination becomes the spare) and the second is `TOH(n-1, B, A, C)` (source becomes the spare). Using `n == 1` as the base case also works; `n == 0` avoids a special-cased print.")

    yield section("Josephus problem (elimination game)", "users")
    yield io("n = 7, k = 3", "3", "n = 8, k = 2", "0")
    yield p("`n` people stand in a circle numbered `0 … n-1`. Starting at `0`, every **kth** person is eliminated and the count restarts from the next person. Which position survives?")
    yield idea("After the first elimination (`k-1` is removed), the circle has `n-1` people and the count restarts at position `k`. If we **renumber** so that position `k` becomes `0`, the remaining game is exactly `josephus(n-1, k)`. Its survivor `j` in the renumbered circle sits at `(j + k) % n` in the original one — hence `jos(n, k) = (jos(n-1, k) + k) % n`, with `jos(1, k) = 0`.")
    yield diagram('''
        jos(1,3) = 0
        jos(2,3) = (0 + 3) % 2 = 1
        jos(3,3) = (1 + 3) % 3 = 1
        jos(4,3) = (1 + 3) % 4 = 0
        jos(5,3) = (0 + 3) % 5 = 3
        jos(6,3) = (3 + 3) % 6 = 0
        jos(7,3) = (0 + 3) % 7 = 3     ← survivor for n = 7, k = 3
    ''', "Unwinding the recursion from the base case up")
    yield multi('''
        n=7 k=3 -> 3
        n=8 k=2 -> 0
        n=5 k=2 -> 2
    ''', py=r'''
        def josephus(n, k):
            if n == 1:
                return 0                          # one person left: position 0 survives
            return (josephus(n - 1, k) + k) % n   # shift the smaller game's answer back by k

        for n, k in ((7, 3), (8, 2), (5, 2)):
            print(f"n={n} k={k} ->", josephus(n, k))
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        int josephus(int n, int k) {
            if (n == 1) return 0;                     // one person left: position 0 survives
            return (josephus(n - 1, k) + k) % n;      // shift the smaller game's answer back by k
        }

        int main() {
            int tests[3][2] = {{7, 3}, {8, 2}, {5, 2}};
            for (auto& t : tests)
                cout << "n=" << t[0] << " k=" << t[1] << " -> " << josephus(t[0], t[1]) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int josephus(int n, int k) {
                if (n == 1) return 0;                 // one person left: position 0 survives
                return (josephus(n - 1, k) + k) % n;  // shift the smaller game's answer back by k
            }

            public static void main(String[] args) {
                int[][] tests = {{7, 3}, {8, 2}, {5, 2}};
                for (int[] t : tests)
                    System.out.println("n=" + t[0] + " k=" + t[1] + " -> " + josephus(t[0], t[1]));
            }
        }
    ''', js=r'''
        function josephus(n, k) {
            if (n === 1) return 0;                    // one person left: position 0 survives
            return (josephus(n - 1, k) + k) % n;      // shift the smaller game's answer back by k
        }

        for (const [n, k] of [[7, 3], [8, 2], [5, 2]])
            console.log(`n=${n} k=${k} ->`, josephus(n, k));
    ''')
    yield complexity("O(n)", "O(n) recursion depth — or O(1) with a loop")
    yield p("To **see** the eliminations, simulate the circle with a list: the next victim is `(idx + k - 1) % size` and the count resumes at that index.")
    yield multi('''
        remove 2 -> left: 0 1 3 4 5 6
        remove 5 -> left: 0 1 3 4 6
        remove 1 -> left: 0 3 4 6
        remove 6 -> left: 0 3 4
        remove 4 -> left: 0 3
        remove 0 -> left: 3
        survivor: 3
    ''', py=r'''
        def simulate(n, k):
            people = list(range(n))
            idx = 0
            while len(people) > 1:
                idx = (idx + k - 1) % len(people)     # count k people from idx, wrapping around
                removed = people.pop(idx)             # the next person now sits at idx
                print("remove", removed, "-> left:", " ".join(map(str, people)))
            print("survivor:", people[0])

        simulate(7, 3)
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        void simulate(int n, int k) {
            vector<int> people;
            for (int i = 0; i < n; i++) people.push_back(i);
            int idx = 0;
            while (people.size() > 1) {
                int size = people.size();
                idx = (idx + k - 1) % size;               // count k people from idx, wrapping around
                int removed = people[idx];
                people.erase(people.begin() + idx);       // the next person now sits at idx
                cout << "remove " << removed << " -> left:";
                for (int x : people) cout << " " << x;
                cout << "\n";
            }
            cout << "survivor: " << people[0] << "\n";
        }

        int main() { simulate(7, 3); }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static void simulate(int n, int k) {
                List<Integer> people = new ArrayList<>();
                for (int i = 0; i < n; i++) people.add(i);
                int idx = 0;
                while (people.size() > 1) {
                    idx = (idx + k - 1) % people.size();  // count k people from idx, wrapping around
                    int removed = people.remove(idx);     // the next person now sits at idx
                    StringBuilder sb = new StringBuilder();
                    for (int x : people) sb.append(' ').append(x);
                    System.out.println("remove " + removed + " -> left:" + sb);
                }
                System.out.println("survivor: " + people.get(0));
            }

            public static void main(String[] args) { simulate(7, 3); }
        }
    ''', js=r'''
        function simulate(n, k) {
            const people = Array.from({ length: n }, (_, i) => i);
            let idx = 0;
            while (people.length > 1) {
                idx = (idx + k - 1) % people.length;      // count k people from idx, wrapping around
                const [removed] = people.splice(idx, 1);  // the next person now sits at idx
                console.log("remove", removed, "-> left:", people.join(" "));
            }
            console.log("survivor:", people[0]);
        }

        simulate(7, 3);
    ''')
    yield complexity("O(n²) with list deletion, O(n · k) with a linked circle", "O(n)")
    yield pitfall("Mixing up **0-based and 1-based** numbering. The formula above returns a 0-based position; if the people are numbered `1 … n` the survivor is `jos(n, k) + 1` (for `n = 7, k = 3` that is `4`). Also `people.remove(idx)` in Java must receive an `int`, not an `Integer` — `remove(Integer)` removes by *value*.")

    yield section("Subset sum (count the subsets)", "coin")
    yield io("arr = [10, 5, 2, 3, 6], sum = 8", "2", "arr = [10, 20, 15], sum = 0", "1")
    yield p("Count the subsets of `arr` whose elements add up to `sum`. For `{10, 5, 2, 3, 6}` and `8` there are two: `{5, 3}` and `{2, 6}`. For `sum = 0` the empty subset always counts, so the answer is at least `1`.")
    yield idea("Look at the **last** element `arr[n-1]`. Either it is left out — count the subsets of the first `n-1` elements that reach `sum` — or it is taken — count those that reach `sum - arr[n-1]`. Add the two. With no elements left (`n == 0`) there is exactly one subset, the empty one, and it works only if the remaining `sum` is `0`.")
    yield diagram('''
        count(n=3, sum=3)   arr = {1, 2, 3}
        ├── exclude 3 → count(2, 3)
        │   ├── exclude 2 → count(1, 3) → count(0,3)=0, count(0,2)=0          ⇒ 0
        │   └── include 2 → count(1, 1) → count(0,1)=0, count(0,0)=1  {1,2}  ⇒ 1
        └── include 3 → count(2, 0)
            ├── exclude 2 → count(1, 0) → count(0,0)=1  {3}, count(0,-1)=0   ⇒ 1
            └── include 2 → count(1,-2) → 0                                   ⇒ 0
                                                                       total = 2
    ''', "Each leaf with sum 0 is one valid subset")
    yield multi('''
        10 5 2 3 6 | sum 8 -> 2
        10 20 15 | sum 0 -> 1
        1 2 3 | sum 3 -> 2
    ''', py=r'''
        def count_subsets(arr, n, target):
            if n == 0:
                return 1 if target == 0 else 0            # empty subset: valid only if nothing is left to reach
            return (count_subsets(arr, n - 1, target)                 # exclude arr[n-1]
                    + count_subsets(arr, n - 1, target - arr[n - 1]))  # include arr[n-1]

        for arr, target in (([10, 5, 2, 3, 6], 8), ([10, 20, 15], 0), ([1, 2, 3], 3)):
            print(" ".join(map(str, arr)), "| sum", target, "->", count_subsets(arr, len(arr), target))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        int countSubsets(const vector<int>& arr, int n, int target) {
            if (n == 0) return target == 0 ? 1 : 0;       // empty subset: valid only if nothing is left to reach
            return countSubsets(arr, n - 1, target)                   // exclude arr[n-1]
                 + countSubsets(arr, n - 1, target - arr[n - 1]);     // include arr[n-1]
        }

        int main() {
            vector<pair<vector<int>, int>> tests = {{{10, 5, 2, 3, 6}, 8}, {{10, 20, 15}, 0}, {{1, 2, 3}, 3}};
            for (auto& [arr, target] : tests) {
                for (int x : arr) cout << x << " ";
                cout << "| sum " << target << " -> " << countSubsets(arr, arr.size(), target) << "\n";
            }
        }
    ''', java=r'''
        public class Main {
            static int countSubsets(int[] arr, int n, int target) {
                if (n == 0) return target == 0 ? 1 : 0;   // empty subset: valid only if nothing is left to reach
                return countSubsets(arr, n - 1, target)               // exclude arr[n-1]
                     + countSubsets(arr, n - 1, target - arr[n - 1]); // include arr[n-1]
            }

            public static void main(String[] args) {
                int[][] arrays = {{10, 5, 2, 3, 6}, {10, 20, 15}, {1, 2, 3}};
                int[] targets = {8, 0, 3};
                for (int t = 0; t < arrays.length; t++) {
                    StringBuilder sb = new StringBuilder();
                    for (int x : arrays[t]) sb.append(x).append(' ');
                    System.out.println(sb + "| sum " + targets[t] + " -> "
                                       + countSubsets(arrays[t], arrays[t].length, targets[t]));
                }
            }
        }
    ''', js=r'''
        function countSubsets(arr, n, target) {
            if (n === 0) return target === 0 ? 1 : 0;     // empty subset: valid only if nothing is left to reach
            return countSubsets(arr, n - 1, target)                   // exclude arr[n-1]
                 + countSubsets(arr, n - 1, target - arr[n - 1]);     // include arr[n-1]
        }

        for (const [arr, target] of [[[10, 5, 2, 3, 6], 8], [[10, 20, 15], 0], [[1, 2, 3], 3]])
            console.log(arr.join(" "), "| sum", target, "->", countSubsets(arr, arr.length, target));
    ''')
    yield complexity("O(2^n)", "O(n) recursion depth")
    yield note("Pruning `target < 0` (return `0` early) is safe only when all elements are non-negative. The same recurrence, memoised on `(n, target)`, is the `O(n · sum)` subset-sum DP; replacing `+` with `or` answers the *decision* version (does any subset reach the sum?).")

    yield section("Print all permutations of a string", "arrows-shuffle")
    yield io("s = \"AB\"", "AB BA", "s = \"ABC\"", "ABC ACB BAC BCA CBA CAB")
    yield p("Print every arrangement of the characters of `s` — there are `n!` of them for `n` distinct characters.")
    yield idea("Fix position `i` by trying **every** character from `i` to the end in that slot (swap it in), recursively permute the rest `i+1 … n-1`, then **swap it back** so the next candidate starts from the original arrangement. The swap-back is what makes this *backtracking*: the shared array is restored after every choice.")
    yield diagram('''
        permute(ABC, i=0)
        ├── swap(0,0) → A|BC  permute(i=1)
        │                ├── swap(1,1) → AB|C → ABC ✔
        │                └── swap(1,2) → AC|B → ACB ✔   (swap back → ABC)
        ├── swap(0,1) → B|AC  permute(i=1)
        │                ├── BAC ✔
        │                └── BCA ✔                       (swap back → ABC)
        └── swap(0,2) → C|BA  permute(i=1)
                         ├── CBA ✔
                         └── CAB ✔                       (swap back → ABC)
    ''', "n choices at level 0, n−1 at level 1, … → n! leaves. Note the order is not alphabetical")
    yield multi('''
        AB -> AB BA
        ABC -> ABC ACB BAC BCA CBA CAB
    ''', py=r'''
        def permute(chars, i, out):
            n = len(chars)
            if i == n - 1:
                out.append("".join(chars))            # every position fixed: one permutation
                return
            for j in range(i, n):
                chars[i], chars[j] = chars[j], chars[i]   # choose chars[j] for position i
                permute(chars, i + 1, out)
                chars[i], chars[j] = chars[j], chars[i]   # backtrack: undo the swap

        for s in ("AB", "ABC"):
            out = []
            permute(list(s), 0, out)
            print(s, "->", " ".join(out))
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        #include <vector>
        #include <utility>
        using namespace std;

        void permute(string& s, int i, vector<string>& out) {
            int n = s.size();
            if (i == n - 1) {
                out.push_back(s);                     // every position fixed: one permutation
                return;
            }
            for (int j = i; j < n; j++) {
                swap(s[i], s[j]);                     // choose s[j] for position i
                permute(s, i + 1, out);
                swap(s[i], s[j]);                     // backtrack: undo the swap
            }
        }

        int main() {
            for (string s : {"AB", "ABC"}) {
                vector<string> out;
                string work = s;
                permute(work, 0, out);
                cout << s << " ->";
                for (const string& p : out) cout << " " << p;
                cout << "\n";
            }
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static void permute(char[] s, int i, List<String> out) {
                int n = s.length;
                if (i == n - 1) {
                    out.add(new String(s));           // every position fixed: one permutation
                    return;
                }
                for (int j = i; j < n; j++) {
                    char t = s[i]; s[i] = s[j]; s[j] = t;   // choose s[j] for position i
                    permute(s, i + 1, out);
                    t = s[i]; s[i] = s[j]; s[j] = t;        // backtrack: undo the swap
                }
            }

            public static void main(String[] args) {
                for (String s : new String[]{"AB", "ABC"}) {
                    List<String> out = new ArrayList<>();
                    permute(s.toCharArray(), 0, out);
                    System.out.println(s + " -> " + String.join(" ", out));
                }
            }
        }
    ''', js=r'''
        function permute(chars, i, out) {
            const n = chars.length;
            if (i === n - 1) {
                out.push(chars.join(""));             // every position fixed: one permutation
                return;
            }
            for (let j = i; j < n; j++) {
                [chars[i], chars[j]] = [chars[j], chars[i]];   // choose chars[j] for position i
                permute(chars, i + 1, out);
                [chars[i], chars[j]] = [chars[j], chars[i]];   // backtrack: undo the swap
            }
        }

        for (const s of ["AB", "ABC"]) {
            const out = [];
            permute([...s], 0, out);
            console.log(s, "->", out.join(" "));
        }
    ''')
    yield complexity("O(n! · n)", "O(n) recursion depth, swapping in place")
    yield pitfall("Forgetting the **second swap** corrupts the array for the next `j` and produces duplicates and missing permutations. The in-place swap uses no extra array, but the auxiliary space is still `O(n)` because of the recursion depth — not `O(1)`. With repeated characters (`\"AAB\"`) this prints duplicates; skip a `j` whose character was already tried at this position, or use a frequency map.")

    yield section("Recursion trees at a glance", "hierarchy")
    yield p("The cost of a recursive solution is read off its tree: **time** is roughly the number of nodes (branching factor to the power of the depth), **auxiliary space** is the height. Overlapping subproblems (the same node appearing many times) are the signal to memoise.")
    yield table(
        ["Problem", "Branching", "Depth", "Time", "Aux space", "Overlap?"],
        ["Rope cutting", "3", "`n / min(a,b,c)`", "`O(3^n)`", "`O(n)`", "yes → DP `O(n)`"],
        ["Subsets of a string", "2", "`n`", "`O(2^n · n)`", "`O(n)`", "no — every leaf is a distinct answer"],
        ["Tower of Hanoi", "2", "`n`", "`O(2^n)`", "`O(n)`", "no — every move is output"],
        ["Josephus", "1", "`n`", "`O(n)`", "`O(n)` (loop: `O(1)`)", "—"],
        ["Subset sum count", "2", "`n`", "`O(2^n)`", "`O(n)`", "yes → DP `O(n · sum)`"],
        ["Permutations", "`n, n-1, …, 1`", "`n`", "`O(n! · n)`", "`O(n)`", "no — every leaf is a distinct answer"],
    )
    yield warn("Each language limits recursion depth: Python stops at about **1000** frames (`sys.setrecursionlimit` raises it, but the C stack still overflows around tens of thousands), Java and C++ overflow their thread stack at roughly `10^4`–`10^5` frames depending on frame size, Node around `10^4`. A linear recursion over `n = 10^5` elements must be rewritten as a loop or use an explicit stack.", "Depth limits")

    yield section("Interview Q&A", "message-question")
    yield qa("What are the two things every recursive function needs?",
             "A **base case** that returns without recursing, and a **recursive case** whose argument is strictly closer to the base case. Missing or unreachable base cases give infinite recursion; a recursive case that does not shrink the input (e.g. `f(n)` calling `f(n)`) does the same.")
    yield qa("What is tail recursion, and does it help?",
             "A call is tail-recursive when the recursive call is the very last action, with nothing left to do after it returns — `jos` above is *not*, because it still adds `k` and takes `% n` after the call returns. C++ compilers optimise tail calls at `-O2`; Python and Java never do, JavaScript engines in practice do not either. So in those languages tail recursion is a style, not a space saving — convert to a loop when depth matters.")
    yield qa("Why is Tower of Hanoi `O(2^n)` and not `O(n)`? There is only one `print` per call.",
             "Because there are `2^n − 1` calls that print: `moves(n) = 2·moves(n−1) + 1`. The recursion tree is a full binary tree of height `n`, and every node does `O(1)` work, so the total is the number of nodes. A single `print` per call does not mean a linear number of calls.")
    yield qa("How do you turn an exponential recursion into a fast one?",
             "Check whether the same subproblem appears many times in the tree (rope cutting: `maxPieces(2)` is recomputed; subset sum: `(n, target)` repeats). If so, store each result the first time it is computed — **memoisation** (top-down DP) — or fill a table from the base cases up (bottom-up DP). If every leaf is a distinct required answer (subsets, permutations, Hanoi) the output itself is exponential and no algorithm can be faster.")
    yield qa("Recursion vs iteration — when to pick which?",
             "Recursion wins when the problem is naturally a tree of choices (subsets, permutations, Hanoi, tree traversals): the call stack keeps the partial state for you and the code mirrors the definition. Iteration wins for linear problems (sum, factorial, Josephus) where recursion only adds `O(n)` stack and the risk of overflow. Any recursion can be made iterative with an explicit stack; it is just more code.")
    yield qa("What does the Josephus formula `(jos(n-1, k) + k) % n` actually mean?",
             "After the first kill the circle is one person smaller and the count restarts at position `k` (0-based). Renumber that person as `0` and the rest is a smaller instance of the game. Its survivor `j` corresponds to `j + k` in the original numbering — the `% n` wraps around the circle. Unwinding from `jos(1) = 0` gives the answer in `O(n)` with no simulation.")
