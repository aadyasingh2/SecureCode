/* 'ptr' is set to null, reassigned only on one branch, then dereferenced. */
int main(int flag) {
    int *ptr;
    int storage;
    int result;

    storage = 7;
    ptr = 0;

    if (flag > 0) {
        ptr = &storage;
    }

    result = *ptr;
    return result;
}
