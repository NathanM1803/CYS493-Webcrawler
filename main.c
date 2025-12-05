#include <stdio.h>
#include <stdlib.h>

#include "crawler.h"
#include "http.h"
#include "robots.h"

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <start_url> [max_pages] [max_depth]\n", argv[0]);
        return 1;
    }

    const char *start_url = argv[1];
    int max_pages = (argc > 2) ? atoi(argv[2]) : 100;
    int max_depth = (argc > 3) ? atoi(argv[3]) : 3;

    if (http_init() != 0) {
        fprintf(stderr, "Failed to initialize HTTP subsystem\n");
        return 1;
    }

    robots_init();

    crawl(start_url, max_pages, max_depth);

    http_cleanup();
    return 0;
}
