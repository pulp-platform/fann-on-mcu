#include <stdio.h>
#include <stdlib.h>
#include "fann.h"
#include "fann_conf.h"
#include "test_data.h"

int main(int argc, char *argv[])
{
    printf("starting tests....\n");
    fann_type *calc_out;

    int corr = 0;
    int i = 0;
    for(i = 0; i < NUM_TESTS; ++i) {
			  // note: the test data has been rescaled offline. For a real application don't forget to scale the input data by MULTIPLIER!
			
        calc_out = fann_run(test_data_input + NUM_INPUT * i);


        int cla = 0;
        if (calc_out[0] > calc_out[1]) {
            cla = 0;
        } else {
            cla = 1;
        }

        if (cla == test_data_output[i]) {
            ++corr;
        }
        
    }
#ifndef PULPFANN
    float accuracy = corr / (float)i * 100;
    printf("correct %d, accuracy %f\r\n", corr, accuracy);
#else
    printf("correct: %d out of %d\n", corr, NUM_TESTS);
#endif
    
}
