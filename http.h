#ifndef HTTP_H
#define HTTP_H

#include <stdlib.h>

typedef struct {
    char *data;
    size_t length;
} HttpResponse;

int http_init(void);
void http_cleanup(void);
int http_get(const char *url, HttpResponse *resp);

#endif // HTTP_H
