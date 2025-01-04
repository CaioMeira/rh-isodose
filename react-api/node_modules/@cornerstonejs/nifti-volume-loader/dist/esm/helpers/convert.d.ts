import type { Types } from '@cornerstonejs/core';
declare const invertDataPerFrame: (dimensions: any, imageDataArray: any) => any;
declare function rasToLps(niftiHeader: any): {
    origin: Types.Point3;
    orientation: number[];
    spacing: Types.Point3;
};
declare function lpsToRas(header: any): {
    orientation: any[];
    origin: any[];
    dataType: any;
    dimensions: any;
    spacing: any;
    slope: any;
    inter: any;
    max: any;
    min: any;
};
export { lpsToRas, rasToLps, invertDataPerFrame };
