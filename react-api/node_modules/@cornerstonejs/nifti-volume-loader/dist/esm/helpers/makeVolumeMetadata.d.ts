import type { Types } from '@cornerstonejs/core';
export default function makeVolumeMetadata(niftiHeader: any, orientation: any, pixelRepresentation: any): {
    volumeMetadata: Types.Metadata;
    dimensions: Types.Point3;
    direction: Types.Mat3;
};
