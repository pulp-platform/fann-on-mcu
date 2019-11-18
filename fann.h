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

#ifndef FANN_FANN_H_
#define FANN_FANN_H_

#include "fann_conf.h"

#ifdef FIXEDFANN
typedef int fann_type;
#else
typedef float fann_type;
#endif

/* Function: fann_run
    Will run input through the neural network, returning an array of outputs, the number of which being
    equal to the number of neurons in the output layer.

    See also:
        <fann_test>

    This function appears in FANN >= 1.0.0.
*/
// __attribute__((ramfunc))
fann_type *fann_run(fann_type * input);


#endif /* FANN_FANN_H_ */
