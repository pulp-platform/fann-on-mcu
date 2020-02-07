//Copyright (c) 2018 ETH Zurich, Xiaying Wang, Ferdinand von Hagen, Lukas Cavigelli, Michele Magno

#include <stdio.h>
#include "fann_conf.h"
#include "fann.h"
#include "fann_structs.h"
#include "fann_net.h"

#include "rt/rt_api.h"
#include "plp_math.h"

#include "fann_utils.h"
#define nPE 8

RT_CL_DATA static int buff_index_weights = 0;
RT_CL_DATA static int buff_index_neuron_values = 0;


fann_type *fann_run(fann_type * input)
{
  //int cycle_count = 0, instr_count =0;
  fann_type *neurons, neuron_sum, steepness;
  fann_type neuron_sum_buffer[nPE];
  fann_type *weights; // Address of weights for dot prod
  fann_type *weights_dma_transfer; // Address of weights for transfering next chunk while computing dot prod
  unsigned int num_connections, activation_function, layer_it, neuron_it, last_neuron, first_neuron, neuron_it_tmp, first_connection, num_iter_neuron;
  int nPE_tmp;

  // For dma transfer
  rt_dma_copy_t id_in_weights;
  int datasize = sizeof(fann_type);
  int num_weights;


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

  plp_copy_i32s_xpulpv2(input, neuron_values[buff_index_neuron_values], NUM_INPUT);

#else // FIXEDFANN

  plp_copy_f32s_xpulpv2(input, neuron_values[buff_index_neuron_values], NUM_INPUT);

#endif // FIXEDFANN

  // Initialize the weights address
  weights_dma_transfer = fann_weights;

  //for all layers
  for(layer_it = 1; layer_it != NUM_LAYERS; ++layer_it) {
    //for all neurons in that layer
    last_neuron = fann_layers[layer_it].last_neuron;
    first_neuron = fann_layers[layer_it].first_neuron;

    first_connection = fann_neurons[first_neuron].first_connection;

    // For parallel version we assume that all the neurons in the same layer have the same number of connections, i.e. fully connected networks. Comment: number of cycles are more if we compute it here...if we compute it in the loop of neuron_it then the cycles are fewer...
    num_connections = fann_neurons[first_neuron].last_connection - first_connection;

    num_weights = num_connections * nPE;
    // Comment: fann_neurons[last_neuron].last_connection is equal to fann_neurons[last_neuron].first_connection (it's the bias neuron)

    // Prologue for the loop, we need to fetch one buffer
    rt_dma_memcpy((int)weights_dma_transfer, (int)weights_loc_buff[buff_index_weights], num_weights*datasize, RT_DMA_DIR_EXT2LOC, 0, &id_in_weights);
    buff_index_weights ^= 1;


#ifdef ACTIVATIONS

    activation_function = fann_neurons[first_neuron].activation_function;
    steepness = fann_neurons[first_neuron].activation_steepness;

#ifdef FIXEDFANN

        

    //recompute activation approximation, if different from prov. layer
    if(activation_function != last_activation_function || steepness != last_steepness)
      { // ACTIVATION_FUNCTION CHOOSE
        
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
      } // ACTIVATION FUNCTION CHOOSE

    last_steepness = steepness;
    last_activation_function = activation_function;

#endif // FIXEDFANN

#endif // ACTIVATIONS

    // Append bias (MULTIPLIER)
    neuron_values[buff_index_neuron_values][num_connections-1] = MULTIPLIER;

    num_iter_neuron = last_neuron-1-first_neuron;

    // ATTENTION: +=nPE --> clean up for the remanding neurons -- done
    //for(neuron_it = first_neuron; neuron_it < last_neuron-1; neuron_it+=nPE) { // EACH NEURON
    for(neuron_it = 0; neuron_it < num_iter_neuron; neuron_it+=nPE) { // EACH NEURON
      //printf("neuron_it %d, last_neuron-1 %d\n", neuron_it, last_neuron -1);


      //if(num_connections == 0){ // will never happen because neuron_it < last_neuron-1
      //  continue; // fast-forward if no connections
      //}

      //get neuron properties & init vars
      neuron_sum = 0;

      if(CONNECTION_RATE >= 1) { // CONNECTION_RATE

#ifdef FIXEDFANN

        //nPE_tmp = last_neuron-neuron_it-1;
        nPE_tmp = num_iter_neuron - neuron_it;

        if (nPE_tmp > nPE){
          // change the number of processing unit according to the number of neurons (clean up for remaining neurons)

          nPE_tmp = nPE;

        }

        //weights = fann_weights + fann_neurons[neuron_it+1].first_connection;
        weights_dma_transfer += num_connections * nPE_tmp; // Address of the weights for the next dot prod

        // Wait for previous iteration input transfer. This is supposed to be already finished if processing is long enough
        rt_dma_wait(&id_in_weights);

        // Enqueue the input buffer transfer for the next iteration so that the DMA transfers it while we do computation
        rt_dma_memcpy((int)weights_dma_transfer, (int)weights_loc_buff[buff_index_weights], num_weights*datasize, RT_DMA_DIR_EXT2LOC, 0, &id_in_weights);
        buff_index_weights ^= 1;

        weights = weights_loc_buff[buff_index_weights];

        compute_per_layer_parallel((fann_type *)weights, neuron_values[buff_index_neuron_values], num_connections, DECIMAL_POINT, nPE_tmp, neuron_sum_buffer);

        buff_index_neuron_values ^= 1;

#else // FIXEDFANN

        //nPE_tmp = last_neuron-neuron_it-1;
        nPE_tmp = num_iter_neuron - neuron_it;

        if (nPE_tmp > nPE){
          // change the number of processing unit according to the number of neurons (clean up for remaining neurons)

          nPE_tmp = nPE;

        }

        //weights = fann_weights + fann_neurons[neuron_it+1].first_connection;
        weights_dma_transfer += num_connections * nPE_tmp; // Address of the weights for the next dot prod

        // Wait for previous iteration input transfer. This is supposed to be already finished if processing is long enough
        rt_dma_wait(&id_in_weights);

        // Enqueue the input buffer transfer for the next iteration so that the DMA transfers it while we do computation
        rt_dma_memcpy((int)weights_dma_transfer, (int)weights_loc_buff[buff_index_weights], num_weights*datasize, RT_DMA_DIR_EXT2LOC, 0, &id_in_weights);
        buff_index_weights ^= 1;

        weights = weights_loc_buff[buff_index_weights];

        compute_per_layer_parallel_f32((fann_type *)weights, neuron_values[buff_index_neuron_values], num_connections, nPE_tmp, neuron_sum_buffer);

        buff_index_neuron_values ^= 1;

#endif // FIXEDFANN


      } else { // CONNECTION_RATE
        // Not supported yet...
      } // CONNECTION_RATE


#ifdef ACTIVATIONS

#ifdef FIXEDFANN

      for (neuron_it_tmp=0; neuron_it_tmp<nPE_tmp; neuron_it_tmp++) {

        neuron_sum = neuron_sum_buffer[neuron_it_tmp];

        //apply activation function
        switch (activation_function) { // APPLY CHOSEN ACTIVATION
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
        } // APPLY CHOSEN ACTIVATION


        // if I save the last steepness and activation here it has fewer cycles...

        neuron_values[buff_index_neuron_values][neuron_it+neuron_it_tmp] = neuron_sum;

      }

      // Switch buffer
      buff_index_neuron_values ^= 1;

#else // FIXEDFANN
      for (neuron_it_tmp=0; neuron_it_tmp<nPE_tmp; neuron_it_tmp++) {

        neuron_sum = neuron_sum_buffer[neuron_it_tmp];

        //apply activation function
          neuron_sum = fann_mult(steepness, neuron_sum);
      max_sum = 150.0f / steepness;
      if(neuron_sum > max_sum)
        neuron_sum = max_sum;
      else if(neuron_sum < -max_sum)
        neuron_sum = -max_sum;

      fann_activation_switch(activation_function, neuron_sum, neuron_values[neuron_it]);

        neuron_values[neuron_it+neuron_it_tmp] = neuron_sum;

      }
#endif // FIXEDFANN

#endif // ACTIVATIONS

    } // EACH NEURON

#ifdef FIXEDFANN
    // Wait for previous iteration input transfer. This is supposed to be already finished if processing is long enough
    rt_dma_wait(&id_in_weights);

    // Readjust index
    buff_index_neuron_values ^= 1;
#endif

  }

  rt_dma_wait(&id_in_weights);

  // return pointer to output values
  return neuron_values[buff_index_neuron_values];
}
