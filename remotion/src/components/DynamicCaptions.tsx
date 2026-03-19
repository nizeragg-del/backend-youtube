import React, { useMemo } from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { montserrat } from "../fonts";
import { WordSync } from "../ShortsComp";

interface DynamicCaptionsProps {
  syncData: WordSync[];
  wordsPerPhrase?: number;
}

export const DynamicCaptions: React.FC<DynamicCaptionsProps> = ({ 
  syncData, 
  wordsPerPhrase = 5 
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  const phrases = useMemo(() => {
    const arr = [];
    for (let i = 0; i < syncData.length; i += wordsPerPhrase) {
      const chunk = syncData.slice(i, i + wordsPerPhrase);
      arr.push({
        words: chunk,
        start: chunk[0].start,
        // Mantém na tela por um pequeno buffer após a última palavra
        end: chunk[chunk.length - 1].end + 0.3 
      });
    }
    return arr;
  }, [syncData, wordsPerPhrase]);

  const activePhrase = phrases.find(
    p => currentTime >= p.start && currentTime <= p.end
  );

  if (!activePhrase) return null;

  return (
    <div style={{
      display: "flex",
      flexWrap: "wrap",
      justifyContent: "center",
      alignItems: "center",
      gap: "20px",
      padding: "0 60px"
    }}>
      {activePhrase.words.map((w, i) => {
        const isActive = currentTime >= w.start && currentTime <= w.end;
        const hasPassed = currentTime > w.end;
        
        // Frame atual relativo ao início exato dessa palavra
        const isActiveFrame = Math.max(0, frame - (w.start * fps));
        
        // Pulo agressivo (Bouncing)
        const pop = spring({
          fps,
          frame: isActiveFrame,
          config: { damping: 10, mass: 0.5, stiffness: 200 }
        });
        
        // A fonte cresce 1.15x e gira levemente
        const rotation = isActive ? interpolate(pop, [0, 1], [0, -3]) : 0;
        const scale = isActive ? interpolate(pop, [0, 1], [1, 1.15]) : 1;
        
        // Estilo visual Kwai/Hormozi
        const isYellow = isActive;
        const textColor = isYellow ? "#FFE600" : (hasPassed ? "#FFFFFF" : "rgba(255,255,255,0.8)");
        const bgColor = isYellow ? "rgba(0, 0, 0, 0.85)" : "transparent";
        const borderColor = isYellow ? "6px solid #FFE600" : "6px solid transparent";
        const textShadow = isYellow 
            ? "0 0 30px rgba(255,230,0,0.8), 0 10px 20px rgba(0,0,0,1)" 
            : "0 10px 20px rgba(0,0,0,0.9)";

        return (
          <div key={`${w.word}-${i}`} style={{
            fontFamily: montserrat,
            fontSize: "100px",
            fontWeight: 900,
            color: textColor,
            textTransform: "uppercase",
            textShadow,
            background: bgColor,
            padding: isYellow ? "15px 30px" : "15px 0",
            borderRadius: "25px",
            transform: `scale(${scale}) rotate(${rotation}deg)`,
            transition: "all 0.1s ease-out",
            lineHeight: 1.1,
            border: borderColor,
            WebkitTextStroke: "6px black", // Borda preta espessa do texto
            boxShadow: isYellow ? "0 25px 50px rgba(0,0,0,0.5)" : "none",
            zIndex: isActive ? 10 : 1
          }}>
            {w.word}
          </div>
        );
      })}
    </div>
  );
};
