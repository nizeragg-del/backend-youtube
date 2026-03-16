import React from "react";
import {
  AbsoluteFill,
  Audio,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
} from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
// @ts-ignore
import { LightLeak } from "@remotion/light-leaks";
import { GodRays, GoldenParticles } from "./components/Effects";
import { OpeningScene } from "./scenes/OpeningScene";
import { VerseScene } from "./scenes/VerseScene";
import { SimpleMessageScene } from "./scenes/SimpleMessageScene";
import { ClimaxScene } from "./scenes/ClimaxScene";
import { EliteText } from "./components/EliteText";

export type WordSync = {
  word: string;
  start: number;
  end: number;
};

export interface ShortsProps {
  title: string;
  scriptText: string;
  visualMeta?: string;
  syncData: WordSync[];
  audioUrl?: string;
  imageUrls?: string[];
}

export const ShortsComp: React.FC<ShortsProps> = ({
  visualMeta,
  syncData,
  audioUrl,
  imageUrls = [],
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  
  // Transição de 20 frames
  const transitionDuration = 20;
  const timing = linearTiming({ durationInFrames: transitionDuration });
  
  // Duração dinâmica por cena baseado no número de imagens
  const totalScenes = imageUrls.length || 1;
  const framesPerScene = Math.floor(durationInFrames / totalScenes);
  const currentTime = frame / fps;
  
  const activeWord = syncData.find(
    (w) => currentTime >= w.start && currentTime <= w.end
  );

  return (
    <AbsoluteFill style={{ backgroundColor: "black", overflow: "hidden" }}>
      {audioUrl && <Audio src={staticFile(audioUrl)} />}

      <GodRays />
      <GoldenParticles />

      <TransitionSeries>
        {imageUrls.map((img, index) => {
          const isLast = index === imageUrls.length - 1;
          const duration = isLast 
            ? durationInFrames - (index * framesPerScene) 
            : framesPerScene;

          return (
            <React.Fragment key={index}>
              <TransitionSeries.Sequence durationInFrames={duration}>
                <OpeningScene 
                  text="" // Removido texto estático
                  imageSrc={img}
                />
              </TransitionSeries.Sequence>

              {!isLast && (
                <TransitionSeries.Transition
                  presentation={fade()}
                  timing={timing}
                />
              )}
            </React.Fragment>
          );
        })}
      </TransitionSeries>

      {/* Legendas de Elite Estabilizadas */}
      {activeWord && (
        <AbsoluteFill style={{ 
          justifyContent: "flex-end", 
          alignItems: "center", 
          bottom: "250px", // Usando bottom ao invés de paddingBottom para garantir posição fixa
          height: "200px",
          top: "auto",
          pointerEvents: "none",
          zIndex: 100
        }}>
          <EliteText 
            key={`${activeWord.word}-${activeWord.start}`} 
            text={activeWord.word} 
            type="caption" 
          />
        </AbsoluteFill>
      )}

      {/* Vinheta Premium */}
      <AbsoluteFill style={{
        boxShadow: "inset 0 0 700px rgba(0,0,0,0.9)",
        pointerEvents: "none",
        zIndex: 101
      }} />
    </AbsoluteFill>
  );
};
