/* Automatically generated train.c file */
/*
Fast Artificial Neural Network Library (fann)
Copyright (C) 2003-2016 Steffen Nissen (steffen.fann@gmail.com)

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/

#include <stdio.h>

#include "fann.h"

int FANN_API test_callback(struct fann *ann, struct fann_train_data *train,
	unsigned int max_epochs, unsigned int epochs_between_reports, 
	float desired_error, unsigned int epochs)
{
	printf("Epochs     %8d. MSE: %.5f. Desired-MSE: %.5f\n", epochs, fann_get_MSE(ann), desired_error);
	return 0;
}

int main (int argc)
{

	srand(1);
	printf("random number %d\n", rand());

	fann_type *calc_out;
	const unsigned int num_input = 100;
	const unsigned int num_output = 8;

	// num_layers = 1 hidden layer + 1 output layer
	const unsigned int num_layers = 41;
	const unsigned int num_neurons_hidden0 = 4;
	const unsigned int num_neurons_hidden1 = 4;
	const unsigned int num_neurons_hidden2 = 20;
	const unsigned int num_neurons_hidden3 = 20;
	const unsigned int num_neurons_hidden4 = 36;
	const unsigned int num_neurons_hidden5 = 36;
	const unsigned int num_neurons_hidden6 = 52;
	const unsigned int num_neurons_hidden7 = 52;
	const unsigned int num_neurons_hidden8 = 68;
	const unsigned int num_neurons_hidden9 = 68;
	const unsigned int num_neurons_hidden10 = 84;
	const unsigned int num_neurons_hidden11 = 84;
	const unsigned int num_neurons_hidden12 = 100;
	const unsigned int num_neurons_hidden13 = 100;
	const unsigned int num_neurons_hidden14 = 116;
	const unsigned int num_neurons_hidden15 = 116;
	const unsigned int num_neurons_hidden16 = 132;
	const unsigned int num_neurons_hidden17 = 132;
	const unsigned int num_neurons_hidden18 = 148;
	const unsigned int num_neurons_hidden19 = 148;
	const unsigned int num_neurons_hidden20 = 164;
	const unsigned int num_neurons_hidden21 = 164;
	const unsigned int num_neurons_hidden22 = 180;
	const unsigned int num_neurons_hidden23 = 180;
	const unsigned int num_neurons_hidden24 = 196;
	const unsigned int num_neurons_hidden25 = 196;
	const unsigned int num_neurons_hidden26 = 212;
	const unsigned int num_neurons_hidden27 = 212;
	const unsigned int num_neurons_hidden28 = 228;
	const unsigned int num_neurons_hidden29 = 228;
	const unsigned int num_neurons_hidden30 = 244;
	const unsigned int num_neurons_hidden31 = 244;
	const unsigned int num_neurons_hidden32 = 260;
	const unsigned int num_neurons_hidden33 = 260;
	const unsigned int num_neurons_hidden34 = 276;
	const unsigned int num_neurons_hidden35 = 276;
	const unsigned int num_neurons_hidden36 = 292;
	const unsigned int num_neurons_hidden37 = 292;
	const unsigned int num_neurons_hidden38 = 308;
	const float desired_error = (const float) 0;
	const unsigned int max_epochs = 1450;
	const unsigned int epochs_between_reports = 10;
	struct fann *ann;
	struct fann_train_data *data, *test_data;

	unsigned int i = 0;
	unsigned int decimal_point;

	printf("Creating network.\n");
	ann = fann_create_standard(num_layers, num_input, num_neurons_hidden0, num_neurons_hidden1, num_neurons_hidden2, num_neurons_hidden3, num_neurons_hidden4, num_neurons_hidden5, num_neurons_hidden6, num_neurons_hidden7, num_neurons_hidden8, num_neurons_hidden9, num_neurons_hidden10, num_neurons_hidden11, num_neurons_hidden12, num_neurons_hidden13, num_neurons_hidden14, num_neurons_hidden15, num_neurons_hidden16, num_neurons_hidden17, num_neurons_hidden18, num_neurons_hidden19, num_neurons_hidden20, num_neurons_hidden21, num_neurons_hidden22, num_neurons_hidden23, num_neurons_hidden24, num_neurons_hidden25, num_neurons_hidden26, num_neurons_hidden27, num_neurons_hidden28, num_neurons_hidden29, num_neurons_hidden30, num_neurons_hidden31, num_neurons_hidden32, num_neurons_hidden33, num_neurons_hidden34, num_neurons_hidden35, num_neurons_hidden36, num_neurons_hidden37, num_neurons_hidden38, num_output);
	data = fann_read_train_from_file("./generated_data/perftest.train");

	fann_set_activation_steepness_hidden(ann, 1);
	fann_set_activation_steepness_output(ann, 1);

	fann_set_activation_function_hidden(ann, FANN_LINEAR);
	fann_set_activation_function_output(ann, FANN_LINEAR);

	fann_set_train_stop_function(ann, FANN_STOPFUNC_BIT); //FANN_STOPFUNC_MSE
	fann_set_bit_fail_limit(ann, 0.01f);

	fann_set_training_algorithm(ann, FANN_TRAIN_RPROP); // FANN_TRAIN_INCREMENTAL

	fann_init_weights(ann, data);
	//fann_randomize_weights(ann, -0.1, 0.1);
	
	printf("Training network.\n");
	fann_train_on_data(ann, data, max_epochs, epochs_between_reports, desired_error);

	printf("perftesting network. %f\n", fann_test_data(ann, data));

	int corr =0;
	for(i = 0; i < fann_length_train_data(data); i++)
	{
		calc_out = fann_run(ann, data->input[i]);
//		printf("lfp test (%f,%f) -> %f, should be %f, difference=%f\n",
//			   data->input[i][0], data->input[i][1], calc_out[0], data->output[i][0],
//			   fann_abs(calc_out[0] - data->output[i][0]));

	int cla = 0, true_cla = 0;
	if ((calc_out[0] > calc_out[1]) && (calc_out[0] > calc_out[2])) {
	    cla = 0;
	} else
	if ((calc_out[1] > calc_out[0]) && (calc_out[1] > calc_out[2])) {
	    cla = 1;
	} else {
	    cla = 2;
	}

	if ((data->output[i][0] > data->output[i][1]) && (data->output[i][0] > data->output[i][2])) {
	    true_cla = 0;
	} else
	if ((data->output[i][1] > data->output[i][0]) && (data->output[i][1] > data->output[i][2])) {
	    true_cla = 1;
	} else {
	    true_cla = 2;
	}

//		printf("predicted class %d, true class %d\n", cla, true_cla);

	if (cla == true_cla) {
	    ++corr;
	}


	}

	printf("correctly classified training data: %d\n", corr);

	printf("Saving network.\n");

	fann_save(ann, "perftest_float.net");

	decimal_point = fann_save_to_fixed(ann, "perftest_fixed.net");
	test_data = fann_read_train_from_file("./generated_data/perftest.test");
	fann_save_train_to_fixed(test_data, "perftest_fixed.data", decimal_point);

	printf("Cleaning up.\n");
	fann_destroy_train(data);
	fann_destroy_train(test_data);
	fann_destroy(ann);

	return 0;

}