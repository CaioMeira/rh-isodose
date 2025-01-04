export default function getScalingParameters(metaData, imageId) {
    const modalityLutModule = metaData.get('modalityLutModule', imageId) || {};
    const generalSeriesModule = (metaData.get('generalSeriesModule', imageId) ||
        {});
    const { modality } = generalSeriesModule;
    const scalingParameters = {
        rescaleSlope: modalityLutModule.rescaleSlope,
        rescaleIntercept: modalityLutModule.rescaleIntercept,
        modality,
    };
    const suvFactor = metaData.get('scalingModule', imageId) || {};
    return {
        ...scalingParameters,
        ...(modality === 'PT' && { suvbw: suvFactor.suvbw }),
    };
}
