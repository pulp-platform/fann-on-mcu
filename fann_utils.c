#include "fann_conf.h"
#include "fann_utils.h"

#ifdef ARMFANN
//#include <arm_math.h>

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

#endif

#ifdef PULPFANN

void plp_fill_fixed32(int32_t value, int32_t * pDst, uint32_t blockSize) {

  uint32_t blkCnt;                               /* loop counter */


#ifndef ARM_MATH_CM0_FAMILY

  /* Run the below code for Cortex-M4 and Cortex-M3 */
  int32_t in1 = value;
  int32_t in2 = value;
  int32_t in3 = value;
  int32_t in4 = value;

  /*loop Unrolling */
  blkCnt = blockSize >> 2u;

  /* First part of the processing with loop unrolling.  Compute 4 outputs at a time.    
   ** a second loop below computes the remaining 1 to 3 samples. */
  while(blkCnt > 0u)
  {
    /* C = value */
    /* Fill the value in the destination buffer */
    *pDst++ = in1;
    *pDst++ = in2;
    *pDst++ = in3;
    *pDst++ = in4;

    /* Decrement the loop counter */
    blkCnt--;
  }

  /* If the blockSize is not a multiple of 4, compute any remaining output samples here.    
   ** No loop unrolling is used. */
  blkCnt = blockSize % 0x4u;

#else

  /* Run the below code for Cortex-M0 */

  /* Loop over blockSize number of values */
  blkCnt = blockSize;

#endif /* #ifndef ARM_MATH_CM0_FAMILY */

  while(blkCnt > 0u)
  {
    /* C = value */
    /* Fill the value in the destination buffer */
    *pDst++ = value;

    /* Decrement the loop counter */
    blkCnt--;
  }
}



void plp_copy_fixed32(int32_t * pSrc, int32_t * pDst, uint32_t blockSize) {

  uint32_t blkCnt;                               /* loop counter */


#ifndef ARM_MATH_CM0_FAMILY

  /* Run the below code for Cortex-M4 and Cortex-M3 */
  int32_t in1, in2, in3, in4;

  /*loop Unrolling */
  blkCnt = blockSize >> 2u;

  /* First part of the processing with loop unrolling.  Compute 4 outputs at a time.    
   ** a second loop below computes the remaining 1 to 3 samples. */
  while(blkCnt > 0u)
  {
    /* C = A */
    /* Copy and then store the values in the destination buffer */
    in1 = *pSrc++;
    in2 = *pSrc++;
    in3 = *pSrc++;
    in4 = *pSrc++;

    *pDst++ = in1;
    *pDst++ = in2;
    *pDst++ = in3;
    *pDst++ = in4;

    /* Decrement the loop counter */
    blkCnt--;
  }

  /* If the blockSize is not a multiple of 4, compute any remaining output samples here.    
   ** No loop unrolling is used. */
  blkCnt = blockSize % 0x4u;

#else

  /* Run the below code for Cortex-M0 */

  /* Loop over blockSize number of values */
  blkCnt = blockSize;

#endif /* #ifndef ARM_MATH_CM0_FAMILY */

  while(blkCnt > 0u)
  {
    /* C = A */
    /* Copy and then store the value in the destination buffer */
    *pDst++ = *pSrc++;

    /* Decrement the loop counter */
    blkCnt--;
  }
}


void plp_dot_prod_fixed32_accum32(int32_t * pSrcA, int32_t * pSrcB, uint32_t blockSize, int32_t * result) {
	
  int32_t sum = 0;
  uint32_t blkCnt;

#ifndef ARM_MATH_CM0_FAMILY

	// 4x loop unrolling: 
  int32_t inA1, inA2, inA3, inA4;
  int32_t inB1, inB2, inB3, inB4;

  blkCnt = blockSize >> 2u;
  while(blkCnt > 0u)
  {
    inA1 = *pSrcA++; inA2 = *pSrcA++; inA3 = *pSrcA++; inA4 = *pSrcA++;
    inB1 = *pSrcB++; inB2 = *pSrcB++; inB3 = *pSrcB++; inB4 = *pSrcB++;

    sum += ((int32_t) inA1 * inB1) >> DECIMAL_POINT;
    sum += ((int32_t) inA2 * inB2) >> DECIMAL_POINT;
    sum += ((int32_t) inA3 * inB3) >> DECIMAL_POINT;
    sum += ((int32_t) inA4 * inB4) >> DECIMAL_POINT;
		
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
    sum += ((int32_t) (*pSrcA++) * (*pSrcB++)) >> DECIMAL_POINT;
    blkCnt--;
  }
  *result = sum;
}


#endif


