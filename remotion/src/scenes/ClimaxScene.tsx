import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import { ImageBackground } from "../components/ImageBackground";
import { EliteText } from "../components/EliteText";

export const ClimaxScene: React.FC<{ 
  text: string; 
  visualMeta?: string; 
  imageSrc?: string;
}> = ({
  text,
  imageSrc,
}) => {
  const frame = useCurrentFrame();
  const zoom = interpolate(frame, [0, 150], [1, 1.1]);

  return (
    <AbsoluteFill>
      <ImageBackground src={imageSrc} />
      
      <AbsoluteFill style={{ 
        justifyContent: "center", 
        alignItems: "center",
        transform: `scale(${zoom})` 
      }}>
        <EliteText text={text} type="title" color="#FFD700" delay={20} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
