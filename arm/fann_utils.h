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

#ifndef FANN_FANN_UTILS_H_
#define FANN_FANN_UTILS_H_

#include <arm_math.h>

void arm_dot_prod_fixed32_accum32(q31_t * pSrcA, q31_t * pSrcB, uint32_t blockSize, q31_t * result);

#endif //FANN_FANN_UTILS_H_
