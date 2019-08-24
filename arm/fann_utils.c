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


/* ----------------------------------------------------------------------
 * Project:      CMSIS DSP Library
 * Title:        arm_copy_q31.c
 * Description:  Copies the elements of a Q31 vector
 *
 * $Date:        18. March 2019
 * $Revision:    V1.6.0
 *
 * Target Processor: Cortex-M cores
 * -------------------------------------------------------------------- */
/*
 * Copyright (C) 2010-2019 ARM Limited or its affiliates. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the License); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an AS IS BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "arm_math.h"

/**
  @ingroup groupSupport
 */

/**
  @addtogroup copy
  @{
 */

/**
  @brief         Copies the elements of a Q31 vector.
  @param[in]     pSrc       points to input vector
  @param[out]    pDst       points to output vector
  @param[in]     blockSize  number of samples in each vector
  @return        none
 */

void arm_copy_q31(
  const q31_t * pSrc,
        q31_t * pDst,
        uint32_t blockSize)
{
  uint32_t blkCnt;                               /* Loop counter */

#if defined (ARM_MATH_LOOPUNROLL)

  /* Loop unrolling: Compute 4 outputs at a time */
  blkCnt = blockSize >> 2U;

  while (blkCnt > 0U)
  {
    /* C = A */

    /* Copy and store result in destination buffer */
    *pDst++ = *pSrc++;
    *pDst++ = *pSrc++;
    *pDst++ = *pSrc++;
    *pDst++ = *pSrc++;

    /* Decrement loop counter */
    blkCnt--;
  }

  /* Loop unrolling: Compute remaining outputs */
  blkCnt = blockSize % 0x4U;

#else

  /* Initialize blkCnt with number of samples */
  blkCnt = blockSize;

#endif /* #if defined (ARM_MATH_LOOPUNROLL) */

  while (blkCnt > 0U)
  {
    /* C = A */

    /* Copy and store result in destination buffer */
    *pDst++ = *pSrc++;

    /* Decrement loop counter */
    blkCnt--;
  }
}

/**
  @} end of BasicCopy group
 */

/* ----------------------------------------------------------------------
 * Project:      CMSIS DSP Library
 * Title:        arm_fill_q31.c
 * Description:  Fills a constant value into a Q31 vector
 *
 * $Date:        18. March 2019
 * $Revision:    V1.6.0
 *
 * Target Processor: Cortex-M cores
 * -------------------------------------------------------------------- */
/*
 * Copyright (C) 2010-2019 ARM Limited or its affiliates. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the License); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an AS IS BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "arm_math.h"

/**
  @ingroup groupSupport
 */

/**
  @addtogroup Fill
  @{
 */

/**
  @brief         Fills a constant value into a Q31 vector.
  @param[in]     value      input value to be filled
  @param[out]    pDst       points to output vector
  @param[in]     blockSize  number of samples in each vector
  @return        none
 */

void arm_fill_q31(
  q31_t value,
  q31_t * pDst,
  uint32_t blockSize)
{
  uint32_t blkCnt;                               /* Loop counter */

#if defined (ARM_MATH_LOOPUNROLL)

  /* Loop unrolling: Compute 4 outputs at a time */
  blkCnt = blockSize >> 2U;

  while (blkCnt > 0U)
  {
    /* C = value */

    /* Fill value in destination buffer */
    *pDst++ = value;
    *pDst++ = value;
    *pDst++ = value;
    *pDst++ = value;

    /* Decrement loop counter */
    blkCnt--;
  }

  /* Loop unrolling: Compute remaining outputs */
  blkCnt = blockSize % 0x4U;

#else

  /* Initialize blkCnt with number of samples */
  blkCnt = blockSize;

#endif /* #if defined (ARM_MATH_LOOPUNROLL) */

  while (blkCnt > 0U)
  {
    /* C = value */

    /* Fill value in destination buffer */
    *pDst++ = value;

    /* Decrement loop counter */
    blkCnt--;
  }
}

