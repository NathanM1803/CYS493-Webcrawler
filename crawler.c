#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "crawler.h"
#include "http.h"
#include "robots.h"
#include "util.h"

#define MAX_VISITED 5000

static char visited[MAX_VISITED][MAX_URL_LENGTH];
static int visited_count = 0;
static const char *find_ci(const char *haystack, const char *needle);

static int has_visited(const char *url) {
    for (int i = 0; i < visited_count; i++) {
        if (strcmp(visited[i], url) == 0) {
            return 1;
        }
    }
    return 0;
}

static void mark_visited(const char *url) {
    if (visited_count < MAX_VISITED) {
        strncpy(visited[visited_count], url, MAX_URL_LENGTH - 1);
        visited[visited_count][MAX_URL_LENGTH - 1] = '\0';
        visited_count++;
    }
}

void queue_init(UrlQueue *q) {
    if (!q) return;
    q->front = q->rear = NULL;
    q->size = 0;
}

int queue_push(UrlQueue *q, const char *url, int depth) {
    if (!q || !url) {
        return -1;
    }
    UrlNode *node = malloc(sizeof(UrlNode));
    if (!node) {
        return -1;
    }
    strncpy(node->url, url, MAX_URL_LENGTH - 1);
    node->url[MAX_URL_LENGTH - 1] = '\0';
    node->depth = depth;
    node->next = NULL;
    if (!q->rear) {
        q->front = q->rear = node;
    } else {
        q->rear->next = node;
        q->rear = node;
    }
    q->size++;
    return 0;
}

int queue_pop(UrlQueue *q, char *out_url, int *out_depth) {
    if (!q || !q->front) {
        return 0;
    }
    UrlNode *node = q->front;
    if (out_url) {
        strncpy(out_url, node->url, MAX_URL_LENGTH);
        out_url[MAX_URL_LENGTH - 1] = '\0';
    }
    if (out_depth) {
        *out_depth = node->depth;
    }
    q->front = node->next;
    if (!q->front) {
        q->rear = NULL;
    }
    free(node);
    q->size--;
    return 1;
}

void queue_free(UrlQueue *q) {
    if (!q) return;
    UrlNode *cur = q->front;
    while (cur) {
        UrlNode *next = cur->next;
        free(cur);
        cur = next;
    }
    q->front = q->rear = NULL;
    q->size = 0;
}

static void save_page_to_file(const char *url, const char *html) {
    FILE *f = fopen("pages.txt", "a");
    if (!f) {
        perror("fopen");
        return;
    }
    fprintf(f, "URL: %s\n", url);
    if (html) {
        size_t len = strlen(html);
        size_t snippet_len = len < 200 ? len : 200;
        fprintf(f, "Content snippet:\n");
        fwrite(html, 1, snippet_len, f);
        fprintf(f, "\n");
    }
    fprintf(f, "\n");
    fclose(f);
}

static void extract_links(const char *base_url, const char *html, UrlQueue *q, int next_depth) {
    (void)base_url;
    if (!html || !q) return;
    const char *p = html;
    while ((p = find_ci(p, "<a")) != NULL) {
        const char *href = find_ci(p, "href=");
        if (!href) {
            p += 2;
            continue;
        }
        href += 5;
        while (*href == ' ' || *href == '\t') href++;
        if (*href == '"') {
            href++;
            const char *end = strchr(href, '"');
            if (end) {
                size_t len = end - href;
                if (len > 0 && len < MAX_URL_LENGTH) {
                    char link[MAX_URL_LENGTH];
                    strncpy(link, href, len);
                    link[len] = '\0';
                    if (strncmp(link, "mailto:", 7) != 0 && strncmp(link, "javascript:", 11) != 0) {
                        char normalized[MAX_URL_LENGTH];
                        normalize_url(link, normalized, sizeof(normalized));
                        if (is_http_url(normalized) && !has_visited(normalized)) {
                            queue_push(q, normalized, next_depth);
                        }
                    }
                }
                p = end;
            } else {
                break;
            }
        } else {
            p = href + 1;
        }
    }
}

static const char *find_ci(const char *haystack, const char *needle) {
    if (!haystack || !needle) {
        return NULL;
    }
    size_t nlen = strlen(needle);
    if (nlen == 0) {
        return haystack;
    }
    for (const char *p = haystack; *p; p++) {
        if (strncasecmp(p, needle, nlen) == 0) {
            return p;
        }
    }
    return NULL;
}

void crawl(const char *start_url, int max_pages, int max_depth) {
    UrlQueue queue;
    queue_init(&queue);
    queue_push(&queue, start_url, 0);

    visited_count = 0;
    int pages_crawled = 0;

    char current_url[MAX_URL_LENGTH];
    int current_depth = 0;

    while (queue_pop(&queue, current_url, &current_depth)) {
        if (pages_crawled >= max_pages || pages_crawled >= MAX_PAGES) {
            break;
        }
        if (has_visited(current_url)) {
            continue;
        }
        mark_visited(current_url);

        if (current_depth > max_depth) {
            continue;
        }

        int allowed = robots_is_allowed(current_url);
        if (allowed <= 0) {
            fprintf(stderr, "Skipping disallowed or error URL: %s\n", current_url);
            continue;
        }

        robots_respect_crawl_delay(current_url);

        HttpResponse resp;
        if (http_get(current_url, &resp) != 0) {
            fprintf(stderr, "Failed to fetch %s\n", current_url);
            continue;
        }

        save_page_to_file(current_url, resp.data);
        pages_crawled++;

        if (current_depth < max_depth) {
            extract_links(current_url, resp.data, &queue, current_depth + 1);
        }

        free(resp.data);
    }

    queue_free(&queue);
}
