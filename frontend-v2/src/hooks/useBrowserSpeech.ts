import { useState, useEffect, useRef } from "react";

export function useBrowserSpeech() {
  const [transcript, setTranscript] = useState("");
  const [listening, setListening] = useState(false);
  const [supported, setSupported] = useState(true);
  const recRef = useRef<any>(null);
  const finalRef = useRef("");
  const activeRef = useRef(false);

  useEffect(() => {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SR) {
      setSupported(false);
      return;
    }
    const rec = new SR();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = "en-IN";
    rec.maxAlternatives = 3;

    rec.onresult = (event: any) => {
      let interim = "",
        final = "";
      for (let i = 0; i < event.results.length; i++) {
        let best = event.results[i][0];
        for (let j = 1; j < event.results[i].length; j++) {
          if (event.results[i][j].confidence > best.confidence) best = event.results[i][j];
        }
        if (event.results[i].isFinal) final += best.transcript + " ";
        else interim = best.transcript;
      }
      if (final) finalRef.current = final;
      setTranscript(finalRef.current + interim);
    };

    rec.onend = () => {
      if (activeRef.current) {
        try {
          rec.start();
        } catch (e) {}
      } else setListening(false);
    };

    rec.onerror = (e: any) => {
      if ((e.error === "no-speech" || e.error === "aborted") && activeRef.current) {
        try {
          rec.start();
        } catch (ex) {}
        return;
      }
      activeRef.current = false;
      setListening(false);
    };

    recRef.current = rec;
  }, []);

  const startListening = () => {
    finalRef.current = "";
    setTranscript("");
    activeRef.current = true;
    try {
      recRef.current.start();
    } catch (e) {}
    setListening(true);
  };

  const stopListening = () => {
    activeRef.current = false;
    try {
      recRef.current.stop();
    } catch (e) {}
    setListening(false);
  };

  const reset = () => {
    finalRef.current = "";
    setTranscript("");
  };

  return { transcript, setTranscript, listening, supported, startListening, stopListening, reset, processing: false };
}
