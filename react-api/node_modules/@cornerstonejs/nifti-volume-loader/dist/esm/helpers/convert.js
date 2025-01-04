import { parseAffineMatrix } from './affineUtilities';
const invertDataPerFrame = (dimensions, imageDataArray) => {
    let TypedArrayConstructor;
    let bytesPerVoxel;
    if (imageDataArray instanceof Uint8Array ||
        imageDataArray instanceof ArrayBuffer) {
        TypedArrayConstructor = Uint8Array;
        bytesPerVoxel = 1;
    }
    else if (imageDataArray instanceof Int16Array) {
        TypedArrayConstructor = Int16Array;
        bytesPerVoxel = 2;
    }
    else if (imageDataArray instanceof Float32Array) {
        TypedArrayConstructor = Float32Array;
        bytesPerVoxel = 4;
    }
    else {
        throw new Error('imageDataArray needs to be a Uint8Array, Int16Array or Float32Array.');
    }
    const newImageDataArray = new TypedArrayConstructor(imageDataArray.byteLength);
    const view = new TypedArrayConstructor(imageDataArray);
    newImageDataArray.set(view);
    const numFrames = dimensions[2];
    const frameLength = dimensions[0] * dimensions[1];
    const buffer = newImageDataArray.buffer;
    for (let frame = 0; frame < numFrames; frame++) {
        const byteOffset = frameLength * frame * bytesPerVoxel;
        const frameView = new TypedArrayConstructor(buffer, byteOffset, frameLength);
        frameView.reverse();
    }
    return newImageDataArray;
};
function rasToLps(niftiHeader) {
    const { affine } = niftiHeader;
    const { orientation, origin, spacing } = parseAffineMatrix(affine);
    const newOrigin = [-origin[0], -origin[1], origin[2]];
    const newOrientation = [
        -orientation[0],
        -orientation[3],
        orientation[6],
        -orientation[1],
        -orientation[4],
        orientation[7],
        -orientation[2],
        -orientation[5],
        orientation[8],
    ];
    return {
        origin: newOrigin,
        orientation: newOrientation,
        spacing,
    };
}
function lpsToRas(header) {
    const { origin, orientation, spacing, dimensions, dataType } = header;
    const newOrigin = [-origin[0], -origin[1], origin[2]];
    const newOrientation = [
        -orientation[0],
        -orientation[3],
        orientation[6],
        -orientation[1],
        -orientation[4],
        orientation[7],
        -orientation[2],
        -orientation[5],
        orientation[8],
    ];
    return {
        orientation: newOrientation,
        origin: [newOrigin[0], newOrigin[1], newOrigin[2]],
        dataType,
        dimensions,
        spacing,
        slope: header.slope,
        inter: header.inter,
        max: header.max,
        min: header.min,
    };
}
export { lpsToRas, rasToLps, invertDataPerFrame };
