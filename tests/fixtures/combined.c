/* Demo file: six vulnerability categories in one program. */
char *admin_password = "hunter2";

int handle_request(int flag) {
    char buffer[16];
    int length;
    int *record;

    record = 0;

    if (flag > 0) {
        length = flag;
    }

    gets(buffer);
    strcpy(buffer, "a string that will not fit in sixteen");

    length = length + 1;
    length = *record;

    return length;

    length = 0;
}
