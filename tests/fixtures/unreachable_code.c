/* A statement after an unconditional return can never execute. */
int classify(int value) {
    int result;

    if (value > 0) {
        result = 1;
        return result;
    }

    result = 0;
    return result;

    result = 99;
}
