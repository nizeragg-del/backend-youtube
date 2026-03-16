import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, staticFile, Img } from "remotion";

export interface ImageBackgroundProps {
  src?: string;
}

export const ImageBackground: React.FC<ImageBackgroundProps> = ({ src }) => {
  const frame = useCurrentFrame();

  // Efeito Ken Burns (Zoom Suave e sutil movimento)
  const scale = interpolate(frame, [0, 300], [1, 1.12], {
    extrapolateRight: "clamp",
  });
  
  const translateX = interpolate(frame, [0, 300], [0, -15], {
    extrapolateRight: "clamp",
  });

  if (!src) {
    return <AbsoluteFill style={{ backgroundColor: "#1a1a1a" }} />;
  }

  return (
    <AbsoluteFill style={{ backgroundColor: "black", overflow: "hidden" }}>
      {/* Camada da Imagem com Zoom */}
      <AbsoluteFill
        style={{
          transform: `scale(${scale}) translateX(${translateX}px)`,
        }}
      >
        <Img 
          src={staticFile(src)} 
          style={{ 
            width: "100%", 
            height: "100%", 
            objectFit: "cover",
            filter: "brightness(0.7) contrast(1.1)"
          }} 
        />
      </AbsoluteFill>

      {/* Camada de Gradiente para Vinheta e profundidade */}
      <AbsoluteFill
        style={{
          background: "radial-gradient(circle at center, transparent 0%, rgba(0,0,0,0.4) 100%)",
        }}
      />

      {/* Textura de Grão para look premium */}
      <AbsoluteFill
        style={{
          opacity: 0.05,
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          pointerEvents: "none"
        }}
      />
      
      {/* Vinheta Estática */}
      <AbsoluteFill style={{
        boxShadow: "inset 0 0 400px rgba(0,0,0,0.8)",
        pointerEvents: "none"
      }} />
    </AbsoluteFill>
  );
};
