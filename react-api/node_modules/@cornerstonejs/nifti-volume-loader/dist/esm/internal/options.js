let options = {
    beforeSend() {
    },
};
export function setOptions(newOptions) {
    options = Object.assign(options, newOptions);
}
export function getOptions() {
    return options;
}
