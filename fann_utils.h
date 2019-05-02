#ifndef FANN_FANN_UTILS_H_
#define FANN_FANN_UTILS_H_

#include <arm_math.h>

void arm_dot_prod_fixed32_accum32(q31_t * pSrcA, q31_t * pSrcB, uint32_t blockSize, q31_t * result);

#endif //FANN_FANN_UTILS_H_