/**
  @} end of Fill group
 */


/* ----------------------------------------------------------------------
 * Project:      CMSIS DSP Library
 * Title:        arm_dot_prod_f32.c
 * Description:  Floating-point dot product
 *
 * $Date:        18. March 2019
 * $Revision:    V1.6.0
 *
 * Target Processor: Cortex-M cores
 * -------------------------------------------------------------------- */
/*
 * Copyright (C) 2010-2019 ARM Limited or its affiliates. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the License); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an AS IS BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "arm_math.h"

/**
  @ingroup groupMath
 */

/**
  @defgroup BasicDotProd Vector Dot Product

  Computes the dot product of two vectors.
  The vectors are multiplied element-by-element and then summed.

  <pre>
      sum = pSrcA[0]*pSrcB[0] + pSrcA[1]*pSrcB[1] + ... + pSrcA[blockSize-1]*pSrcB[blockSize-1]
  </pre>

  There are separate functions for floating-point, Q7, Q15, and Q31 data types.
 */

/**
  @addtogroup BasicDotProd
  @{
 */

/**
  @brief         Dot product of floating-point vectors.
  @param[in]     pSrcA      points to the first input vector.
  @param[in]     pSrcB      points to the second input vector.
  @param[in]     blockSize  number of samples in each vector.
  @param[out]    result     output result returned here.
  @return        none
 */

void arm_dot_prod_f32(
  const float32_t * pSrcA,
  const float32_t * pSrcB,
        uint32_t blockSize,
        float32_t * result)
{
        uint32_t blkCnt;                               /* Loop counter */
        float32_t sum = 0.0f;                          /* Temporary return variable */

#if defined(ARM_MATH_NEON)
    float32x4_t vec1;
    float32x4_t vec2;
    float32x4_t res;
    float32x4_t accum = vdupq_n_f32(0);    

    /* Compute 4 outputs at a time */
    blkCnt = blockSize >> 2U;

    vec1 = vld1q_f32(pSrcA);
    vec2 = vld1q_f32(pSrcB);

    while (blkCnt > 0U)
    {
        /* C = A[0]*B[0] + A[1]*B[1] + A[2]*B[2] + ... + A[blockSize-1]*B[blockSize-1] */
        /* Calculate dot product and then store the result in a temporary buffer. */
        
	accum = vmlaq_f32(accum, vec1, vec2);
	
        /* Increment pointers */
        pSrcA += 4;
        pSrcB += 4; 

        vec1 = vld1q_f32(pSrcA);
        vec2 = vld1q_f32(pSrcB);
        
        /* Decrement the loop counter */
        blkCnt--;
    }
    
#if __aarch64__
    sum = vpadds_f32(vpadd_f32(vget_low_f32(accum), vget_high_f32(accum)));
#else
    sum = (vpadd_f32(vget_low_f32(accum), vget_high_f32(accum)))[0] + (vpadd_f32(vget_low_f32(accum), vget_high_f32(accum)))[1];
#endif    

    /* Tail */
    blkCnt = blockSize & 0x3;

#else
#if defined (ARM_MATH_LOOPUNROLL)

  /* Loop unrolling: Compute 4 outputs at a time */
  blkCnt = blockSize >> 2U;

  /* First part of the processing with loop unrolling. Compute 4 outputs at a time.
   ** a second loop below computes the remaining 1 to 3 samples. */
  while (blkCnt > 0U)
  {
    /* C = A[0]* B[0] + A[1]* B[1] + A[2]* B[2] + .....+ A[blockSize-1]* B[blockSize-1] */

    /* Calculate dot product and store result in a temporary buffer. */
    sum += (*pSrcA++) * (*pSrcB++);

    sum += (*pSrcA++) * (*pSrcB++);

    sum += (*pSrcA++) * (*pSrcB++);

    sum += (*pSrcA++) * (*pSrcB++);

    /* Decrement loop counter */
    blkCnt--;
  }

  /* Loop unrolling: Compute remaining outputs */
  blkCnt = blockSize % 0x4U;

#else

  /* Initialize blkCnt with number of samples */
  blkCnt = blockSize;

#endif /* #if defined (ARM_MATH_LOOPUNROLL) */
#endif /* #if defined(ARM_MATH_NEON) */

  while (blkCnt > 0U)
  {
    /* C = A[0]* B[0] + A[1]* B[1] + A[2]* B[2] + .....+ A[blockSize-1]* B[blockSize-1] */

    /* Calculate dot product and store result in a temporary buffer. */
    sum += (*pSrcA++) * (*pSrcB++);

    /* Decrement loop counter */
    blkCnt--;
  }

  /* Store result in destination buffer */
  *result = sum;
}

