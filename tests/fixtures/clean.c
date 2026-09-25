/* Clean program. The engine must report ZERO findings on this file. */
int add(int a, int b) {
    int result;
    result = a + b;
    return result;
}

int main() {
    int values[4];
    int total;

    total = 0;
    values[0] = 1;
    values[1] = 2;
    values[2] = 3;
    values[3] = 4;

    for (int i = 0; i < 4; i = i + 1) {
        total = total + values[i];
    }

    return add(total, 0);
}
