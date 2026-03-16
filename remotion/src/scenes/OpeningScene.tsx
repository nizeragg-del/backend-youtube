import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import { ImageBackground } from "../components/ImageBackground";
import { EliteText } from "../components/EliteText";
import { MotionEasings } from "../utils/motion";

export const OpeningScene: React.FC<{ 
  text: string; 
  visualMeta?: string; 
  imageSrc?: string;
}> = ({
  text,
  imageSrc,
}) => {
  const frame = useCurrentFrame();
  
  // Parallax: O Texto se move levemente mais rápido que o fundo
  const parallax = interpolate(frame, [0, 150], [0, -40], { easing: MotionEasings.slowSlow });

  return (
    <AbsoluteFill>
      <ImageBackground src={imageSrc} />
      
      <AbsoluteFill style={{ 
        justifyContent: "center", 
        alignItems: "center",
        transform: `translateY(${parallax}px)` 
      }}>
        <EliteText text={text} type="title" delay={15} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
