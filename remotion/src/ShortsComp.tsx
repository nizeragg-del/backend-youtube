import React from "react";
import {
  AbsoluteFill,
  Audio,
  useVideoConfig,
  staticFile,
} from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
// @ts-ignore
import { LightLeak } from "@remotion/light-leaks";
import { GodRays, GoldenParticles } from "./components/Effects";
import { OpeningScene } from "./scenes/OpeningScene";
import { TikTokCaptions } from "./components/TikTokCaptions";
import { Particles, TypeWriter } from "remotion-bits";

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
  title,
  visualMeta,
  syncData,
  audioUrl,
  imageUrls = [],
}) => {
  const { durationInFrames } = useVideoConfig();
  
  // Transição de 20 frames
  const transitionDuration = 20;
  const timing = linearTiming({ durationInFrames: transitionDuration });
  
  // Duração dinâmica por cena baseado no número de imagens
  const totalScenes = imageUrls.length || 1;
  const framesPerScene = Math.floor(durationInFrames / totalScenes);
  

  return (
    <AbsoluteFill style={{ backgroundColor: "black", overflow: "hidden" }}>
      {audioUrl && <Audio src={staticFile(audioUrl)} />}

      <GodRays />
      <GoldenParticles />
      <Particles />

      {/* Título com animação TypeWriter nos primeiros 3 segundos */}
      <AbsoluteFill style={{
        justifyContent: "center",
        alignItems: "center",
        top: "200px",
        height: "100px",
        pointerEvents: "none",
        zIndex: 102
      }}>
        <div style={{
          fontFamily: "Montserrat",
          fontSize: "60px",
          fontWeight: 900,
          color: "white",
          textTransform: "uppercase",
          textShadow: "0 0 20px rgba(0,0,0,0.8)"
        }}>
          <TypeWriter 
            text={title} 
            typeSpeed={3} 
          />
        </div>
      </AbsoluteFill>

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

      {/* Legendas Dinâmicas Estilo TikTok/Kwai */}
      <AbsoluteFill style={{ 
        justifyContent: "center", // Centraliza verticamente no container
        alignItems: "center", 
        bottom: "300px", // Posição exata acima da vinheta
        height: "400px", // Altura maior para acomodar quebras de linha das frases
        top: "auto",
        pointerEvents: "none",
        zIndex: 100
      }}>
        <TikTokCaptions syncData={syncData} wordsPerPhrase={3} />
      </AbsoluteFill>

      {/* Vinheta Premium */}
      <AbsoluteFill style={{
        boxShadow: "inset 0 0 700px rgba(0,0,0,0.9)",
        pointerEvents: "none",
        zIndex: 101
      }} />
    </AbsoluteFill>
  );
};
