/* Unsafe C library calls: gets, strcpy, scanf, system. */
int main() {
    char buffer[64];
    char other[64];
    int n;

    gets(buffer);
    strcpy(other, buffer);
    scanf("%s", buffer);
    system(buffer);

    n = 0;
    return n;
}
