export declare const urlsMap: Map<any, any>;
export declare function fetchArrayBuffer({ url, onProgress, controller, onLoad, onHeader, loadFullVolume, }: {
    url: any;
    onProgress: any;
    controller: any;
    onLoad: any;
    onHeader: any;
    loadFullVolume?: boolean;
}): Promise<{
    data: Uint8Array;
    headerInfo: any;
    sliceInfo: any;
}>;
declare function createNiftiImageIdsAndCacheMetadata({ url }: {
    url: any;
}): Promise<any[]>;
export { createNiftiImageIdsAndCacheMetadata };
