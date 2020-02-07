
PULP_APP = test
PULP_APP_FC_SRCS = test.c
PULP_APP_CL_SRCS = cluster.c fann.c

PULP_LDFLAGS += -lplpdsp
PULP_CFLAGS += -I$(IDIR) -O3 -g #-fno-tree-loop-distribute-patterns

include $(PULP_SDK_HOME)/install/rules/pulp_rt.mk

