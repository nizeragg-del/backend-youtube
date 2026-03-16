import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export const GodRays: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  return (
    <AbsoluteFill style={{ overflow: "hidden", pointerEvents: "none" }}>
      {[...Array(5)].map((_, i) => {
        const opacity = interpolate(
          Math.sin(frame / 20 + i),
          [-1, 1],
          [0.1, 0.3]
        );
        const rotation = -30 + i * 15;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              top: -height,
              left: width * 0.2 + i * 100,
              width: "200px",
              height: height * 3,
              background: "linear-gradient(to bottom, rgba(255,255,255,0.4) 0%, transparent 80%)",
              transform: `rotate(${rotation}deg)`,
              filter: "blur(40px)",
              opacity,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

export const GoldenParticles: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {[...Array(30)].map((_, i) => {
        const seed = i * 123.45;
        const x = (seed % width) + Math.sin(frame / 50 + seed) * 50;
        const y = ((seed * 1.5) % height) - (frame % height);
        const opacity = interpolate(
          Math.sin(frame / 30 + seed),
          [-1, 1],
          [0.1, 0.6]
        );
        const scale = interpolate(Math.cos(frame / 40 + seed), [-1, 1], [0.5, 1.2]);

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y < -10 ? y + height : y,
              width: "4px",
              height: "4px",
              backgroundColor: "#ffd700",
              borderRadius: "50%",
              boxShadow: "0 0 10px #ffd700",
              opacity,
              transform: `scale(${scale})`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
