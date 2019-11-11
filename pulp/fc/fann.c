//Copyright (c) 2018 ETH Zurich, Xiaying Wang, Ferdinand von Hagen, Lukas Cavigelli, Michele Magno

#include <stdio.h>
#include "fann_conf.h"
#include "fann.h"
#include "fann_structs.h"
#include "fann_net.h"

#include "rt/rt_api.h"
#include "plp_math.h"


// The PULP-DSP is not open-sourced yet, so I'm copying the dsp functions here before fann_run.
void plp_copy_i32s_rv32im(
                          int32_t * __restrict__ pSrc,
                          int32_t * __restrict__ pDst,
                          uint32_t blockSize){

  uint32_t blkCnt, tmpBS;             /* Loop counter and temporal blockSize */

#if defined (PLP_MATH_LOOPUNROLL)

  tmpBS = (blockSize>>2);

  for (blkCnt=0; blkCnt<tmpBS; blkCnt++){

    /* Copy and store result in destination buffer */
    *pDst++ = *pSrc++;
    *pDst++ = *pSrc++;
    *pDst++ = *pSrc++;
    *pDst++ = *pSrc++;
  }

  tmpBS = (blockSize%4U);

  for (blkCnt=0; blkCnt<tmpBS; blkCnt++){
    *pDst++ = *pSrc++;
  }

#else

  for (blkCnt=0; blkCnt<blockSize; blkCnt++){
    *pDst++ = *pSrc++;
  }

#endif // PLP_MATH_LOOPUNROLL


}

void plp_dot_prod_q32s_rv32im(
                              const int32_t * __restrict__ pSrcA,
                              const int32_t * __restrict__ pSrcB,
                              uint32_t blockSize,
                              uint32_t deciPoint,
                              int32_t * __restrict__ pRes){
        uint32_t blkCnt;                               /* Loop counter */
        int32_t sum = 0;                          /* Temporary return variable */

#if defined (PLP_MATH_LOOPUNROLL)

        for (blkCnt=0; blkCnt<(blockSize>>2); blkCnt++){
          sum += (*pSrcA++) * (*pSrcB++) >> deciPoint;
          sum += (*pSrcA++) * (*pSrcB++) >> deciPoint;
          sum += (*pSrcA++) * (*pSrcB++) >> deciPoint;
          sum += (*pSrcA++) * (*pSrcB++) >> deciPoint;
        }

        for (blkCnt=0; blkCnt<(blockSize%4U); blkCnt++){
          sum += (*pSrcA++) * (*pSrcB++) >> deciPoint;
        }

#else // PLP_MATH_LOOPUNROLL

        for (blkCnt=0; blkCnt<blockSize; blkCnt++){
          sum += (*pSrcA++) * (*pSrcB++) >> deciPoint;
        }

#endif // PLP_MATH_LOOPUNROLL

        * pRes = sum;

}



fann_type *fann_run(fann_type * input)
{
  fann_type *neurons, neuron_sum, steepness;
  fann_type *weights;
  unsigned int num_connections, activation_function, layer_it, neuron_it, last_neuron, first_neuron;

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

  plp_copy_i32s_rv32im(input, &neuron_values[fann_layers[0].first_neuron], NUM_INPUT);

#else

  printf("float version not supported for pulp yet\n");
  return 0;

#endif

  //for all layers
  for(layer_it = 1; layer_it != NUM_LAYERS; ++layer_it) {
    //for all neurons in that layer
    last_neuron = fann_layers[layer_it].last_neuron -1; // last_neuron -1 because the last neuron is anyways the bias which is counted already in neuron_values with MULTIPLIER (see above)
    first_neuron = fann_layers[layer_it].first_neuron;

#ifdef ACTIVATIONS

    activation_function = fann_neurons[first_neuron].activation_function;
    steepness = fann_neurons[first_neuron].activation_steepness;


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
            v1 = SIGMOID_VALUES_0 / steepness;
            v2 = SIGMOID_VALUES_1 / steepness;
            v3 = SIGMOID_VALUES_2 / steepness;
            v4 = SIGMOID_VALUES_3 / steepness;
            v5 = SIGMOID_VALUES_4 / steepness;
            v6 = SIGMOID_VALUES_5 / steepness;
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

    last_steepness = steepness;
    last_activation_function = activation_function;

#endif // FIXEDFANN

#endif // ACTIVATIONS

    if(CONNECTION_RATE >= 1) { // CONNECTION_RATE
        if(network_type == FANN_NETTYPE_SHORTCUT) {
          neurons = neuron_values;
        } else {
          neurons = neuron_values + fann_layers[layer_it - 1].first_neuron;
        } // FANN_NETTYPE_SHORTCUT

    } else{
        // not supported yet...
    }

    for(neuron_it = first_neuron; neuron_it < last_neuron; ++neuron_it) { // last_neuron -1 because the last neuron is anyways the bias which is counted already in neuron_values with MULTIPLIER (see above)
          
      num_connections = fann_neurons[neuron_it].last_connection - fann_neurons[neuron_it].first_connection;
      if(num_connections == 0){
        continue; // fast-forward if no connections
      }

      //get neuron properties & init vars

      weights = fann_weights + fann_neurons[neuron_it].first_connection;
      neuron_sum = 0;

      if(CONNECTION_RATE >= 1) {

        // Append bias (MULTIPLIER)
        neurons[num_connections-1] = MULTIPLIER;


#ifdef FIXEDFANN

        plp_dot_prod_q32s_rv32im((fann_type *)weights, neurons, num_connections, DECIMAL_POINT, &neuron_sum);

#else
        printf("floating point not supported yet for pulp\n");
        return 0;
#endif
      } else {
        // Not supported yet... (connection rate < 1?)
      }

#ifdef ACTIVATIONS

#ifdef FIXEDFANN
    
            
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
            
      neuron_values[neuron_it] = neuron_sum;
#else // FIXEDFANN
      neuron_sum = fann_mult(steepness, neuron_sum);
      max_sum = 150.0f / steepness;
      if(neuron_sum > max_sum)
        neuron_sum = max_sum;
      else if(neuron_sum < -max_sum)
        neuron_sum = -max_sum;

      fann_activation_switch(activation_function, neuron_sum, neuron_values[neuron_it]);
#endif // FIXEDFANN

#endif // ACTIVATIONS
    }
  }
    
  // return pointer to output values
  return neuron_values + fann_layers[NUM_LAYERS - 1].first_neuron;
}
