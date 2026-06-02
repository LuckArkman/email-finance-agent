namespace Hermes.OCR;

public record OcrResult(
    string RawText,
    float Confidence
);
