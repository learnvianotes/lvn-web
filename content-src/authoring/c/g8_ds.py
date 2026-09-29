from kit import *

G = "Data Structures & Algorithms in C"


@topic(G, "linked-list", "Singly Linked List", "list")
def _():
    yield lead("A chain of heap-allocated nodes, each pointing to the next. O(1) insertion at the head, O(n) search — and the most common C interview data structure.")
    yield flow("`head`", "[1 | •]", "[2 | •]", "[3 | •]", "`NULL`")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        typedef struct Node {
            int data;
            struct Node *next;
        } Node;

        Node *new_node(int v) {
            Node *n = malloc(sizeof *n);
            if (!n) { perror("malloc"); exit(EXIT_FAILURE); }
            n->data = v;
            n->next = NULL;
            return n;
        }

        void push_front(Node **head, int v) {        /* O(1) */
            Node *n = new_node(v);
            n->next = *head;
            *head = n;
        }

        void push_back(Node **head, int v) {         /* O(n): walk to the tail */
            Node **pp = head;
            while (*pp) pp = &(*pp)->next;
            *pp = new_node(v);
        }

        int remove_value(Node **head, int v) {       /* pointer-to-pointer: no special case for head */
            for (Node **pp = head; *pp; pp = &(*pp)->next) {
                if ((*pp)->data == v) {
                    Node *dead = *pp;
                    *pp = dead->next;
                    free(dead);
                    return 1;
                }
            }
            return 0;
        }

        void reverse(Node **head) {                  /* O(n), O(1) space */
            Node *prev = NULL, *cur = *head;
            while (cur) {
                Node *next = cur->next;
                cur->next = prev;
                prev = cur;
                cur = next;
            }
            *head = prev;
        }

        void print(const Node *n) {
            for (; n; n = n->next) printf("%d -> ", n->data);
            printf("NULL\n");
        }

        void free_list(Node *n) {
            while (n) { Node *next = n->next; free(n); n = next; }
        }

        int main(void) {
            Node *head = NULL;
            push_back(&head, 2);
            push_back(&head, 3);
            push_front(&head, 1);
            push_back(&head, 4);
            print(head);
            remove_value(&head, 1);
            remove_value(&head, 3);
            print(head);
            reverse(&head);
            print(head);
            free_list(head);
            return 0;
        }
    ''', out='''
        1 -> 2 -> 3 -> 4 -> NULL
        2 -> 4 -> NULL
        4 -> 2 -> NULL
    ''')
    yield section("Classic interview operations", "puzzle")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        typedef struct Node { int data; struct Node *next; } Node;

        Node *build(const int *a, int n) {
            Node *head = NULL, **tail = &head;
            for (int i = 0; i < n; i++) {
                *tail = malloc(sizeof **tail);
                if (!*tail) exit(1);
                (*tail)->data = a[i];
                (*tail)->next = NULL;
                tail = &(*tail)->next;
            }
            return head;
        }

        Node *middle(Node *head) {                   /* slow/fast pointers */
            Node *slow = head, *fast = head;
            while (fast && fast->next) { slow = slow->next; fast = fast->next->next; }
            return slow;
        }

        int has_cycle(const Node *head) {            /* Floyd's tortoise and hare */
            const Node *slow = head, *fast = head;
            while (fast && fast->next) {
                slow = slow->next;
                fast = fast->next->next;
                if (slow == fast) return 1;
            }
            return 0;
        }

        Node *merge_sorted(Node *a, Node *b) {       /* splice two sorted lists */
            Node dummy = {0, NULL}, *t = &dummy;
            while (a && b) {
                if (a->data <= b->data) { t->next = a; a = a->next; }
                else                    { t->next = b; b = b->next; }
                t = t->next;
            }
            t->next = a ? a : b;
            return dummy.next;
        }

        int main(void) {
            int x[] = {1, 4, 7, 9, 12};
            int y[] = {2, 3, 10};
            Node *a = build(x, 5), *b = build(y, 3);
            printf("middle of a: %d\n", middle(a)->data);
            printf("cycle? %d\n", has_cycle(a));

            Node *m = merge_sorted(a, b);
            for (Node *n = m; n; n = n->next) printf("%d ", n->data);
            printf("\n");

            Node *last = m;                          /* make a cycle to test detection */
            while (last->next) last = last->next;
            last->next = m->next->next;
            printf("cycle? %d\n", has_cycle(m));
            last->next = NULL;                       /* break it again before freeing */

            while (m) { Node *next = m->next; free(m); m = next; }
            return 0;
        }
    ''', out='''
        middle of a: 7
        cycle? 0
        1 2 3 4 7 9 10 12
        cycle? 1
    ''')
    yield table(
        ["Operation", "Singly linked list", "Array"],
        ["Access k-th", "O(n)", "O(1)"],
        ["Insert/delete at head", "O(1)", "O(n)"],
        ["Insert/delete after a known node", "O(1)", "O(n)"],
        ["Search", "O(n)", "O(n) (O(log n) if sorted)"],
        ["Memory", "Extra pointer per node; scattered (cache-unfriendly)", "Contiguous"],
    )
    yield qa("How do you reverse a singly linked list?",
             "Iteratively with three pointers: `prev = NULL`, `cur = head`; for each node save `next`, point `cur->next` to `prev`, then advance `prev = cur`, `cur = next`. At the end `prev` is the new head. O(n) time, O(1) space.")
    yield qa("How do you detect a cycle in a linked list?",
             "Floyd’s algorithm: move a slow pointer one step and a fast pointer two steps; if they ever meet there is a cycle, if the fast pointer reaches `NULL` there isn’t. To find the cycle start, reset one pointer to the head and move both one step at a time — they meet at the entry.")


