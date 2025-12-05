#ifndef ROBOTS_H
#define ROBOTS_H

#include <time.h>

#define MAX_RULES 128
#define MAX_PATH_LEN 256
#define MAX_DOMAIN_LEN 256

typedef struct {
    char path[MAX_PATH_LEN];
    int disallow;
} RobotsRule;

typedef struct {
    char domain[MAX_DOMAIN_LEN];
    RobotsRule rules[MAX_RULES];
    int rule_count;
    int crawl_delay_seconds;
    time_t last_access;
    int initialized;
} RobotsInfo;

void robots_init(void);
int robots_is_allowed(const char *url);
void robots_respect_crawl_delay(const char *url);

#endif // ROBOTS_H
