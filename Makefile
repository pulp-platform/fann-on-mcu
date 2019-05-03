PULPFANN=0

ifeq ($(PULPFANN),1)

PULP_APP = test
PULP_APP_FC_SRCS = test.c fann.c fann_utils.c
#PULP_APP_HOST_SRCS = test.c
PULP_CFLAGS += -O3 -g

include $(PULP_SDK_HOME)/install/rules/pulp_rt.mk

else

CC = gcc
CFLAGS = -O3
TARGETS = test.c fann.c fann_utils.c
APP = test

all:
			$(CC) $(CFLAGS) $(TARGETS) -o $(APP)

run:
			./test

clean:
			rm -f test

endif

