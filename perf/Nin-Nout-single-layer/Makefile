GCC=gcc
CFLAGS=-I ~/fann/src/include
LDFLAGS=-L ~/fann/src/

TARGETS = perftest_train perftest_test perftest_test_fixed
DEBUG_TARGETS = perftest_debug

all: $(TARGETS)

%: %.c Makefile
	$(GCC) $(CFLAGS) $(LDFLAGS) -O3 $< -o $@ -lfann -lm

%_fixed: %.c Makefile
	$(GCC) $(CFLAGS) $(LDFLAGS) -O3 -DFIXEDFANN $< -o $@ -lfixedfann -lm

clean:
	rm -f $(TARGETS) $(DEBUG_TARGETS) perftest_fixed.data *.net *~ *.obj *.exe *.tds noscale.txt withscale.txt scale_test_results.txt

onlytrain: perftest_train
	@echo
	@echo Training network
	./perftest_train 708 132
