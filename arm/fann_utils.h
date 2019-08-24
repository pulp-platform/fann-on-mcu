#ifndef FANN_FANN_UTILS_H_
#define FANN_FANN_UTILS_H_

#include <arm_math.h>

void arm_dot_prod_fixed32_accum32(q31_t * pSrcA, q31_t * pSrcB, uint32_t blockSize, q31_t * result);

void arm_copy_q31(
                  const q31_t * pSrc,
                  q31_t * pDst,
                  uint32_t blockSize);

void arm_fill_q31(
                  q31_t value,
                  q31_t * pDst,
                  uint32_t blockSize);

void arm_dot_prod_f32(
                      const float32_t * pSrcA,
                      const float32_t * pSrcB,
                      uint32_t blockSize,
                      float32_t * result);

void arm_copy_f32(
                  const float32_t * pSrc,
                  float32_t * pDst,
                  uint32_t blockSize);

void arm_fill_f32(
                  float32_t value,
                  float32_t * pDst,
                  uint32_t blockSize);

#endif //FANN_FANN_UTILS_H_
