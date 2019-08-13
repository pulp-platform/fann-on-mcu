//Copyright (c) 2018 ETH Zurich, Ferdinand von Hagen, Michele Magno, Lukas Cavigelli

#include <stdio.h>
#include "fann.h"
#include "fann_structs.h"
#include "fann_net.h"
#include "fann_conf.h"
#include "rt/rt_api.h"
//#include <pulp.h>
#include "plp_math.h"

#include "fann_utils.h"

#define nPE 8

//#define ACTIVATIONS


//static int cycle_count = 0, instr_count =0;

fann_type *fann_run(fann_type * input)
{
  //int cycle_count = 0, instr_count =0;
  fann_type *neurons, neuron_sum, steepness;
  fann_type neuron_sum_buffer[nPE];
  fann_type *weights;
  unsigned int num_connections, activation_function, layer_it, neuron_it, last_neuron, first_neuron, neuron_it_tmp;
  int nPE_tmp;

  //unsigned int local = 0;


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

  /*
    rt_perf_t perf;
    rt_perf_init(&perf);
    rt_perf_conf(&perf, (1<<RT_PERF_CYCLES) | (1<<RT_PERF_INSTR));
    rt_perf_reset(&perf);
    rt_perf_start(&perf);
    
  */
  plp_copy_i32s_xpulpv2(input, &neuron_values[fann_layers[0].first_neuron], NUM_INPUT);

  /*
    rt_perf_stop(&perf);


    printf("Total cycles: %d\n", rt_perf_read(RT_PERF_CYCLES));
    printf("Instructions: %d\n", rt_perf_read(RT_PERF_INSTR));

  */
    

#else // FIXEDFANN

  printf("float version not supported with pulp yet\n");
  return 0;

#endif // FIXEDFANN

  //int C=0;
  //for all layers
  for(layer_it = 1; layer_it != NUM_LAYERS; ++layer_it) {
    //for all neurons in that layer
    last_neuron = fann_layers[layer_it].last_neuron;
    first_neuron = fann_layers[layer_it].first_neuron;

#ifdef ACTIVATIONS

    activation_function = fann_neurons[first_neuron].activation_function;
    steepness = fann_neurons[first_neuron].activation_steepness;

#ifdef FIXEDFANN

        

    //recompute activation approximation, if different from prov. layer
    if(activation_function != last_activation_function || steepness != last_steepness)
      { // ACTIVATION_FUNCTION CHOOSE
        fann_type inv_steepness = 1/steepness;
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
            v1 = SIGMOID_SYMMETRIC_RESULTS_0 * inv_steepness;
            v2 = SIGMOID_SYMMETRIC_RESULTS_1 * inv_steepness;
            v3 = SIGMOID_SYMMETRIC_RESULTS_2 * inv_steepness;
            v4 = SIGMOID_SYMMETRIC_RESULTS_3 * inv_steepness;
            v5 = SIGMOID_SYMMETRIC_RESULTS_4 * inv_steepness;
            v6 = SIGMOID_SYMMETRIC_RESULTS_5 * inv_steepness;
            break;
          case FANN_SIGMOID_SYMMETRIC:
          case FANN_SIGMOID_SYMMETRIC_STEPWISE:
                      
            r1 = SIGMOID_SYMMETRIC_RESULTS_0;
            r2 = SIGMOID_SYMMETRIC_RESULTS_1;
            r3 = SIGMOID_SYMMETRIC_RESULTS_2;
            r4 = SIGMOID_SYMMETRIC_RESULTS_3;
            r5 = SIGMOID_SYMMETRIC_RESULTS_4;
            r6 = SIGMOID_SYMMETRIC_RESULTS_5;
            v1 = SIGMOID_SYMMETRIC_VALUES_0 * inv_steepness;
            v2 = SIGMOID_SYMMETRIC_VALUES_1 * inv_steepness;
            v3 = SIGMOID_SYMMETRIC_VALUES_2 * inv_steepness;
            v4 = SIGMOID_SYMMETRIC_VALUES_3 * inv_steepness;
            v5 = SIGMOID_SYMMETRIC_VALUES_4 * inv_steepness;
            v6 = SIGMOID_SYMMETRIC_VALUES_5 * inv_steepness;
            break;
          case FANN_THRESHOLD:
            break;
          }
      } // ACTIVATION FUNCTION CHOOSE

    last_steepness = steepness;
    last_activation_function = activation_function;

#endif // FIXEDFANN

#endif // ACTIVATIONS

    ///printf("last_neuron - first neuron %d\n", last_neuron-first_neuron);
    //int C=0;

    // For parallel version we assume that all the neurons in the same layer have the same number of connections, i.e. fully connected networks
    num_connections = fann_neurons[first_neuron].last_connection - fann_neurons[first_neuron].first_connection;
    // Comment: number of cycles are more if we compute it here...if we compute it in the loop of neuron_it then the cycles are fewer...

    if(CONNECTION_RATE >= 1) { // CONNECTION_RATE
        if(network_type == FANN_NETTYPE_SHORTCUT) {
          neurons = neuron_values;
        } else {
          neurons = neuron_values + fann_layers[layer_it - 1].first_neuron;
        } // FANN_NETTYPE_SHORTCUT

        // Append bias (MULTIPLIER)
        neurons[num_connections-1] = MULTIPLIER;
    } else{
        // not supported yet...
    }

    // ATTENTION: +=nPE --> clean up for the remanding neurons -- done
    for(neuron_it = first_neuron; neuron_it < last_neuron-1; neuron_it+=nPE) { // EACH NEURON
      //printf("neuron_it %d, last_neuron-1 %d\n", neuron_it, last_neuron -1);


      //if(num_connections == 0){ // will never happen because neuron_it < last_neuron-1
      //  continue; // fast-forward if no connections
      //}
      //get neuron properties & init vars
            
      weights = fann_weights + fann_neurons[neuron_it].first_connection;
      neuron_sum = 0;

      if(CONNECTION_RATE >= 1) { // CONNECTION_RATE

#ifdef FIXEDFANN

        //if(layer_it==3){  

        nPE_tmp = last_neuron-neuron_it-1;

        if (nPE_tmp > nPE){
          // change the number of processing unit according to the number of neurons (clean up for remaining neurons)

          nPE_tmp = nPE;

        }
	
        //printf("nPE %d\n", nPE_tmp);

        //num_connections = 6000;
        /*
          rt_perf_t perf;
          rt_perf_init(&perf);
          rt_perf_conf(&perf, (1<<RT_PERF_CYCLES) | (1<<RT_PERF_INSTR));
          rt_perf_reset(&perf);
          rt_perf_start(&perf);
        */
        compute_per_layer_parallel((fann_type *)weights, neurons, num_connections, DECIMAL_POINT, nPE_tmp, neuron_sum_buffer); // &neuron_values[neuron_it]??? neuron_sum_buffer

        /*
          for (int k=0; k<nPE_tmp; k++){
          printf("neuron_sum_buffer[%d] = %d\n", k, neuron_sum_buffer[k]);
          }
        */
        //}


        //plp_dot_prod_q32_parallel((fann_type *)weights, neurons, num_connections, DECIMAL_POINT, 8, &neuron_sum);
        //neuron_sum = neuron_sum >> DECIMAL_POINT;

        /*
          rt_perf_stop(&perf);


          //printf("Total cycles: %d\n", rt_perf_read(RT_PERF_CYCLES));
          //printf("Instructions: %d\n", rt_perf_read(RT_PERF_INSTR));
          cycle_count += rt_perf_read(RT_PERF_CYCLES);
          instr_count += rt_perf_read(RT_PERF_INSTR);
        */

#else // FIXEDFANN
        // float version not supported yet for pulp
#endif // FIXEDFANN
      } else { // CONNECTION_RATE
        // Not supported yet...
      } // CONNECTION_RATE
            
      /*
        rt_perf_t perf;
        rt_perf_init(&perf);
        rt_perf_conf(&perf, (1<<RT_PERF_CYCLES) | (1<<RT_PERF_INSTR));
        rt_perf_reset(&perf);
        rt_perf_start(&perf);
      */
      //continue;

      /*
        #ifdef LIN_ACTIVATIONS

        for (neuron_it_tmp=0; neuron_it_tmp<nPE_tmp; neuron_it_tmp++) {

        neuron_values[neuron_it+neuron_it_tmp] = neuron_sum_buffer[neuron_it_tmp];

        }
      */



#ifdef ACTIVATIONS

#ifdef FIXEDFANN

      //local = activation_function;


      for (neuron_it_tmp=0; neuron_it_tmp<nPE_tmp; neuron_it_tmp++) {
        //printf("count %d\n",C++);
              
    
        //printf("count %d\n",C++);
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


        neuron_values[neuron_it+neuron_it_tmp] = neuron_sum;

      }

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

    } // EACH NEURON

 

  }

  //printf("cycle count %d, instr count %d\n", cycle_count/48, instr_count/48);

    
  // return pointer to output values
  return neuron_values + fann_layers[NUM_LAYERS - 1].first_neuron;
}
