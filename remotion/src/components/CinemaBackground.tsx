import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export interface BackgroundProps {
  visualMeta?: string;
}

const getColorsFromMeta = (meta: string) => {
  const m = meta.toLowerCase();
  if (m.includes("pôr do sol") || m.includes("quente") || m.includes("esperança")) {
    return { start: "#4b1212", mid: "#c0392b", end: "#f1c40f" }; // Tons quentes/dourados
  }
  if (m.includes("mistério") || m.includes("profundo") || m.includes("azul") || m.includes("noite")) {
    return { start: "#1a1a2e", mid: "#16213e", end: "#0f3460" }; // Tons azuis profundos
  }
  if (m.includes("espiritual") || m.includes("roxo") || m.includes("divino")) {
    return { start: "#2d0b3d", mid: "#4b1348", end: "#c94b4b" }; // Roxo litúrgico
  }
  return { start: "#000000", mid: "#1a1a1a", end: "#333333" }; // Fallback Dark
};

export const CinemaBackground: React.FC<BackgroundProps> = ({ visualMeta = "" }) => { // eslint-disable-line
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig(); // eslint-disable-line
  const colors = getColorsFromMeta(visualMeta);

  // Efeito Ken Burns (Zoom Suave)
  const scale = interpolate(frame, [0, 300], [1, 1.15]);
  const translateX = interpolate(frame, [0, 300], [0, -20]);

  return (
    <AbsoluteFill style={{ backgroundColor: "black", overflow: "hidden" }}>
      {/* Camada de Gradiente Dinâmico */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at center, ${colors.mid} 0%, ${colors.start} 100%)`,
          transform: `scale(${scale}) translateX(${translateX}px)`,
        }}
      />

      {/* Camada de Brilho Secundário */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(45deg, transparent 0%, ${colors.end}22 50%, transparent 100%)`,
          opacity: interpolate(Math.sin(frame / 60), [-1, 1], [0.3, 0.7]),
        }}
      />

      {/* Textura de Grão (Grainy Overlay) */}
      <AbsoluteFill
        style={{
          opacity: 0.04,
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />
      
      {/* Vinheta Dinâmica */}
      <AbsoluteFill style={{
        boxShadow: "inset 0 0 500px rgba(0,0,0,0.85)",
        pointerEvents: "none"
      }} />
    </AbsoluteFill>
  );
};
