import type { Types } from '@cornerstonejs/core';
declare function generateAffineMatrix(origin: Types.Point3, orientation: Types.Mat3, spacing: Types.Point3): Types.AffineMatrix;
declare function parseAffineMatrix(affine: any): {
    origin: Types.Point3;
    orientation: Types.Mat3;
    spacing: Types.Point3;
};
export { generateAffineMatrix, parseAffineMatrix };
