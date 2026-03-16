import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import { ImageBackground } from "../components/ImageBackground";
import { EliteText } from "../components/EliteText";

export const SimpleMessageScene: React.FC<{
  text: string;
  subtext?: string;
  visualMeta?: string;
  imageSrc?: string;
}> = ({ text, subtext, imageSrc }) => {
  const frame = useCurrentFrame();
  const parallax = interpolate(frame, [0, 120], [0, -25]);

  return (
    <AbsoluteFill>
      <ImageBackground src={imageSrc} />
      
      <AbsoluteFill style={{ 
        justifyContent: "center", 
        alignItems: "center", 
        flexDirection: "column",
        gap: "20px",
        transform: `translateY(${parallax}px)`
      }}>
        <EliteText text={text} type="title" delay={10} />
        {subtext && (
          <EliteText 
            text={subtext} 
            type="subtitle" 
            color="rgba(255,255,255,0.7)" 
            delay={35}
          />
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
