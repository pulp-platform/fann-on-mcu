#include "fann_conf.h"
#include "fann_utils.h"
#include <arm_math.h>

void arm_dot_prod_fixed32_accum32(q31_t * pSrcA, q31_t * pSrcB, uint32_t blockSize, q31_t * result) {
	
  q31_t sum = 0;
  uint32_t blkCnt;

#ifndef ARM_MATH_CM0_FAMILY

	// 4x loop unrolling: 
  q31_t inA1, inA2, inA3, inA4;
  q31_t inB1, inB2, inB3, inB4;

  blkCnt = blockSize >> 2u;
  while(blkCnt > 0u)
  {
    inA1 = *pSrcA++; inA2 = *pSrcA++; inA3 = *pSrcA++; inA4 = *pSrcA++;
    inB1 = *pSrcB++; inB2 = *pSrcB++; inB3 = *pSrcB++; inB4 = *pSrcB++;

    sum += ((q31_t) inA1 * inB1) >> DECIMAL_POINT;
    sum += ((q31_t) inA2 * inB2) >> DECIMAL_POINT;
    sum += ((q31_t) inA3 * inB3) >> DECIMAL_POINT;
    sum += ((q31_t) inA4 * inB4) >> DECIMAL_POINT;
		
//    sum += ((q31_t) inA1 * inB1);
//    sum += ((q31_t) inA2 * inB2);
//    sum += ((q31_t) inA3 * inB3);
//    sum += ((q31_t) inA4 * inB4);
//		sum = sum >> DECIMAL_POINT;

    blkCnt--;
  }

  //set block counter to remaining number of iterations
  blkCnt = blockSize % 0x4u;
#else
	// for the Cortex-M0, we should not do loop unrolling, and
	// thus perform all iterations individually
  blkCnt = blockSize;
#endif 

  while(blkCnt > 0u) {
    sum += ((q31_t) (*pSrcA++) * (*pSrcB++)) >> DECIMAL_POINT;
    blkCnt--;
  }
  *result = sum;
}
