const local = {
    jpeg: undefined,
    decodeConfig: {},
};
export function initialize(decodeConfig) {
    local.decodeConfig = decodeConfig;
    if (local.jpeg) {
        return Promise.resolve();
    }
    return new Promise((resolve, reject) => {
        import('jpeg-lossless-decoder-js').then(({ Decoder }) => {
            const decoder = new Decoder();
            local.jpeg = decoder;
            resolve();
        }, reject);
    });
}
async function decodeJPEGLossless(imageFrame, pixelData) {
    await initialize();
    if (typeof local.jpeg === 'undefined') {
        throw new Error('No JPEG Lossless decoder loaded');
    }
    const byteOutput = imageFrame.bitsAllocated <= 8 ? 1 : 2;
    const buffer = pixelData.buffer;
    const decompressedData = local.jpeg.decode(buffer, pixelData.byteOffset, pixelData.length, byteOutput);
    if (imageFrame.pixelRepresentation === 0) {
        if (imageFrame.bitsAllocated === 16) {
            imageFrame.pixelData = new Uint16Array(decompressedData.buffer);
            return imageFrame;
        }
        imageFrame.pixelData = new Uint8Array(decompressedData.buffer);
        return imageFrame;
    }
    imageFrame.pixelData = new Int16Array(decompressedData.buffer);
    return imageFrame;
}
export default decodeJPEGLossless;
