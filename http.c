#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>

#include "http.h"

static size_t write_cb(char *ptr, size_t size, size_t nmemb, void *userdata) {
    size_t total = size * nmemb;
    HttpResponse *resp = (HttpResponse *)userdata;
    char *new_data = realloc(resp->data, resp->length + total + 1);
    if (!new_data) {
        return 0;
    }
    resp->data = new_data;
    memcpy(resp->data + resp->length, ptr, total);
    resp->length += total;
    resp->data[resp->length] = '\0';
    return total;
}

int http_init(void) {
    CURLcode code = curl_global_init(CURL_GLOBAL_DEFAULT);
    return (code == CURLE_OK) ? 0 : -1;
}

void http_cleanup(void) {
    curl_global_cleanup();
}

int http_get(const char *url, HttpResponse *resp) {
    if (!url || !resp) {
        return -1;
    }
    resp->data = NULL;
    resp->length = 0;

    CURL *curl = curl_easy_init();
    if (!curl) {
        return -1;
    }

    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 10L);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_cb);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, resp);

    CURLcode res = curl_easy_perform(curl);
    if (res != CURLE_OK) {
        fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        free(resp->data);
        resp->data = NULL;
        resp->length = 0;
        curl_easy_cleanup(curl);
        return -1;
    }

    curl_easy_cleanup(curl);
    return 0;
}
