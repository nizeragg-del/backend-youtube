import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import { MotionEasings } from "../utils/motion";

export const GraphicElements: React.FC<{ theme?: string }> = ({ theme }) => {
  const frame = useCurrentFrame();
  
  // Cores baseadas no tema
  const isDark = theme?.toLowerCase().includes("profundo") || theme?.toLowerCase().includes("mistério");
  const primaryColor = isDark ? "#4a90e2" : "#FFD700";
  
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {/* Grade de fundo sutil */}
      <AbsoluteFill style={{
        backgroundImage: `radial-gradient(${primaryColor}22 1px, transparent 1px)`,
        backgroundSize: "50px 50px",
        opacity: 0.3
      }} />
      
      {/* Círculo concêntrico animado */}
      <div style={{
        position: "absolute",
        top: "50%",
        left: "50%",
        width: "600px",
        height: "600px",
        border: `1px solid ${primaryColor}44`,
        borderRadius: "50%",
        transform: `translate(-50%, -50%) scale(${interpolate(frame % 300, [0, 300], [0.8, 1.2], { easing: MotionEasings.slowSlow })})`,
        opacity: interpolate(frame % 300, [0, 150, 300], [0, 0.4, 0])
      }} />

      {/* Linhas de "Flow" Graphics */}
      <svg width="100%" height="100%" style={{ position: "absolute" }}>
        <path
          d="M 0 800 Q 540 600 1080 800"
          fill="none"
          stroke={primaryColor}
          strokeWidth="2"
          strokeDasharray="10 20"
          opacity="0.2"
          style={{
            transform: `translateY(${Math.sin(frame / 60) * 20}px)`
          }}
        />
      </svg>
    </AbsoluteFill>
  );
};
