import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import { ImageBackground } from "../components/ImageBackground";
import { EliteText } from "../components/EliteText";

export const VerseScene: React.FC<{
  reference: string;
  text: string;
  visualMeta?: string;
  imageSrc?: string;
}> = ({ reference, text, imageSrc }) => {
  const frame = useCurrentFrame();
  const parallax = interpolate(frame, [0, 180], [0, -30]);

  return (
    <AbsoluteFill>
      <ImageBackground src={imageSrc} />
      
      <AbsoluteFill style={{ 
        justifyContent: "center", 
        alignItems: "center", 
        flexDirection: "column",
        gap: "40px",
        transform: `translateY(${parallax}px)`
      }}>
        <EliteText 
          text={reference} 
          type="subtitle" 
          color="#FFD700" 
          delay={10}
        />
        <EliteText 
          text={`"${text}"`} 
          type="title" 
          delay={30}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
