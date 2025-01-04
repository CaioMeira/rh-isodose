import type { Types } from '@cornerstonejs/core';
import type { LabelmapRepresentation } from '../../../types/SegmentationStateTypes';
export declare const MAX_NUMBER_COLORS = 255;
declare function removeRepresentation(viewportId: string, segmentationId: string, renderImmediate?: boolean): void;
declare function render(viewport: Types.IStackViewport | Types.IVolumeViewport, representation: LabelmapRepresentation): Promise<void>;
declare const _default: {
    render: typeof render;
    removeRepresentation: typeof removeRepresentation;
};
export default _default;
export { render, removeRepresentation };