@topic(G, "doubly-linked-list", "Doubly & Circular Linked Lists", "arrows-left-right")
def _():
    yield lead("A doubly linked list stores `prev` and `next` pointers, so a node can be removed in O(1) given only a pointer to it and the list can be walked both ways.")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        typedef struct DNode {
            int data;
            struct DNode *prev, *next;
        } DNode;

        /* circular list with a sentinel: no NULL checks at the ends */
        typedef struct { DNode head; size_t size; } List;

        void list_init(List *l) { l->head.prev = l->head.next = &l->head; l->size = 0; }

        void insert_after(List *l, DNode *pos, int v) {
            DNode *n = malloc(sizeof *n);
            if (!n) exit(1);
            n->data = v;
            n->prev = pos;
            n->next = pos->next;
            pos->next->prev = n;
            pos->next = n;
            l->size++;
        }

        void push_front(List *l, int v) { insert_after(l, &l->head, v); }
        void push_back(List *l, int v)  { insert_after(l, l->head.prev, v); }

        void unlink_node(List *l, DNode *n) {        /* O(1): no search for the predecessor */
            n->prev->next = n->next;
            n->next->prev = n->prev;
            free(n);
            l->size--;
        }

        void print(const List *l) {
            for (const DNode *n = l->head.next; n != &l->head; n = n->next) printf("%d ", n->data);
            printf("| backwards: ");
            for (const DNode *n = l->head.prev; n != &l->head; n = n->prev) printf("%d ", n->data);
            printf("(size %zu)\n", l->size);
        }

        int main(void) {
            List l;
            list_init(&l);
            push_back(&l, 2); push_back(&l, 3); push_front(&l, 1); push_back(&l, 4);
            print(&l);
            unlink_node(&l, l.head.next->next);       /* remove the 2 */
            print(&l);
            while (l.size) unlink_node(&l, l.head.next);
            print(&l);
            return 0;
        }
    ''', out='''
        1 2 3 4 | backwards: 4 3 2 1 (size 4)
        1 3 4 | backwards: 4 3 1 (size 3)
        | backwards: (size 0)
    ''')
    yield note("A **sentinel** (dummy head) node makes the list circular and never empty, which removes every special case for the first and last element. The Linux kernel’s `list_head` uses this design.")
    yield table(
        ["Variant", "Pros", "Cons"],
        ["Singly linked", "Smallest nodes, simplest", "Can’t go back; deleting needs the predecessor"],
        ["Doubly linked", "O(1) delete of any node, both directions", "Two pointers per node"],
        ["Circular", "Round-robin traversal; no NULL end", "Must stop by comparing with the start"],
    )
    yield qa("Why is deletion O(1) in a doubly linked list but O(n) in a singly linked one?",
             "To unlink a node you must update its predecessor’s `next`. A doubly linked node knows its predecessor (`prev`); in a singly linked list you have to walk from the head to find it (unless you already hold it).")


@topic(G, "stack-queue", "Stack & Queue", "stack-2")
def _():
    yield lead("A **stack** is last-in-first-out (push/pop at one end); a **queue** is first-in-first-out (enqueue at the back, dequeue at the front). In C you build them on an array or a linked list.")
    yield section("Array-based stack", "stack")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdbool.h>
        #include <string.h>

        #define CAP 64

        typedef struct { char items[CAP]; int top; } Stack;   /* top = count */

        bool push(Stack *s, char c) { if (s->top == CAP) return false; s->items[s->top++] = c; return true; }
        bool pop(Stack *s, char *out) { if (s->top == 0) return false; *out = s->items[--s->top]; return true; }

        bool balanced(const char *expr) {
            Stack s = {.top = 0};
            for (; *expr; expr++) {
                char c = *expr, open;
                if (strchr("([{", c)) {
                    if (!push(&s, c)) return false;
                } else if (strchr(")]}", c)) {
                    if (!pop(&s, &open)) return false;
                    if ((c == ')' && open != '(') || (c == ']' && open != '[') || (c == '}' && open != '{'))
                        return false;
                }
            }
            return s.top == 0;
        }

        int main(void) {
            const char *tests[] = {"{a[b(c)d]e}", "(]", "((())", "f(x[0])"};
            for (int i = 0; i < 4; i++) printf("%-12s %s\n", tests[i], balanced(tests[i]) ? "balanced" : "NOT balanced");
            return 0;
        }
    ''', out='''
        {a[b(c)d]e}  balanced
        (]           NOT balanced
        ((())        NOT balanced
        f(x[0])      balanced
    ''')
    yield section("Circular-buffer queue", "refresh")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdbool.h>

        #define QCAP 4

        typedef struct { int buf[QCAP]; int head, count; } Queue;

        bool enqueue(Queue *q, int v) {
            if (q->count == QCAP) return false;               /* full */
            q->buf[(q->head + q->count) % QCAP] = v;          /* wrap around */
            q->count++;
            return true;
        }

        bool dequeue(Queue *q, int *out) {
            if (q->count == 0) return false;                  /* empty */
            *out = q->buf[q->head];
            q->head = (q->head + 1) % QCAP;
            q->count--;
            return true;
        }

        int main(void) {
            Queue q = {.head = 0, .count = 0};
            for (int i = 1; i <= 5; i++)
                if (!enqueue(&q, i * 10)) printf("queue full, dropped %d\n", i * 10);
            int v;
            dequeue(&q, &v); printf("got %d\n", v);
            dequeue(&q, &v); printf("got %d\n", v);
            enqueue(&q, 60); enqueue(&q, 70);                  /* reuses freed slots */
            while (dequeue(&q, &v)) printf("%d ", v);
            printf("\n");
            return 0;
        }
    ''', out='''
        queue full, dropped 50
        got 10
        got 20
        30 40 60 70
    ''')
    yield section("Linked-list stack (unbounded)", "list")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        typedef struct SNode { int val; struct SNode *below; } SNode;

        void push(SNode **top, int v) {
            SNode *n = malloc(sizeof *n);
            if (!n) exit(1);
            n->val = v; n->below = *top; *top = n;
        }

        int pop(SNode **top) {                     /* caller checks for empty */
            SNode *n = *top;
            int v = n->val;
            *top = n->below;
            free(n);
            return v;
        }

        /* evaluate a postfix (RPN) expression of single digits */
        int eval_rpn(const char *s) {
            SNode *st = NULL;
            for (; *s; s++) {
                if (*s >= '0' && *s <= '9') { push(&st, *s - '0'); continue; }
                if (*s == ' ') continue;
                int b = pop(&st), a = pop(&st);
                push(&st, *s == '+' ? a + b : *s == '-' ? a - b : *s == '*' ? a * b : a / b);
            }
            return pop(&st);
        }

        int main(void) {
            printf("%d\n", eval_rpn("3 4 + 2 *"));      /* (3 + 4) * 2 */
            printf("%d\n", eval_rpn("5 1 2 + 4 * + 3 -"));
            return 0;
        }
    ''', out='''
        14
        14
    ''')
    yield table(
        ["", "Array", "Linked list"],
        ["Push/pop, enqueue/dequeue", "O(1)", "O(1)"],
        ["Capacity", "Fixed (or amortised O(1) with `realloc`)", "Unbounded"],
        ["Memory", "Compact, cache-friendly", "One `malloc` + pointer per element"],
    )
    yield qa("How do you implement a queue using two stacks?",
             "Push onto an *in* stack. To dequeue, if the *out* stack is empty, pop everything from *in* and push it onto *out* (reversing the order), then pop from *out*. Each element moves at most twice, so operations are amortised O(1).")
    yield qa("How do you tell a full circular buffer from an empty one?",
             "`head == tail` is ambiguous, so either keep a separate `count` (as above), or always leave one slot unused (`(tail + 1) % CAP == head` means full).")


