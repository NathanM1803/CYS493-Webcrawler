#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <unistd.h>
#include <time.h>

#include "http.h"
#include "robots.h"
#include "util.h"

#define MAX_DOMAINS 64

static RobotsInfo robots_list[MAX_DOMAINS];
static int robots_count = 0;

static RobotsInfo *find_or_create_info(const char *domain);
static void parse_robots(RobotsInfo *info, const char *content);

void robots_init(void) {
    robots_count = 0;
    for (int i = 0; i < MAX_DOMAINS; i++) {
        robots_list[i].initialized = 0;
        robots_list[i].rule_count = 0;
        robots_list[i].crawl_delay_seconds = 0;
        robots_list[i].last_access = 0;
        robots_list[i].domain[0] = '\0';
    }
}

static RobotsInfo *find_or_create_info(const char *domain) {
    if (!domain) {
        return NULL;
    }
    for (int i = 0; i < robots_count; i++) {
        if (strcmp(robots_list[i].domain, domain) == 0) {
            return &robots_list[i];
        }
    }
    if (robots_count >= MAX_DOMAINS) {
        return NULL;
    }
    RobotsInfo *info = &robots_list[robots_count++];
    strncpy(info->domain, domain, sizeof(info->domain) - 1);
    info->domain[sizeof(info->domain) - 1] = '\0';
    info->rule_count = 0;
    info->crawl_delay_seconds = 0;
    info->last_access = 0;
    info->initialized = 0;
    return info;
}

static void parse_robots(RobotsInfo *info, const char *content) {
    if (!info || !content) {
        return;
    }
    int in_user_agent_star = 0;
    char line[512];
    const char *p = content;

    while (*p) {
        size_t len = 0;
        while (p[len] && p[len] != '\n' && len < sizeof(line) - 1) {
            line[len] = p[len];
            len++;
        }
        line[len] = '\0';
        p += len;
        if (*p == '\n') {
            p++;
        }

        char *trim = line;
        while (*trim == ' ' || *trim == '\t') {
            trim++;
        }
        if (*trim == '#' || *trim == '\0') {
            continue;
        }

        if (strncasecmp(trim, "User-agent:", 11) == 0) {
            char *ua = trim + 11;
            while (*ua == ' ' || *ua == '\t') ua++;
            in_user_agent_star = (strncmp(ua, "*", 1) == 0);
        } else if (strncasecmp(trim, "Disallow:", 9) == 0 && in_user_agent_star) {
            char *path = trim + 9;
            while (*path == ' ' || *path == '\t') path++;
            if (info->rule_count < MAX_RULES && *path != '\0') {
                strncpy(info->rules[info->rule_count].path, path, MAX_PATH_LEN - 1);
                info->rules[info->rule_count].path[MAX_PATH_LEN - 1] = '\0';
                info->rules[info->rule_count].disallow = 1;
                info->rule_count++;
            }
        } else if (strncasecmp(trim, "Crawl-delay:", 12) == 0 && in_user_agent_star) {
            char *val = trim + 12;
            while (*val == ' ' || *val == '\t') val++;
            int delay = atoi(val);
            if (delay > 0) {
                info->crawl_delay_seconds = delay;
            }
        }
    }
}

int robots_is_allowed(const char *url) {
    char domain[MAX_DOMAIN_LEN];
    char path[MAX_PATH_LEN];
    if (extract_domain(url, domain, sizeof(domain)) != 0) {
        return -1;
    }

    const char *p = url;
    if (strncmp(p, "http://", 7) == 0) {
        p += 7;
    } else if (strncmp(p, "https://", 8) == 0) {
        p += 8;
    }
    while (*p && *p != '/') {
        p++;
    }
    if (*p) {
        strncpy(path, p, sizeof(path) - 1);
        path[sizeof(path) - 1] = '\0';
    } else {
        strncpy(path, "/", sizeof(path) - 1);
        path[sizeof(path) - 1] = '\0';
    }

    RobotsInfo *info = find_or_create_info(domain);
    if (!info) {
        return -1;
    }

    if (!info->initialized) {
        char robots_url[512];
        snprintf(robots_url, sizeof(robots_url), "http://%s/robots.txt", domain);
        HttpResponse resp;
        if (http_get(robots_url, &resp) == 0 && resp.data) {
            parse_robots(info, resp.data);
            free(resp.data);
        } else {
            info->rule_count = 0;
            info->crawl_delay_seconds = 0;
            if (resp.data) {
                free(resp.data);
            }
        }
        info->initialized = 1;
    }

    for (int i = 0; i < info->rule_count; i++) {
        RobotsRule *rule = &info->rules[i];
        if (rule->disallow && strncmp(path, rule->path, strlen(rule->path)) == 0) {
            return 0;
        }
    }

    return 1;
}

void robots_respect_crawl_delay(const char *url) {
    char domain[MAX_DOMAIN_LEN];
    if (extract_domain(url, domain, sizeof(domain)) != 0) {
        sleep(1);
        return;
    }

    RobotsInfo *info = find_or_create_info(domain);
    if (!info) {
        sleep(1);
        return;
    }

    int delay = info->crawl_delay_seconds > 0 ? info->crawl_delay_seconds : 1;
    if (info->last_access > 0) {
        time_t now = time(NULL);
        time_t elapsed = now - info->last_access;
        if (elapsed < delay) {
            sleep(delay - elapsed);
        }
    }
    info->last_access = time(NULL);
}
