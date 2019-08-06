PULPFANN=1
GAPFANN=0

ifeq ($(PULPFANN),1)

IDIR=/home/xiaywang/pulp/PULP-DSP/include

PULP_APP = test
PULP_APP_FC_SRCS = test.c fann.c fann_utils.c
#PULP_APP_HOST_SRCS = test.c

#PULP_CFLAGS += -O3 -g

PULP_LDFLAGS += -lplpdsp
PULP_CFLAGS += -I$(IDIR) -O3 -g


ifeq ($(GAPFANN),1)
include $(GAP_SDK_HOME)/tools/rules/pulp_rules.mk
else
include $(PULP_SDK_HOME)/install/rules/pulp_rt.mk
endif

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