@topic(G, "binary-search-tree", "Binary Search Tree", "binary-tree")
def _():
    yield lead("A binary tree where every left descendant is smaller and every right descendant is larger than the node. Search, insert and delete are O(h) — O(log n) when balanced, O(n) when degenerate.")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        typedef struct Tree { int key; struct Tree *left, *right; } Tree;

        Tree *insert(Tree *t, int key) {
            if (!t) {
                t = malloc(sizeof *t);
                if (!t) exit(1);
                t->key = key; t->left = t->right = NULL;
            } else if (key < t->key) t->left = insert(t->left, key);
            else if (key > t->key)   t->right = insert(t->right, key);
            return t;                                  /* duplicates ignored */
        }

        const Tree *search(const Tree *t, int key) {
            while (t && t->key != key) t = key < t->key ? t->left : t->right;
            return t;
        }

        Tree *delete(Tree *t, int key) {
            if (!t) return NULL;
            if (key < t->key) t->left = delete(t->left, key);
            else if (key > t->key) t->right = delete(t->right, key);
            else if (!t->left || !t->right) {          /* 0 or 1 child */
                Tree *child = t->left ? t->left : t->right;
                free(t);
                return child;
            } else {                                   /* 2 children: copy in-order successor */
                Tree *s = t->right;
                while (s->left) s = s->left;
                t->key = s->key;
                t->right = delete(t->right, s->key);
            }
            return t;
        }

        void inorder(const Tree *t)  { if (t) { inorder(t->left); printf("%d ", t->key); inorder(t->right); } }
        void preorder(const Tree *t) { if (t) { printf("%d ", t->key); preorder(t->left); preorder(t->right); } }
        int height(const Tree *t) {
            if (!t) return 0;
            int l = height(t->left), r = height(t->right);
            return 1 + (l > r ? l : r);
        }
        void destroy(Tree *t) { if (t) { destroy(t->left); destroy(t->right); free(t); } }  /* postorder */

        int main(void) {
            Tree *root = NULL;
            int keys[] = {50, 30, 70, 20, 40, 60, 80};
            for (int i = 0; i < 7; i++) root = insert(root, keys[i]);

            printf("inorder:  "); inorder(root);  printf("\n");
            printf("preorder: "); preorder(root); printf("\n");
            printf("height %d, has 60? %s, has 65? %s\n", height(root),
                   search(root, 60) ? "yes" : "no", search(root, 65) ? "yes" : "no");

            root = delete(root, 50);                   /* root with two children */
            printf("after deleting 50: "); inorder(root); printf("(root %d)\n", root->key);
            destroy(root);
            return 0;
        }
    ''', out='''
        inorder:  20 30 40 50 60 70 80
        preorder: 50 30 20 40 70 60 80
        height 3, has 60? yes, has 65? no
        after deleting 50: 20 30 40 60 70 80 (root 60)
    ''')
    yield table(
        ["Traversal", "Order", "Use"],
        ["In-order", "left, node, right", "Sorted output of a BST"],
        ["Pre-order", "node, left, right", "Copy / serialise a tree"],
        ["Post-order", "left, right, node", "Free a tree (children before parent)"],
        ["Level-order", "breadth-first with a queue", "Print by levels, shortest path in unweighted trees"],
    )
    yield warn("Inserting already-sorted keys produces a linked list (height n) and O(n) operations. Self-balancing trees (AVL, red-black) keep the height O(log n).")
    yield qa("How do you check whether a binary tree is a valid BST?",
             "Recurse with an allowed range: every node’s key must lie strictly between a lower and upper bound inherited from its ancestors (`check(node->left, lo, node->key)`, `check(node->right, node->key, hi)`). Comparing a node only with its direct children is not enough.")


@topic(G, "hash-table", "Hash Table", "hash")
def _():
    yield lead("An array of buckets indexed by `hash(key) % capacity`. With a good hash function and a reasonable load factor, lookup, insert and delete are O(1) on average.")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>

        #define NBUCKETS 8

        typedef struct Entry {
            char *key;
            int value;
            struct Entry *next;               /* separate chaining */
        } Entry;

        typedef struct { Entry *buckets[NBUCKETS]; size_t count; } Map;

        unsigned long hash(const char *s) {   /* djb2 by Dan Bernstein */
            unsigned long h = 5381;
            for (; *s; s++) h = h * 33 + (unsigned char)*s;
            return h;
        }

        void map_put(Map *m, const char *key, int value) {
            size_t i = hash(key) % NBUCKETS;
            for (Entry *e = m->buckets[i]; e; e = e->next)
                if (strcmp(e->key, key) == 0) { e->value = value; return; }   /* update */
            Entry *e = malloc(sizeof *e);
            if (!e) exit(1);
            size_t n = strlen(key) + 1;
            e->key = malloc(n);
            if (!e->key) exit(1);
            memcpy(e->key, key, n);
            e->value = value;
            e->next = m->buckets[i];          /* insert at bucket head */
            m->buckets[i] = e;
            m->count++;
        }

        int *map_get(Map *m, const char *key) {
            for (Entry *e = m->buckets[hash(key) % NBUCKETS]; e; e = e->next)
                if (strcmp(e->key, key) == 0) return &e->value;
            return NULL;
        }

        void map_free(Map *m) {
            for (int i = 0; i < NBUCKETS; i++)
                for (Entry *e = m->buckets[i], *next; e; e = next) {
                    next = e->next;
                    free(e->key);
                    free(e);
                }
        }

        int main(void) {
            Map m = {0};
            const char *words[] = {"the", "cat", "sat", "on", "the", "mat", "the", "cat"};
            for (int i = 0; i < 8; i++) {
                int *c = map_get(&m, words[i]);
                if (c) (*c)++; else map_put(&m, words[i], 1);
            }
            const char *probe[] = {"the", "cat", "mat", "dog"};
            for (int i = 0; i < 4; i++) {
                int *c = map_get(&m, probe[i]);
                printf("%s: %d\n", probe[i], c ? *c : 0);
            }
            printf("distinct words: %zu\n", m.count);
            map_free(&m);
            return 0;
        }
    ''', out='''
        the: 3
        cat: 2
        mat: 1
        dog: 0
        distinct words: 5
    ''')
    yield table(
        ["Collision strategy", "How", "Notes"],
        ["Separate chaining", "Each bucket is a linked list", "Simple; degrades gracefully; extra pointers"],
        ["Linear probing", "Try `i + 1`, `i + 2`, … in the array", "Cache-friendly; needs tombstones for delete; clustering"],
        ["Quadratic / double hashing", "Probe with a step that grows or comes from a 2nd hash", "Less clustering"],
    )
    yield note("Keep the *load factor* (`count / capacity`) below ~0.75 by resizing (allocate a bigger bucket array, rehash every entry). Resizing by doubling keeps insertion amortised O(1).")
    yield qa("What makes a good hash function?",
             "It is fast, deterministic, and spreads typical keys uniformly across buckets so that small changes in the key change many output bits. For strings, FNV-1a, djb2 or xxHash/SipHash (the latter resists hash-flooding attacks) are common choices.")


