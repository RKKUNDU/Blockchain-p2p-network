#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <string.h>
#include <stdlib.h>

#define MAX_LEN 1024
#define MAX_TOKENS 64

char** split(char*, char*);
int is_delim(char, char*);
void run(char *ip,char* port);

int main(int argc, char** argv) {
	FILE* fp = fopen("config.csv", "rw");
    char* buffer = (char*) malloc(MAX_LEN * sizeof(char));
	size_t t;
	int len;
	int count = 0;
	char** lines = (char**) malloc(MAX_TOKENS * sizeof(char*));
	while ((len = getline(&buffer, &t, fp)) > 0) {
		if (buffer[len - 1] == '\n')
			buffer[len - 1] = '\0';
		char* line = (char*) malloc(MAX_LEN * sizeof(char));
		strcpy(line, buffer);
		lines[count++] = line;
	}
	free(buffer);



    for (int i = 0; i < count; ++i) {
        char** tokens = split(lines[i], ",");

        int id = fork();

        if (id == 0) {
	    run(tokens[0], tokens[1]);
        }
    }
}

void run(char *ip,char* port) {
    char* args[5] = {"python3", "seed.py", ip, port, NULL};
    execvp(args[0], args);
}

char** split (char* str, char* delims) {
	char** tokens = (char**) malloc (MAX_TOKENS * sizeof(char*));
	char* token = (char*) malloc(MAX_LEN * sizeof(char));
	int len = (int) strlen(str), idx = 0, t_no = 0;

	if (len == 0) {
		tokens[0] = NULL;
		free(token);
		return tokens;
	}

	// Break string
	for (int i = 0; i <= len; ++i) {
		char c = str[i];

		// if (i > 0 && is_delim(str[i - 1], delims) && is_delim(c, delims)) continue;

		if (is_delim(c, delims) || c == '\0') {
			token[idx] = '\0';
			tokens[t_no++] = token;
			idx = 0;
			token = (char*) malloc(MAX_LEN * sizeof(char));
		} else {
			token[idx++] = c;
		}
	}

	tokens[t_no] = NULL;
	free(token);
	return tokens;
}

int is_delim(char c, char* delims) {
	for (int i = 0; i < strlen(delims); ++i) {
		if (c == delims[i])
			return 1;
	}
	return 0;
}
