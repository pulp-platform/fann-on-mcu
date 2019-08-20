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

int main()
{
	fann_type *calc_out;
	unsigned int i;
	int ret = 0;

	struct fann *ann;
	struct fann_train_data *data;

	printf("Creating network.\n");

#ifdef FIXEDFANN
	ann = fann_create_from_file("perftest_fixed.net");
#else
	ann = fann_create_from_file("perftest_float.net");
#endif

	if(!ann)
	{
		printf("Error creating ann --- ABORTING.\n");
		return -1;
	}

	fann_print_connections(ann);
	fann_print_parameters(ann);

	printf("Testing network.\n");

#ifdef FIXEDFANN
	printf("Reading from fixed data\n");
	data = fann_read_train_from_file("perftest_fixed.data");
#else
	printf("Reading from float data\n");
	data = fann_read_train_from_file("./generated_data/perftest.test");
#endif

	int corr = 0;
	for(i = 0; i < fann_length_train_data(data); i++)
	{
		fann_reset_MSE(ann);
		calc_out = fann_run(ann, data->input[i]); //, data->output[i]);
#ifdef FIXEDFANN
//		printf("calc_out %d, %d, %d\n", calc_out[0], calc_out[1], calc_out[2]);
#else
//		printf("calc_out %f, %f, %f\n", calc_out[0], calc_out[1], calc_out[2]);
#endif

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


#ifdef FIXEDFANN
		//printf("lfp test (%d, %d) -> %d, should be %d, difference=%f\n",
		//	   data->input[i][0], data->input[i][1], calc_out[0], data->output[i][0],
		//	   (float) fann_abs(calc_out[0] - data->output[i][0]) / fann_get_multiplier(ann));
		//printf("true output = %d %d %d\n", data->output[i][0], data->output[i][1], data->output[i][2]);

/*
		if((float) fann_abs(calc_out[0] - data->output[i][0]) / fann_get_multiplier(ann) > 0.2)
		{
			printf("Test failed\n");
			ret = -1;
		}
*/
#else
/*
		printf("lfp test (%f, %f) -> %f, should be %f, difference=%f\n",
			   data->input[i][0], data->input[i][1], calc_out[0], data->output[i][0],
			   (float) fann_abs(calc_out[0] - data->output[i][0]));
*/
		//printf("true output = %f %f %f\n", data->output[i][0], data->output[i][1], data->output[i][2]);
#endif
	}

	printf("correctly classified are %d\n", corr);

	printf("Cleaning up.\n");
	fann_destroy_train(data);
	fann_destroy(ann);

	return ret;
}
