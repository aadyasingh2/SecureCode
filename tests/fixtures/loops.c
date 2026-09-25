/* Nested loops with back-edges. Exercises fixed-point termination in the
   data-flow solver. No findings expected. */
int sum_matrix(int rows, int cols) {
    int total;
    int j;

    total = 0;

    for (int i = 0; i < rows; i = i + 1) {
        j = 0;
        while (j < cols) {
            total = total + j;
            j = j + 1;
        }
    }

    return total;
}
