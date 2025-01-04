import { useEffect, useRef } from "react"
import createImageIdsAndCacheMetaData from "./lib/createImageIdsAndCacheMetaData"
import {
  RenderingEngine,
  Enums,
  type Types,
  volumeLoader,
  imageLoader,
  setVolumesForViewports,
  eventTarget,
} from "@cornerstonejs/core"
import { init as csRenderInit } from "@cornerstonejs/core"
import {
  cornerstoneNiftiImageLoader,
  createNiftiImageIdsAndCacheMetadata,
  Enums as NiftiEnums,
} from "@cornerstonejs/nifti-volume-loader"
import { ImageLoaderFn } from "@cornerstonejs/core/types"

function CT() {
  const elementRef = useRef<HTMLDivElement>(null)
  const running = useRef(false)

  useEffect(() => {
    const setup = async () => {
      if (running.current) {
        return
      }
      running.current = true

      await csRenderInit()

      const niftiURL =
        "https://ohif-assets.s3.us-east-2.amazonaws.com/nifti/CTACardio.nii.gz"

      imageLoader.registerImageLoader(
        "nifti",
        cornerstoneNiftiImageLoader as unknown as ImageLoaderFn
      )

      const imageIds = await createNiftiImageIdsAndCacheMetadata({
        url: niftiURL,
      })

      const renderingEngineId = "myRenderingEngine"
      const renderingEngine = new RenderingEngine(renderingEngineId)

      const viewportId1 = "CT_NIFTI_AXIAL"
      const viewportId2 = "CT_NIFTI_SAGITTAL"
      const viewportId3 = "CT_NIFTI_CORONAL"

      const viewportInputArray = [
        {
          viewportId: viewportId1,
          type: Enums.ViewportType.ORTHOGRAPHIC,
          element: elementRef.current,
          defaultOptions: {
            orientation: Enums.OrientationAxis.AXIAL,
          },
        },
        {
          viewportId: viewportId2,
          type: Enums.ViewportType.ORTHOGRAPHIC,
          element: elementRef.current,
          defaultOptions: {
            orientation: Enums.OrientationAxis.SAGITTAL,
          },
        },
        {
          viewportId: viewportId3,
          type: Enums.ViewportType.ORTHOGRAPHIC,
          element: elementRef.current,
          defaultOptions: {
            orientation: Enums.OrientationAxis.CORONAL,
          },
        },
      ]

      renderingEngine.setViewports(viewportInputArray)

      const updateProgress = (evt) => {
        const { data } = evt.detail

        if (!data) {
          return
        }

        const { total, loaded } = data

        if (!total) {
          return
        }

        const progress = Math.round((loaded / total) * 100)

        const element = document.querySelector('progress')
        element.value = progress
      }

      eventTarget.addEventListener(
        NiftiEnums.Events.NIFTI_VOLUME_PROGRESS,
        updateProgress
      )

      const volumeId = `cornerstoneStreamingImageVolume:${niftiURL}`
      const volume = await volumeLoader.createAndCacheVolume(volumeId, {
        imageIds,
      })

      await volume.load()

      setVolumesForViewports(
        renderingEngine,
        [{ volumeId }],
        viewportInputArray.map((v) => v.viewportId)
      )

      renderingEngine.render()
    }

    setup()

  }, [elementRef, running])

  return (
    <div
      ref={elementRef}
      style={{
        width: "512px",
        height: "512px",
        backgroundColor: "#000",
      }}
    ></div>
  )
}

export default CT