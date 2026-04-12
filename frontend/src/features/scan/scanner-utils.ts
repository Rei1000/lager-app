type MinimalDetection = {
  rawValue?: string | null;
};

export function getFirstDetectedCode(detections: MinimalDetection[]): string | null {
  for (const detection of detections) {
    const value = detection.rawValue?.trim();
    if (value) {
      return value;
    }
  }
  return null;
}

export function canUseBrowserScanner(
  mediaDevices: MediaDevices | undefined,
  barcodeDetectorCtor: unknown
): boolean {
  return Boolean(mediaDevices?.getUserMedia && barcodeDetectorCtor);
}