/**
  @} end of BasicDotProd group
 */


/* ----------------------------------------------------------------------
 * Project:      CMSIS DSP Library
 * Title:        arm_copy_f32.c
 * Description:  Copies the elements of a floating-point vector
 *
 * $Date:        18. March 2019
 * $Revision:    V1.6.0
 *
 * Target Processor: Cortex-M cores
 * -------------------------------------------------------------------- */
/*
 * Copyright (C) 2010-2019 ARM Limited or its affiliates. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the License); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an AS IS BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "arm_math.h"

/**
  @ingroup groupSupport
 */

/**
  @defgroup copy Vector Copy

  Copies sample by sample from source vector to destination vector.

  <pre>
      pDst[n] = pSrc[n];   0 <= n < blockSize.
  </pre>

  There are separate functions for floating point, Q31, Q15, and Q7 data types.
 */

/**
  @addtogroup copy
  @{
 */

/**
  @brief         Copies the elements of a floating-point vector.
  @param[in]     pSrc       points to input vector
  @param[out]    pDst       points to output vector
  @param[in]     blockSize  number of samples in each vector
  @return        none
 */

#if defined(ARM_MATH_NEON_EXPERIMENTAL)
void arm_copy_f32(
  const float32_t * pSrc,
  float32_t * pDst,
  uint32_t blockSize)
{
  uint32_t blkCnt;                               /* loop counter */

  float32x4_t inV;

  blkCnt = blockSize >> 2U;

  /* Compute 4 outputs at a time.
   ** a second loop below computes the remaining 1 to 3 samples. */
  while (blkCnt > 0U)
  {
    /* C = A */
    /* Copy and then store the results in the destination buffer */
    inV = vld1q_f32(pSrc);
    vst1q_f32(pDst, inV);
    pSrc += 4;
    pDst += 4;

    /* Decrement the loop counter */
    blkCnt--;
  }

  /* If the blockSize is not a multiple of 4, compute any remaining output samples here.
   ** No loop unrolling is used. */
  blkCnt = blockSize & 3;

  while (blkCnt > 0U)
  {
    /* C = A */
    /* Copy and then store the results in the destination buffer */
    *pDst++ = *pSrc++;

    /* Decrement the loop counter */
    blkCnt--;
  }
}
#else
void arm_copy_f32(
  const float32_t * pSrc,
        float32_t * pDst,
        uint32_t blockSize)
{
  uint32_t blkCnt;                               /* Loop counter */

#if defined (ARM_MATH_LOOPUNROLL)

  /* Loop unrolling: Compute 4 outputs at a time */
  blkCnt = blockSize >> 2U;

  while (blkCnt > 0U)
  {
    /* C = A */

    /* Copy and store result in destination buffer */
    *pDst++ = *pSrc++;
    *pDst++ = *pSrc++;
    *pDst++ = *pSrc++;
    *pDst++ = *pSrc++;

    /* Decrement loop counter */
    blkCnt--;
  }

  /* Loop unrolling: Compute remaining outputs */
  blkCnt = blockSize % 0x4U;

#else

  /* Initialize blkCnt with number of samples */
  blkCnt = blockSize;

#endif /* #if defined (ARM_MATH_LOOPUNROLL) */

  while (blkCnt > 0U)
  {
    /* C = A */

    /* Copy and store result in destination buffer */
    *pDst++ = *pSrc++;

    /* Decrement loop counter */
    blkCnt--;
  }
}
#endif /* #if defined(ARM_MATH_NEON) */
/**
  @} end of BasicCopy group
 */


