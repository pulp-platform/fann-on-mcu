//Copyright (c) 2018 ETH Zurich, Ferdinand von Hagen, Michele Magno, Lukas Cavigelli

#include <stdio.h>
#include "fann_conf.h"
#include "fann.h"
#include "fann_structs.h"
#include "fann_net.h"
#include <arm_math.h>

void arm_dot_prod_fixed32_accum32(q31_t * pSrcA, q31_t * pSrcB, uint32_t blockSize, q31_t * result) {
	
  q31_t sum = 0;
  uint32_t blkCnt;

#ifndef ARM_MATH_CM0_FAMILY

	// 4x loop unrolling: 
  q31_t inA1, inA2, inA3, inA4;
  q31_t inB1, inB2, inB3, inB4;

  blkCnt = blockSize >> 2u;
  while(blkCnt > 0u)
  {
    inA1 = *pSrcA++; inA2 = *pSrcA++; inA3 = *pSrcA++; inA4 = *pSrcA++;
    inB1 = *pSrcB++; inB2 = *pSrcB++; inB3 = *pSrcB++; inB4 = *pSrcB++;

    sum += ((q31_t) inA1 * inB1) >> DECIMAL_POINT;
    sum += ((q31_t) inA2 * inB2) >> DECIMAL_POINT;
    sum += ((q31_t) inA3 * inB3) >> DECIMAL_POINT;
    sum += ((q31_t) inA4 * inB4) >> DECIMAL_POINT;
		
//    sum += ((q31_t) inA1 * inB1);
//    sum += ((q31_t) inA2 * inB2);
//    sum += ((q31_t) inA3 * inB3);
//    sum += ((q31_t) inA4 * inB4);
//		sum = sum >> DECIMAL_POINT;

    blkCnt--;
  }

  //set block counter to remaining number of iterations
  blkCnt = blockSize % 0x4u;
#else
	// for the Cortex-M0, we should not do loop unrolling, and
	// thus perform all iterations individually
  blkCnt = blockSize;
#endif 

  while(blkCnt > 0u) {
    sum += ((q31_t) (*pSrcA++) * (*pSrcB++)) >> DECIMAL_POINT;
    blkCnt--;
  }
  *result = sum;
}

fann_type neuron_values[NUM_NEURONS];

