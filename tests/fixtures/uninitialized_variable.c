/* 'total' is assigned only inside the if, then read after the merge.
   The symbol table's is_initialized flag says True; the data-flow
   analysis correctly says it is not assigned on every path. */
int compute(int flag) {
    int total;
    int result;

    if (flag > 0) {
        total = flag * 2;
    }

    result = total + 1;
    return result;
}
