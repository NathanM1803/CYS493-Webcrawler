CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -g
LDFLAGS = -lcurl

OBJS = main.o http.o robots.o crawler.o util.o

all: crawler

crawler: $(OBJS)
	$(CC) $(CFLAGS) -o $@ $(OBJS) $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) crawler
