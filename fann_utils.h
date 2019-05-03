#ifndef FANN_FANN_UTILS_H_
#define FANN_FANN_UTILS_H_

//#include <arm_math.h>

typedef int int32_t;
typedef unsigned int uint32_t;

typedef int32_t q31_t;


void arm_dot_prod_fixed32_accum32(q31_t * pSrcA, q31_t * pSrcB, uint32_t blockSize, q31_t * result);
void plp_fill_fixed32(q31_t value, q31_t * pDst, uint32_t blockSize);
void plp_copy_fixed32(q31_t * pSrc, q31_t * pDst, uint32_t blockSize);

#endif //FANN_FANN_UTILS_H_
