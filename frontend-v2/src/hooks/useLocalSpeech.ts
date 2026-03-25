import { useState, useRef } from "react";
import { convertToWav } from "@/lib/audio";
import { API } from "@/lib/api";

export function useLocalSpeech(engine: string) {
  const [transcript, setTranscript] = useState("");
  const [listening, setListening] = useState(false);
  const [processing, setProcessing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const intervalRef = useRef<any>(null);
  const fullTranscriptRef = useRef("");

  const sendChunk = async (blob: Blob, isFinal: boolean) => {
    if (blob.size < 100) return;
    setProcessing(true);
    try {
      const wavBlob = await convertToWav(blob);
      const formData = new FormData();
      formData.append("audio", wavBlob, "chunk.wav");
      formData.append("engine", engine);
      formData.append("is_final", isFinal ? "true" : "false");
      const res = await fetch(`${API}/transcribe/stream`, { method: "POST", body: formData });
      const data = await res.json();
      if (data.transcript) {
        if (isFinal) fullTranscriptRef.current = data.transcript;
        else fullTranscriptRef.current += data.transcript + " ";
        setTranscript(fullTranscriptRef.current.trim());
      }
    } catch (e) {
      console.error("Transcribe error:", e);
    }
    setProcessing(false);
  };

  const startListening = async () => {
    fullTranscriptRef.current = "";
    setTranscript("");
    chunksRef.current = [];
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { sampleRate: 16000, channelCount: 1, echoCancellation: true, noiseSuppression: true } as any,
      });
      streamRef.current = stream;
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm;codecs=opus" });
      mediaRecorderRef.current = recorder;
      let chunkCollector: Blob[] = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
          chunkCollector.push(e.data);
        }
      };
      recorder.start(500);
      setListening(true);
      intervalRef.current = setInterval(() => {
        if (chunkCollector.length > 0) {
          const blob = new Blob(chunkCollector, { type: "audio/webm" });
          chunkCollector = [];
          sendChunk(blob, false);
        }
      }, 4000);
    } catch (e) {
      console.error("Mic error:", e);
    }
  };

  const stopListening = async () => {
    clearInterval(intervalRef.current);
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") mediaRecorderRef.current.stop();
    if (streamRef.current) streamRef.current.getTracks().forEach((t) => t.stop());
    setListening(false);
    if (chunksRef.current.length > 0) {
      const fullBlob = new Blob(chunksRef.current, { type: "audio/webm" });
      chunksRef.current = [];
      fullTranscriptRef.current = "";
      await sendChunk(fullBlob, true);
    }
  };

  const reset = () => {
    fullTranscriptRef.current = "";
    setTranscript("");
  };

  return { transcript, setTranscript, listening, processing, supported: true, startListening, stopListening, reset };
}