fann_type *fann_run(fann_type * input)
{
    fann_type *neurons, neuron_sum, steepness;
		const fann_type *weights;
    unsigned int num_connections, activation_function, layer_it, neuron_it, last_neuron;

#ifdef FIXEDFANN
    /* values used for the stepwise linear sigmoid function */
    fann_type r1 = 0, r2 = 0, r3 = 0, r4 = 0, r5 = 0, r6 = 0;
    fann_type v1 = 0, v2 = 0, v3 = 0, v4 = 0, v5 = 0, v6 = 0;

    fann_type last_steepness = 0;
    unsigned int last_activation_function = 0;
#else
    fann_type max_sum = 0;
#endif

#ifdef FIXEDFANN
    arm_fill_q31(MULTIPLIER, neuron_values, NUM_NEURONS); // setting the bias neuron values
    arm_copy_q31(input, &neuron_values[fann_layers[0].first_neuron], NUM_INPUT); // copy input data
#else
    arm_fill_f32(1.0f, neuron_values, NUM_NEURONS);
    arm_copy_f32(input, &neuron_values[fann_layers[0].first_neuron], NUM_INPUT);
#endif

		//for all layers
    for(layer_it = 1; layer_it != NUM_LAYERS; ++layer_it) {
				//for all neurons in that layer
        last_neuron = fann_layers[layer_it].last_neuron;
        for(neuron_it = fann_layers[layer_it].first_neuron; neuron_it != last_neuron; ++neuron_it) {
					
            num_connections = fann_neurons[neuron_it].last_connection - fann_neurons[neuron_it].first_connection;
            if(num_connections == 0){
                continue; // fast-forward if no connections
            }

						//get neuron properties & init vars
            activation_function = fann_neurons[neuron_it].activation_function;
            steepness = fann_neurons[neuron_it].activation_steepness;
            weights = fann_weights + fann_neurons[neuron_it].first_connection;
            neuron_sum = 0;

            if(CONNECTION_RATE >= 1) {
                if(network_type == FANN_NETTYPE_SHORTCUT) {
                    neurons = neuron_values;
                } else {
                    neurons = neuron_values + fann_layers[layer_it - 1].first_neuron;
                }

#ifdef FIXEDFANN
                arm_dot_prod_fixed32_accum32((fann_type *)weights, neurons, num_connections, &neuron_sum);
#else
                arm_dot_prod_f32((fann_type *)weights, neurons, num_connections, &neuron_sum);
#endif
            } else {
                // Not supported yet...
						}
#ifdef FIXEDFANN
						//recompute activation approximation, if different from prov. layer
            if(activation_function != last_activation_function || steepness != last_steepness)
            {
                switch (activation_function)
                {
                    case FANN_SIGMOID:
                    case FANN_SIGMOID_STEPWISE:
                        r1 = SIGMOID_RESULTS_0;
                        r2 = SIGMOID_RESULTS_1;
                        r3 = SIGMOID_RESULTS_2;
                        r4 = SIGMOID_RESULTS_3;
                        r5 = SIGMOID_RESULTS_4;
                        r6 = SIGMOID_RESULTS_5;
                        v1 = SIGMOID_SYMMETRIC_RESULTS_0 / steepness;
                        v2 = SIGMOID_SYMMETRIC_RESULTS_1 / steepness;
                        v3 = SIGMOID_SYMMETRIC_RESULTS_2 / steepness;
                        v4 = SIGMOID_SYMMETRIC_RESULTS_3 / steepness;
                        v5 = SIGMOID_SYMMETRIC_RESULTS_4 / steepness;
                        v6 = SIGMOID_SYMMETRIC_RESULTS_5 / steepness;
                        break;
                    case FANN_SIGMOID_SYMMETRIC:
                    case FANN_SIGMOID_SYMMETRIC_STEPWISE:
                        r1 = SIGMOID_SYMMETRIC_RESULTS_0;
                        r2 = SIGMOID_SYMMETRIC_RESULTS_1;
                        r3 = SIGMOID_SYMMETRIC_RESULTS_2;
                        r4 = SIGMOID_SYMMETRIC_RESULTS_3;
                        r5 = SIGMOID_SYMMETRIC_RESULTS_4;
                        r6 = SIGMOID_SYMMETRIC_RESULTS_5;
                        v1 = SIGMOID_SYMMETRIC_VALUES_0 / steepness;
                        v2 = SIGMOID_SYMMETRIC_VALUES_1 / steepness;
                        v3 = SIGMOID_SYMMETRIC_VALUES_2 / steepness;
                        v4 = SIGMOID_SYMMETRIC_VALUES_3 / steepness;
                        v5 = SIGMOID_SYMMETRIC_VALUES_4 / steepness;
                        v6 = SIGMOID_SYMMETRIC_VALUES_5 / steepness;
                        break;
                    case FANN_THRESHOLD:
                        break;
                }
            }
						
						//apply activation function
            switch (activation_function) {
                case FANN_SIGMOID:
                case FANN_SIGMOID_STEPWISE:
                    neuron_sum =
                        (fann_type) fann_stepwise(v1, v2, v3, v4, v5, v6, r1, r2, r3, r4, r5, r6, 0,
                                                  MULTIPLIER, neuron_sum);
                    break;
                case FANN_SIGMOID_SYMMETRIC:
                case FANN_SIGMOID_SYMMETRIC_STEPWISE:
                    neuron_sum =
                        (fann_type) fann_stepwise(v1, v2, v3, v4, v5, v6, r1, r2, r3, r4, r5, r6,
                                                  -MULTIPLIER, MULTIPLIER, neuron_sum);
                    break;
                case FANN_THRESHOLD:
                    neuron_sum = (fann_type) ((neuron_sum < 0) ? 0 : MULTIPLIER);
                    break;
                case FANN_THRESHOLD_SYMMETRIC:
                    neuron_sum = (fann_type) ((neuron_sum < 0) ? -MULTIPLIER : MULTIPLIER);
                    break;
                case FANN_LINEAR:
                    neuron_sum = neuron_sum;
                    break;
                case FANN_LINEAR_PIECE:
                    neuron_sum = (fann_type)((neuron_sum < 0) ? 0 : (neuron_sum > MULTIPLIER) ? MULTIPLIER : neuron_sum);
                    break;
                case FANN_LINEAR_PIECE_SYMMETRIC:
                    neuron_sum = (fann_type)((neuron_sum < -MULTIPLIER) ? -MULTIPLIER : (neuron_sum > MULTIPLIER) ? MULTIPLIER : neuron_sum);
                    break;
                case FANN_ELLIOT:
                case FANN_ELLIOT_SYMMETRIC:
                case FANN_GAUSSIAN:
                case FANN_GAUSSIAN_SYMMETRIC:
                case FANN_GAUSSIAN_STEPWISE:
                case FANN_SIN_SYMMETRIC:
                case FANN_COS_SYMMETRIC:
                    while(1) {} // not supported...
                    break;
            }
            last_steepness = steepness;
            last_activation_function = activation_function;
            neuron_values[neuron_it] = neuron_sum;
#else
            neuron_sum = fann_mult(steepness, neuron_sum);
            max_sum = 150.0f / steepness;
            if(neuron_sum > max_sum)
                neuron_sum = max_sum;
            else if(neuron_sum < -max_sum)
                neuron_sum = -max_sum;

            fann_activation_switch(activation_function, neuron_sum, neuron_values[neuron_it]);
#endif
        }
    }
		
		// return pointer to output values
    return neuron_values + fann_layers[NUM_LAYERS - 1].first_neuron;
}
