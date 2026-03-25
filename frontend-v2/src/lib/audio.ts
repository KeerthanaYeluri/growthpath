export async function convertToWav(blob: Blob): Promise<Blob> {
  const arrayBuffer = await blob.arrayBuffer();
  const audioCtx = new ((window as any).AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
  let audioBuffer: AudioBuffer;
  try {
    audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
  } catch (e) {
    audioCtx.close();
    return blob;
  }
  const sampleRate = 16000;
  const rawData = audioBuffer.getChannelData(0);
  let samples: Float32Array;
  if (audioBuffer.sampleRate !== sampleRate) {
    const ratio = audioBuffer.sampleRate / sampleRate;
    const newLen = Math.round(rawData.length / ratio);
    samples = new Float32Array(newLen);
    for (let i = 0; i < newLen; i++) samples[i] = rawData[Math.round(i * ratio)];
  } else {
    samples = rawData;
  }
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);
  const writeStr = (offset: number, str: string) => {
    for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
  };
  writeStr(0, "RIFF");
  view.setUint32(4, 36 + samples.length * 2, true);
  writeStr(8, "WAVE");
  writeStr(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeStr(36, "data");
  view.setUint32(40, samples.length * 2, true);
  for (let i = 0; i < samples.length; i++) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  audioCtx.close();
  return new Blob([buffer], { type: "audio/wav" });
}
