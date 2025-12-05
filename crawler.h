#ifndef CRAWLER_H
#define CRAWLER_H

#define MAX_URL_LENGTH 1024
#define MAX_PAGES 1000

typedef struct UrlNode {
    char url[MAX_URL_LENGTH];
    int depth;
    struct UrlNode *next;
} UrlNode;

typedef struct {
    UrlNode *front;
    UrlNode *rear;
    int size;
} UrlQueue;

void queue_init(UrlQueue *q);
int queue_push(UrlQueue *q, const char *url, int depth);
int queue_pop(UrlQueue *q, char *out_url, int *out_depth);
void queue_free(UrlQueue *q);

void crawl(const char *start_url, int max_pages, int max_depth);

#endif // CRAWLER_H
