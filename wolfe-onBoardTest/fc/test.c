#include <stdio.h>
#include <stdlib.h>
#include "fann.h"
#include "fann_conf.h"
#include "test_data.h"

#include <rt/rt_api.h>

// for taking measurements on board
#define NUM_REPEAT 1003
#define WARM_CACHE 3

int main(int argc, char *argv[])
{
    printf("starting tests....\n");
    fann_type *calc_out;

    int sum_cycles = 0;
    int sum_instr = 0;


    int corr = 0;
    int i = 0;
#ifdef NUM_REPEAT
    for(i = 0; i < NUM_REPEAT; ++i) {
#else
    for(i = 0; i < NUM_TESTS; ++i) {
#endif
			  // note: the test data has been rescaled offline. For a real application don't forget to scale the input data by MULTIPLIER!
			

  // This tructure will hold the configuration and also the results in the
  // cumulative mode
  rt_perf_t perf;

  // It must be initiliazed at least once, this will set all values in the
  // structure to zero.
  rt_perf_init(&perf);

  // To be compatible with all platforms, we can count only 1 event at the
  // same time (the silicon as only 1 HW counter), but the total number of cyles
  // is reported by a timer, we can activate it at the same time.
//  do_bench_0(&perf, (1<<RT_PERF_CYCLES) | (1<<RT_PERF_INSTR));

  // Activate specified events
  rt_perf_conf(&perf, (1<<RT_PERF_CYCLES) | (1<<RT_PERF_INSTR));
  //rt_perf_conf(&perf, (1<<RT_PERF_IMISS)); //75
  //rt_perf_conf(&perf, (1<<RT_PERF_TCDM_CONT));
  //rt_perf_conf(&perf, (1<<RT_PERF_INSTR));
  //rt_perf_conf(&perf, (1<<RT_PERF_ACTIVE_CYCLES));

  // Reset HW counters now and start and stop counters so that we benchmark
  // only around the printf
  rt_perf_reset(&perf);
  rt_perf_start(&perf);

#ifdef NUM_REPEAT
  calc_out = fann_run(test_data_input);
#else
  calc_out = fann_run(test_data_input + NUM_INPUT * i);
#endif

  rt_perf_stop(&perf);


//  printf("Total cycles: %d\n", rt_perf_read(RT_PERF_CYCLES));
//  printf("Instructions: %d\n", rt_perf_read(RT_PERF_INSTR));
  //printf("imiss stalls: %d\n", rt_perf_read(RT_PERF_IMISS));
  //printf("imiss stalls: %d\n", rt_perf_read(RT_PERF_TCDM_CONT));

// To measure warm cache
  if (i >= WARM_CACHE) {
    sum_cycles += rt_perf_read(RT_PERF_CYCLES);
    sum_instr += rt_perf_read(RT_PERF_INSTR);
  }



#ifndef NUM_REPEAT

        int cla = 0;
	if ((calc_out[0] > calc_out[1]) && (calc_out[0] > calc_out[2])) {
	    cla = 0;
	} else
	if ((calc_out[1] > calc_out[0]) && (calc_out[1] > calc_out[2])) {
	    cla = 1;
	} else {
	    cla = 2;
	}

        if (cla == test_data_output[i]) {
            ++corr;
        }
#endif
        
    }

#ifdef NUM_REPEAT
    //printf("mean cycles over num test is %d, mean instr is %d\n", sum_cycles/NUM_TESTS, sum_instr/NUM_TESTS);
    //printf("#### run on fc\n");
    printf("#### NUM_INPUT_fc %d\n", NUM_INPUT);
    printf("#### NUM_OUTPUT_fc %d\n", NUM_OUTPUT);
    printf("#### mean_cycles_fc %d\n", sum_cycles/(NUM_REPEAT-WARM_CACHE));
    printf("#### mean_instr_fc %d\n", sum_instr/(NUM_REPEAT-WARM_CACHE));

    printf("ending tests....\n");
#else
    printf("#### NUM_INPUT_fc %d\n", NUM_INPUT);
    printf("#### NUM_OUTPUT_fc %d\n", NUM_OUTPUT);
    printf("#### mean_cycles_fc %d\n", sum_cycles/(NUM_TESTS-WARM_CACHE));
    printf("#### mean_instr_fc %d\n", sum_instr/(NUM_TESTS-WARM_CACHE));

    printf("ending tests....\n");
#endif

#ifndef FIXEDFANN
    float accuracy = corr / (float)i * 100;
    //printf("correct %d, accuracy %f\r\n", corr, accuracy);
#else
    //printf("correct: %d out of %d\n", corr, NUM_TESTS);
#endif

    return 0;
    
}
