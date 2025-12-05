#ifndef UTIL_H
#define UTIL_H

int extract_domain(const char *url, char *out_domain, int out_len);
void normalize_url(const char *url, char *out, int out_len);
int is_http_url(const char *url);

#endif // UTIL_H
