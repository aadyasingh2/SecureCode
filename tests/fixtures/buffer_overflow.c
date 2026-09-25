/* A constant subscript past the end, and a provable strcpy overflow. */
int main() {
    int numbers[3];
    char small[8];
    int value;

    numbers[0] = 10;
    numbers[5] = 20;

    strcpy(small, "this is much longer than eight bytes");

    value = numbers[0];
    return value;
}
