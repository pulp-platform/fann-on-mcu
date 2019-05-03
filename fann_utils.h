#ifndef FANN_FANN_UTILS_H_
#define FANN_FANN_UTILS_H_

#ifdef ARMFANN
#include <arm_math.h>
void arm_dot_prod_fixed32_accum32(q31_t * pSrcA, q31_t * pSrcB, uint32_t blockSize, q31_t * result);
#endif

#ifdef PULPFANN

#include <pulp.h>
//typedef int int32_t;
//typedef unsigned int uint32_t;
//typedef int32_t q31_t;

void plp_fill_fixed32(int32_t value, int32_t * pDst, uint32_t blockSize);
void plp_copy_fixed32(int32_t * pSrc, int32_t * pDst, uint32_t blockSize);
void plp_dot_prod_fixed32_accum32(int32_t * pSrcA, int32_t * pSrcB, uint32_t blockSize, int32_t * result);

#endif

#endif //FANN_FANN_UTILS_H_
