function getInstanceModule(imageId, metaDataProvider, types) {
    const result = {};
    for (const t of types) {
        try {
            const data = metaDataProvider(t, imageId);
            if (data) {
                const capitalizedData = {};
                for (const key in data) {
                    if (key in data) {
                        const capitalizedKey = capitalizeTag(key);
                        capitalizedData[capitalizedKey] = data[key];
                    }
                }
                Object.assign(result, capitalizedData);
            }
        }
        catch (error) {
            console.error(`Error retrieving ${t} data:`, error);
        }
    }
    return result;
}
const capitalizeTag = (tag) => tag.charAt(0).toUpperCase() + tag.slice(1);
const instanceModuleNames = [
    'multiframeModule',
    'generalSeriesModule',
    'patientStudyModule',
    'imagePlaneModule',
    'nmMultiframeGeometryModule',
    'imagePixelModule',
    'modalityLutModule',
    'voiLutModule',
    'sopCommonModule',
    'petIsotopeModule',
    'overlayPlaneModule',
    'transferSyntax',
    'petSeriesModule',
    'petImageModule',
];
export { getInstanceModule, instanceModuleNames };
