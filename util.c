#include <ctype.h>
#include <stdio.h>
#include <string.h>

#include "util.h"

/*
 * Check if the URL is HTTP or HTTPS.
 */
int is_http_url(const char *url) {
    if (!url) {
        return 0;
    }
    return strncmp(url, "http://", 7) == 0 || strncmp(url, "https://", 8) == 0;
}

/*
 * Extract the domain from a URL. Returns 0 on success.
 */
int extract_domain(const char *url, char *out_domain, int out_len) {
    if (!url || !out_domain || out_len <= 0) {
        return -1;
    }
    const char *p = url;
    if (strncmp(p, "http://", 7) == 0) {
        p += 7;
    } else if (strncmp(p, "https://", 8) == 0) {
        p += 8;
    }

    int i = 0;
    while (*p && *p != '/' && *p != ':' && i < out_len - 1) {
        out_domain[i++] = *p++;
    }
    out_domain[i] = '\0';
    return (i > 0) ? 0 : -1;
}

/*
 * Normalize a URL by trimming whitespace and copying to the output buffer.
 */
void normalize_url(const char *url, char *out, int out_len) {
    if (!url || !out || out_len <= 0) {
        return;
    }

    while (*url && isspace((unsigned char)*url)) {
        url++;
    }

    int i = 0;
    while (*url && i < out_len - 1) {
        out[i++] = *url++;
    }
    out[i] = '\0';
}