/* ----------------------------------------------------------------------
 * Project:      CMSIS DSP Library
 * Title:        arm_fill_f32.c
 * Description:  Fills a constant value into a floating-point vector
 *
 * $Date:        18. March 2019
 * $Revision:    V1.6.0
 *
 * Target Processor: Cortex-M cores
 * -------------------------------------------------------------------- */
/*
 * Copyright (C) 2010-2019 ARM Limited or its affiliates. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the License); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an AS IS BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "arm_math.h"

/**
  @ingroup groupSupport
 */

/**
  @defgroup Fill Vector Fill

  Fills the destination vector with a constant value.

  <pre>
      pDst[n] = value;   0 <= n < blockSize.
  </pre>

  There are separate functions for floating point, Q31, Q15, and Q7 data types.
 */

/**
  @addtogroup Fill
  @{
 */

/**
  @brief         Fills a constant value into a floating-point vector.
  @param[in]     value      input value to be filled
  @param[out]    pDst       points to output vector
  @param[in]     blockSize  number of samples in each vector
  @return        none
 */

#if defined(ARM_MATH_NEON_EXPERIMENTAL)
void arm_fill_f32(
  float32_t value,
  float32_t * pDst,
  uint32_t blockSize)
{
  uint32_t blkCnt;                               /* loop counter */


  float32x4_t inV = vdupq_n_f32(value);

  blkCnt = blockSize >> 2U;

  /* Compute 4 outputs at a time.
   ** a second loop below computes the remaining 1 to 3 samples. */
  while (blkCnt > 0U)
  {
    /* C = value */
    /* Fill the value in the destination buffer */
    vst1q_f32(pDst, inV);
    pDst += 4;

    /* Decrement the loop counter */
    blkCnt--;
  }

  /* If the blockSize is not a multiple of 4, compute any remaining output samples here.
   ** No loop unrolling is used. */
  blkCnt = blockSize & 3;

  while (blkCnt > 0U)
  {
    /* C = value */
    /* Fill the value in the destination buffer */
    *pDst++ = value;

    /* Decrement the loop counter */
    blkCnt--;
  }
}
#else
void arm_fill_f32(
  float32_t value,
  float32_t * pDst,
  uint32_t blockSize)
{
  uint32_t blkCnt;                               /* Loop counter */

#if defined (ARM_MATH_LOOPUNROLL)

  /* Loop unrolling: Compute 4 outputs at a time */
  blkCnt = blockSize >> 2U;

  while (blkCnt > 0U)
  {
    /* C = value */

    /* Fill value in destination buffer */
    *pDst++ = value;
    *pDst++ = value;
    *pDst++ = value;
    *pDst++ = value;

    /* Decrement loop counter */
    blkCnt--;
  }

  /* Loop unrolling: Compute remaining outputs */
  blkCnt = blockSize % 0x4U;

#else

  /* Initialize blkCnt with number of samples */
  blkCnt = blockSize;

#endif /* #if defined (ARM_MATH_LOOPUNROLL) */

  while (blkCnt > 0U)
  {
    /* C = value */

    /* Fill value in destination buffer */
    *pDst++ = value;

    /* Decrement loop counter */
    blkCnt--;
  }
}
#endif /* #if defined(ARM_MATH_NEON) */
/**
  @} end of Fill group
 */

