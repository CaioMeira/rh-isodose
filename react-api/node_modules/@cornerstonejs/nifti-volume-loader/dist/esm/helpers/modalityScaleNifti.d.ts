import type { Types } from '@cornerstonejs/core';
export default function modalityScaleNifti(niftiHeader: any, niftiImageBuffer: any): {
    scalarData: Types.PixelDataTypedArray;
    pixelRepresentation: number;
};