@topic(G, "sorting-searching", "Sorting & Searching", "sort-ascending-numbers")
def _():
    yield lead("The classic algorithms, implemented on plain `int` arrays. Know their complexity, stability and when to reach for the library’s `qsort` / `bsearch` instead.")
    yield table(
        ["Algorithm", "Best", "Average", "Worst", "Space", "Stable?"],
        ["Bubble sort", "O(n)", "O(n²)", "O(n²)", "O(1)", "Yes"],
        ["Selection sort", "O(n²)", "O(n²)", "O(n²)", "O(1)", "No"],
        ["Insertion sort", "O(n)", "O(n²)", "O(n²)", "O(1)", "Yes"],
        ["Merge sort", "O(n log n)", "O(n log n)", "O(n log n)", "O(n)", "Yes"],
        ["Quick sort", "O(n log n)", "O(n log n)", "O(n²)", "O(log n)", "No"],
        ["Heap sort", "O(n log n)", "O(n log n)", "O(n log n)", "O(1)", "No"],
        ["Counting sort", "O(n + k)", "O(n + k)", "O(n + k)", "O(k)", "Yes"],
    )
    yield section("Simple O(n²) sorts", "arrows-sort")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdbool.h>

        void swap(int *a, int *b) { int t = *a; *a = *b; *b = t; }

        void bubble_sort(int *a, int n) {
            for (int i = 0; i < n - 1; i++) {
                bool swapped = false;
                for (int j = 0; j < n - 1 - i; j++)
                    if (a[j] > a[j + 1]) { swap(&a[j], &a[j + 1]); swapped = true; }
                if (!swapped) break;                 /* already sorted: O(n) best case */
            }
        }

        void selection_sort(int *a, int n) {
            for (int i = 0; i < n - 1; i++) {
                int min = i;
                for (int j = i + 1; j < n; j++) if (a[j] < a[min]) min = j;
                swap(&a[i], &a[min]);
            }
        }

        void insertion_sort(int *a, int n) {
            for (int i = 1; i < n; i++) {
                int key = a[i], j = i - 1;
                while (j >= 0 && a[j] > key) { a[j + 1] = a[j]; j--; }
                a[j + 1] = key;
            }
        }

        void print(const int *a, int n) { for (int i = 0; i < n; i++) printf("%d ", a[i]); printf("\n"); }

        int main(void) {
            int a[] = {5, 2, 9, 1, 5, 6}, b[] = {5, 2, 9, 1, 5, 6}, c[] = {5, 2, 9, 1, 5, 6};
            bubble_sort(a, 6); print(a, 6);
            selection_sort(b, 6); print(b, 6);
            insertion_sort(c, 6); print(c, 6);
            return 0;
        }
    ''', out='''
        1 2 5 5 6 9
        1 2 5 5 6 9
        1 2 5 5 6 9
    ''')
    yield section("Merge sort and quick sort", "git-merge")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>

        static void merge(int *a, int *tmp, int lo, int mid, int hi) {
            int i = lo, j = mid, k = lo;
            while (i < mid && j < hi) tmp[k++] = a[i] <= a[j] ? a[i++] : a[j++];   /* <= keeps it stable */
            while (i < mid) tmp[k++] = a[i++];
            while (j < hi)  tmp[k++] = a[j++];
            memcpy(a + lo, tmp + lo, (size_t)(hi - lo) * sizeof *a);
        }

        static void msort(int *a, int *tmp, int lo, int hi) {     /* sorts a[lo, hi) */
            if (hi - lo < 2) return;
            int mid = lo + (hi - lo) / 2;
            msort(a, tmp, lo, mid);
            msort(a, tmp, mid, hi);
            merge(a, tmp, lo, mid, hi);
        }

        void merge_sort(int *a, int n) {
            int *tmp = malloc((size_t)n * sizeof *tmp);
            if (!tmp) return;
            msort(a, tmp, 0, n);
            free(tmp);
        }

        void quick_sort(int *a, int lo, int hi) {                 /* Lomuto partition, a[lo..hi] */
            if (lo >= hi) return;
            int pivot = a[hi], i = lo;
            for (int j = lo; j < hi; j++)
                if (a[j] < pivot) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; }
            int t = a[i]; a[i] = a[hi]; a[hi] = t;                /* pivot to its final place */
            quick_sort(a, lo, i - 1);
            quick_sort(a, i + 1, hi);
        }

        int main(void) {
            int a[] = {38, 27, 43, 3, 9, 82, 10}, b[] = {38, 27, 43, 3, 9, 82, 10};
            merge_sort(a, 7);
            quick_sort(b, 0, 6);
            for (int i = 0; i < 7; i++) printf("%d ", a[i]);
            printf("\n");
            for (int i = 0; i < 7; i++) printf("%d ", b[i]);
            printf("\n");
            return 0;
        }
    ''', out='''
        3 9 10 27 38 43 82
        3 9 10 27 38 43 82
    ''')
    yield section("Binary search", "search")
    yield snippet("c", r'''
        #include <stdio.h>

        int binary_search(const int *a, int n, int key) {
            int lo = 0, hi = n - 1;
            while (lo <= hi) {
                int mid = lo + (hi - lo) / 2;     /* not (lo + hi) / 2: that can overflow */
                if (a[mid] == key) return mid;
                if (a[mid] < key) lo = mid + 1;
                else hi = mid - 1;
            }
            return -1;
        }

        int lower_bound(const int *a, int n, int key) {   /* first index with a[i] >= key */
            int lo = 0, hi = n;
            while (lo < hi) {
                int mid = lo + (hi - lo) / 2;
                if (a[mid] < key) lo = mid + 1; else hi = mid;
            }
            return lo;
        }

        int main(void) {
            int a[] = {2, 5, 8, 8, 8, 13, 21};
            printf("%d %d\n", binary_search(a, 7, 13), binary_search(a, 7, 4));
            printf("first 8 at %d, insert 9 at %d\n", lower_bound(a, 7, 8), lower_bound(a, 7, 9));
            return 0;
        }
    ''', out='''
        5 -1
        first 8 at 2, insert 9 at 5
    ''')
    yield note("In production C, use `qsort` (see Function Pointers) and `bsearch` from `<stdlib.h>`. Write your own when you need stability (merge sort), a specialised key, or an interview asks for it.")
    yield qa("Why is quicksort usually faster than merge sort in practice even though its worst case is O(n²)?",
             "It sorts in place with a tight inner loop and excellent cache locality, and choosing the pivot randomly or by median-of-three makes the O(n²) case vanishingly unlikely. Merge sort needs O(n) extra memory and more data movement. Library sorts (introsort) switch to heap sort if recursion gets too deep, guaranteeing O(n log n).")
    yield qa("What does it mean for a sort to be stable?",
             "Elements with equal keys keep their original relative order. It matters when sorting records by one field after another (e.g. by name, then stably by department). Merge, insertion and bubble sort are stable; quick, heap and selection sort are not. `qsort` is not guaranteed stable.")
