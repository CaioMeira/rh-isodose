import { utilities } from '@cornerstonejs/core';
import { vec3 } from 'gl-matrix';
const { windowLevel } = utilities;
export default function makeVolumeMetadata(niftiHeader, orientation, pixelRepresentation) {
    const { numBitsPerVoxel, littleEndian, pixDims, dims } = niftiHeader;
    const min = Infinity;
    const max = -Infinity;
    const frameLength = dims[1] * dims[2];
    const middleFrameIndex = Math.floor(dims[3] / 2);
    const offset = frameLength * middleFrameIndex;
    const { windowWidth, windowCenter } = { windowWidth: 400, windowCenter: 40 };
    const rowCosines = vec3.create();
    const columnCosines = vec3.create();
    const scanAxisNormal = vec3.create();
    vec3.set(rowCosines, orientation[0], orientation[1], orientation[2]);
    vec3.set(columnCosines, orientation[3], orientation[4], orientation[5]);
    vec3.set(scanAxisNormal, orientation[6], orientation[7], orientation[8]);
    return {
        volumeMetadata: {
            BitsAllocated: numBitsPerVoxel,
            BitsStored: numBitsPerVoxel,
            SamplesPerPixel: 1,
            HighBit: littleEndian ? numBitsPerVoxel - 1 : 1,
            PhotometricInterpretation: 'MONOCHROME2',
            PixelRepresentation: pixelRepresentation,
            ImageOrientationPatient: [
                rowCosines[0],
                rowCosines[1],
                rowCosines[2],
                columnCosines[0],
                columnCosines[1],
                columnCosines[2],
            ],
            PixelSpacing: [pixDims[1], pixDims[2]],
            Columns: dims[1],
            Rows: dims[2],
            voiLut: [{ windowCenter, windowWidth }],
            FrameOfReferenceUID: '1.2.3',
            Modality: 'MR',
            VOILUTFunction: 'LINEAR',
        },
        dimensions: [dims[1], dims[2], dims[3]],
        direction: new Float32Array([
            rowCosines[0],
            rowCosines[1],
            rowCosines[2],
            columnCosines[0],
            columnCosines[1],
            columnCosines[2],
            scanAxisNormal[0],
            scanAxisNormal[1],
            scanAxisNormal[2],
        ]),
    };
}
