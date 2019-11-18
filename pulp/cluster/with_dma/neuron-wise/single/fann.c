/*

  FANN-on-MCU

  Copyright (c) 2018 ETH Zurich, Xiaying Wang, Ferdinand von Hagen, Lukas Cavigelli, Michele Magno

  This library is free software; you can redistribute it and/or

  modify it under the terms of the GNU Lesser General Public

  License as published by the Free Software Foundation; either

  version 2.1 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,

  but WITHOUT ANY WARRANTY; without even the implied warranty of

  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU

  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public

  License along with this library; if not, write to the Free Software

  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

*/

#include <stdio.h>
#include "fann_conf.h"
#include "fann.h"
#include "fann_structs.h"
#include "fann_net.h"

#include "rt/rt_api.h"
#include "plp_math.h"

RT_CL_DATA static int buff_index_weights = 0;
RT_CL_DATA static int buff_index_neuron_values = 0;


// The PULP-DSP is not open-sourced yet, so I'm copying the dsp functions here before fann_run.
void plp_copy_i32s_xpulpv2(
                           int32_t * __restrict__ pSrc,
                           int32_t * __restrict__ pDst,
                           uint32_t blockSize){

  uint32_t blkCnt, tmpBS;                     /* Loop counter, temporal BlockSize */


#if defined (PLP_MATH_LOOPUNROLL)

  tmpBS = (blockSize>>1);

  for (blkCnt=0; blkCnt<tmpBS; blkCnt++){

    /* Copy and store result in destination buffer */
    *pDst++ = *pSrc++;
    *pDst++ = *pSrc++;

  }

  tmpBS = (blockSize%2U);

  for (blkCnt=0; blkCnt<tmpBS; blkCnt++){
    *pDst++ = *pSrc++;
  }

#else

  for (blkCnt=0; blkCnt<blockSize; blkCnt++){
    *pDst++ = *pSrc++;
  }

#endif // PLP_MATH_LOOPUNROLL


}


void plp_dot_prod_q32s_xpulpv2(
                               const int32_t * __restrict__ pSrcA,
                               const int32_t * __restrict__ pSrcB,
                               uint32_t blockSize,
                               uint32_t deciPoint,
                               int32_t * __restrict__ pRes){
  uint32_t blkCnt, tmpBS;                   /* Loop counter, temporal BlockSize */
        int32_t sum = 0; //, sum1 =0;                          /* Temporary return variable */

#if defined(PLP_MATH_LOOPUNROLL)

        tmpBS = (blockSize>>1);

        for (blkCnt=0; blkCnt<tmpBS; blkCnt++){

	sum += (*pSrcA++) * (*pSrcB++) >> deciPoint;
	sum += (*pSrcA++) * (*pSrcB++) >> deciPoint;

        }

        for (blkCnt=0; blkCnt<(blockSize%2U); blkCnt++){
          sum += (*pSrcA++) * (*pSrcB++) >> deciPoint;
        }

#else // PLP_MATH_LOOPUNROLL

        for (blkCnt=0; blkCnt<blockSize; blkCnt++){
          sum += (*pSrcA++) * (*pSrcB++) >> deciPoint;
        }

#endif // PLP_MATH_LOOPUNROLL

        * pRes = sum; // + sum1;

}



fann_type *fann_run(fann_type * input)
{
  fann_type *neurons, neuron_sum, steepness;
  fann_type *weights;
  unsigned int num_connections, activation_function, layer_it, neuron_it, last_neuron, first_neuron, first_connection;

  // For dma transfer
  rt_dma_copy_t id_in_weights;
  int datasize = sizeof(fann_type);

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

  //plp_fill_i32s_xpulpv2(MULTIPLIER, neuron_values, NUM_NEURONS);
  // Comment: not necessary, it's appended later, see below: append bias

  plp_copy_i32s_xpulpv2(input, neuron_values[buff_index_neuron_values], NUM_INPUT);

#else

  printf("float version not supported for pulp yet\n");
  return 0;

#endif

  // Initialize the weights address
  weights = fann_weights;

  //for all layers
  for(layer_it = 1; layer_it != NUM_LAYERS; ++layer_it) {
    //for all neurons in that layer
    last_neuron = fann_layers[layer_it].last_neuron -1; // last_neuron -1 because the last neuron is anyways the bias which is counted already in neuron_values with MULTIPLIER (see above)
    first_neuron = fann_layers[layer_it].first_neuron;
    first_connection = fann_neurons[first_neuron].first_connection;

    num_connections = fann_neurons[first_neuron].last_connection - first_connection;
    // We assume that all the neurons in the same layer have the same number of connections, i.e. fully connected networks.

    // Transfer the weights of the first neuron of the layer
    // weights = fann_weights + first_connection;

    // Prologue for the loop, we need to fetch one buffer
    rt_dma_memcpy((int)weights, (int)weights_loc_buff[buff_index_weights], num_connections*datasize, RT_DMA_DIR_EXT2LOC, 0, &id_in_weights);
    buff_index_weights ^= 1;

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

    // Append bias (MULTIPLIER)
    neuron_values[buff_index_neuron_values][num_connections-1] = MULTIPLIER;

    for(neuron_it = 0; neuron_it < last_neuron-first_neuron; ++neuron_it) { // last_neuron -1 because the last neuron is anyways the bias which is counted already in neuron_values with MULTIPLIER (see above)

      // With dma transfers we also assume that all the neurons in the same layer have the same number of connections, i.e. fully-connected layers
      //num_connections = fann_neurons[neuron_it].last_connection - fann_neurons[neuron_it].first_connection;
      //if(num_connections == 0){
      //  continue; // fast-forward if no connections
      //}

      

      //get neuron properties & init vars
       neuron_sum = 0;

      // DONE append bias to neuron_values
      if(CONNECTION_RATE >= 1) {


#ifdef FIXEDFANN

      //weights = fann_weights + fann_neurons[neuron_it+1].first_connection;
      weights += num_connections;

      // Wait for previous iteration input transfer. This is supposed to be already finished if processing is long enough
      rt_dma_wait(&id_in_weights);

      // Enqueue the input buffer transfer for the next iteration so that the DMA transfers it while we do computation
      rt_dma_memcpy((int)weights, (int)weights_loc_buff[buff_index_weights], num_connections*datasize, RT_DMA_DIR_EXT2LOC, 0, &id_in_weights);
      buff_index_weights ^= 1;

        plp_dot_prod_q32s_xpulpv2((fann_type *)weights_loc_buff[buff_index_weights], neuron_values[buff_index_neuron_values], num_connections, DECIMAL_POINT, &neuron_sum);

        buff_index_neuron_values ^= 1;

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
      
      neuron_values[buff_index_neuron_values][neuron_it] = neuron_sum;
      buff_index_neuron_values ^= 1;

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

#ifdef FIXEDFANN

    // Wait for previous iteration input transfer. This is supposed to be already finished if processing is long enough
    rt_dma_wait(&id_in_weights);

    // Readjust index
    buff_index_neuron_values ^= 1;

#endif
    
  }
    
  // return pointer to output values
  return neuron_values[buff_index_neuron_values];
}
