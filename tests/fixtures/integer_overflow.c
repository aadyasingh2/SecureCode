/* Constant overflow, char truncation, and an unchecked allocation product. */
int main(int count) {
    int overflowed = 2147483647 + 1;
    char truncated = 300;
    int *block;
    int ok;

    block = malloc(count * 4);
    ok = 2 * 3;

    return ok;
}
